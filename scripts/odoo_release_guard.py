#!/usr/bin/env python3
"""Préparer la version avant recette et sceller une clôture sur ses preuves réelles."""
import argparse
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

from odoo_evidence import fingerprint, verify
from odoo_flow import graph_hash, now, write_state
from odoo_plan import location, read, statuses

def artifact_hash(path):
    text = path.read_text()
    if path.name == 'README.md':
        text = re.sub(r'(?m)^<!-- (?:release|lot) ouverte? -->\n?', '', text)
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


REQUIRED = ('README.md', 'demande.md', 'doc.md', 'recette.md', 'tests_navigateur.md', 'consolidation.md', 'controls.json')


def required_artifacts(release):
    from odoo_effort import REPORT_FILES, check_report, preparation_entries
    has_effort = (release / 'effort.json').exists()
    if has_effort or preparation_entries(release.resolve().parent.parent, release.name):
        check_report(release)
        return REQUIRED + (('effort.json',) if has_effort else ()) + REPORT_FILES
    return REQUIRED


def prepare(module):
    path = Path(module).resolve() / '__manifest__.py'
    source = path.read_text()
    tree = ast.parse(source)
    data = ast.literal_eval(tree.body[0].value)
    version = data['version']
    if not re.fullmatch(r'\d+(?:\.\d+){3,}', version):
        raise ValueError('version non numérique : choisir explicitement une version avant recette')
    # L'action est idempotente pour une release : le rôle appelle prepare une seule fois.
    value = next(v for k, v in zip(tree.body[0].value.keys, tree.body[0].value.values) if isinstance(k, ast.Constant) and k.value == 'version')
    parts = version.split('.'); parts[-1] = str(int(parts[-1]) + 1); target = '.'.join(parts)
    lines = source.splitlines(keepends=True)
    start = sum(len(x.encode()) for x in lines[:value.lineno - 1]) + value.col_offset
    end = sum(len(x.encode()) for x in lines[:value.end_lineno - 1]) + value.end_col_offset
    raw = source.encode(); path.write_bytes(raw[:start] + repr(target).encode() + raw[end:])
    return version, target


def prepare_release(release, modules):
    release, project = location(release)
    marker = release / 'versions.json'
    versions = json.loads(marker.read_text()) if marker.exists() else {}
    for relative in modules:
        module = (project / relative).resolve()
        if not module.is_relative_to(project):
            raise ValueError('module hors projet')
        current = ast.literal_eval((module / '__manifest__.py').read_text())['version']
        if relative in versions:
            if current != versions[relative]['target']:
                raise ValueError('version changée après préparation : ' + relative)
            continue
        # Ne pas incrémenter une seconde fois un manifest déjà préparé par le projet.
        base = (release / '.base').read_text().strip() if (release / '.base').exists() else ''
        old = subprocess.run(['git', 'show', base + ':' + relative + '/__manifest__.py'], cwd=project, capture_output=True, text=True)
        previous = ast.literal_eval(old.stdout).get('version') if old.returncode == 0 else current
        before, target = prepare(module) if current == previous else (previous, current)
        versions[relative] = {'base': before, 'target': target, 'prepared_at': now()}
        write_state(marker, versions)
    return versions


def controls(release, project, evidence_by_path):
    data = json.loads((release / 'controls.json').read_text())
    if data.get('schema') != 1 or data.get('risk') not in ('normal', 'high') or data.get('route') not in ('module', 'studio', 'mixed', 'standard'):
        raise ValueError('contrôles : schema, risque et voie explicites requis')
    rows = data.get('controls', [])
    ids = [r['id'] for r in rows]
    required = {'installation', 'update', 'tests', 'client_copy', 'browser', 'uninstall'}
    if len(ids) != len(set(ids)) or not required <= set(ids):
        raise ValueError('contrôles obligatoires absents ou dupliqués')
    for row in rows:
        status = row.get('status')
        if status == 'passed':
            proof = row.get('proof')
            if proof not in evidence_by_path:
                raise ValueError('contrôle sans preuve vérifiée : ' + row['id'])
            if row['id'] == 'tests' and data['route'] in ('module', 'mixed') and not evidence_by_path[proof].get('module'):
                raise ValueError('tests Odoo sans preuve de tests du module')
        elif status == 'not_applicable' and row.get('reason') and (row['id'] == 'browser' or (data['route'] in ('studio', 'standard') and row['id'] in ('installation', 'update', 'uninstall'))):
            pass
        elif status == 'waived' and row['id'] == 'client_copy' and data['risk'] == 'normal' and row.get('reason'):
            pass
        else:
            raise ValueError('contrôle obligatoire incomplet ou dispense invalide : ' + row['id'])
    if (release / 'plan.json').exists():
        plan, _ = read(release)
        routes = {t['route'] for t in plan['tasks'] if not t.get('deferred')}
        expected_route = 'mixed' if 'module' in routes and 'studio' in routes else ('module' if 'module' in routes else ('studio' if 'studio' in routes else 'standard'))
        if data['route'] != expected_route:
            raise ValueError('voie de contrôle différente de celle du plan')
        if any(t['risk'] == 'high' and not t.get('deferred') for t in plan['tasks']) and data['risk'] != 'high':
            raise ValueError('le plan impose le risque élevé')
    return data


def seal(release, scopes, proofs):
    release, project = location(release)
    # Only new seals enforce this: do not invalidate historical closures.
    from odoo_effort import check_closure
    check_closure(release)
    if (release / 'plan.json').exists():
        plan, _ = read(release)
        bad = {key: value for key, value in statuses(plan, project).items() if value[0] not in ('validated', 'deferred')}
        if bad:
            raise ValueError('tâches non réceptionnées : ' + ', '.join(bad))
    artifacts = {}
    for name in required_artifacts(release):
        path = release / name
        if not path.is_file() or not path.read_text().strip():
            raise ValueError('livrable obligatoire absent/vide : ' + name)
        artifacts[name] = artifact_hash(path)
    if not proofs:
        raise ValueError('au moins une preuve d’exécution requise')
    covered = {}; receipts = []; evidence_by_path = {}
    for name in proofs:
        path = (project / name).resolve()
        if not path.is_relative_to(project):
            raise ValueError('preuve hors projet')
        evidence = json.loads(path.read_text()); verify(evidence, expected_project=project)
        covered.update(evidence['sources'])
        evidence_by_path[str(path.relative_to(project))] = evidence
        receipts.append({'path': str(path.relative_to(project)), 'sha256': graph_hash(path)})
    controls(release, project, evidence_by_path)
    sources = fingerprint(project, scopes)
    if any(Path(name).name == '__manifest__.py' for name in sources) and controls(release, project, evidence_by_path)['route'] not in ('module', 'mixed'):
        raise ValueError('module livré sous une voie non module')
    if (release / 'plan.json').exists():
        plan, _ = read(release)
        for task in plan['tasks']:
            if not task.get('deferred') and not fingerprint(project, task['scopes']).keys() <= sources.keys():
                raise ValueError('périmètre de clôture incomplet pour ' + task['id'])
    if not sources.keys() <= covered.keys():
        raise ValueError('périmètre livré non couvert par les preuves')
    result = {'format': 'odoo-release/1', 'at': now(), 'project': str(project), 'release': str(release), 'plan_sha256': graph_hash(release / 'plan.json') if (release / 'plan.json').exists() else None, 'scopes': scopes,
              'sources': sources, 'artifacts': artifacts, 'proofs': receipts,
              'limitation': 'La structure et la fraîcheur sont contrôlées ; la pertinence métier est relue par le responsable de clôture.'}
    write_state(release / 'closure.json', result)
    return result


def check(release):
    release, project = location(release)
    record = json.loads((release / 'closure.json').read_text())
    if record.get('format') != 'odoo-release/1' or record['project'] != str(project) or record.get('release') != str(release):
        raise ValueError('sceau d’une autre release/projet ou format invalide')
    current_plan = graph_hash(release / 'plan.json') if (release / 'plan.json').exists() else None
    if record.get('plan_sha256') != current_plan:
        raise ValueError('plan ajouté, supprimé ou changé après scellement')
    if fingerprint(project, record['scopes']) != record['sources']:
        raise ValueError('code changé après recette')
    if set(record['artifacts']) != set(required_artifacts(release)):
        raise ValueError('liste documentaire incomplète')
    for name, sha in record['artifacts'].items():
        if artifact_hash(release / name) != sha:
            raise ValueError('document changé après contrôle : ' + name)
    evidence_by_path = {}
    for proof in record['proofs']:
        path = (project / proof['path']).resolve()
        if not path.is_relative_to(project) or graph_hash(path) != proof['sha256']:
            raise ValueError('preuve changée')
        evidence_by_path[proof['path']] = json.loads(path.read_text())
        verify(evidence_by_path[proof['path']], expected_project=project)
    controls(release, project, evidence_by_path)
    if (release / 'plan.json').exists():
        plan, _ = read(release)
        if any(state[0] not in ('validated', 'deferred') for state in statuses(plan, project).values()):
            raise ValueError('plan non réceptionné')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'seal', 'check'])
    parser.add_argument('release', type=Path)
    parser.add_argument('--module', action='append', default=[])
    parser.add_argument('--scope', action='append', default=[])
    parser.add_argument('--proof', action='append', default=[])
    args = parser.parse_args()
    if args.action == 'prepare':
        print(json.dumps(prepare_release(args.release, args.module), ensure_ascii=False))
    elif args.action == 'seal':
        seal(args.release, args.scope, args.proof); print('Clôture scellée sur les preuves et documents courants.')
    else:
        check(args.release); print('Clôture : preuves, code et documents conformes.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        sys.exit(str(exc))
