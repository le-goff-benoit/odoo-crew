#!/usr/bin/env python3
"""Plan de release versionné ; le graphe reste l'autorité des étapes d'exécution."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import uuid

import odoo_flow as flow
from odoo_evidence import fingerprint, verify

ROOT = Path(__file__).resolve().parents[1]


def location(release):
    release = Path(release).resolve()
    if release.parent.name != 'changelog' or not (release / 'README.md').is_file():
        raise ValueError('dossier changelog/<release> requis')
    return release, release.parent.parent


def reference(project, name, *, directory=False):
    path = (project / name).resolve()
    if not path.is_relative_to(project) or (not path.is_dir() if directory else not path.is_file()):
        raise ValueError('référence absente ou hors projet : ' + name)
    return path


def validate(plan, project):
    if plan.get('schema') not in (1, 2) or not isinstance(plan.get('tasks'), list) or not plan['tasks']:
        raise ValueError('plan schema 1 ou 2 avec tâches requis')
    if plan['schema'] == 2:
        author = plan.get('author', {})
        if author.get('role') != 'orchestrator' or author.get('provider') not in ('codex', 'claude') or not author.get('model') or not isinstance(plan.get('decisions'), list):
            raise ValueError('auteur orchestrateur, modèle principal et décisions explicites requis')
    ids = [t.get('id') for t in plan['tasks']]
    if any(not isinstance(i, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,40}', i) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('identifiants uniques et stables requis')
    by_id = {t['id']: t for t in plan['tasks']}
    for task in plan['tasks']:
        for field in ('title', 'request', 'acceptance', 'scopes', 'risk', 'route'):
            if not task.get(field):
                raise ValueError(task['id'] + ' : ' + field + ' manquant')
        if task['route'] not in ('module', 'studio', 'standard') or task['risk'] not in ('normal', 'high'):
            raise ValueError('voie ou risque invalide')
        if not isinstance(task['acceptance'], list) or any(not isinstance(x, str) or not x.strip() for x in task['acceptance']):
            raise ValueError('critères explicites requis')
        reference(project, task['request'])
        if task.get('request_excerpt') is not None:
            excerpt = task['request_excerpt']
            if not isinstance(excerpt, str) or not excerpt.strip():
                raise ValueError('extrait source exact et unique requis')
        if task.get('check_scopes') and not task.get('selection_reason'):
            raise ValueError('sélection de contrôles bornée : motif d’impact requis')
        if task['risk'] == 'high' and task.get('check_scopes', task['scopes']) != task['scopes']:
            raise ValueError('risque élevé : périmètre complet requis')
        if plan['schema'] == 2:
            if not task.get('intentions') and not task.get('technical_reason'):
                raise ValueError(task['id'] + ' : intentions ou prérequis technique motivé requis')
            checks = task.get('checks', [])
            if not checks or any(not all(c.get(k) for k in ('id', 'command', 'environment', 'cases')) for c in checks):
                raise ValueError(task['id'] + ' : contrôles, commandes, environnement et cas requis')
            check_ids = [c['id'] for c in checks]
            if len(set(check_ids)) != len(check_ids) or any(not isinstance(c['command'], list) or not all(isinstance(v, str) for v in c['command']) or not isinstance(c['environment'], str) for c in checks):
                raise ValueError('identifiants de contrôle uniques, argv et environnement explicites requis')
            execution = task.get('execution', {})
            if not all(execution.get(k) for k in ('provider', 'model', 'effort')):
                raise ValueError(task['id'] + ' : fournisseur, modèle et effort requis')
            if not isinstance(task.get('reads'), list) or not isinstance(task.get('writes'), list):
                raise ValueError(task['id'] + ' : entrées et écritures explicites requises')
            if task.get('intentions'):
                import odoo_intentions
                register = odoo_intentions.read(reference(project, plan['intentions_file']))
                items = {i['id']: i for i in register['items']}
                for identifier in task['intentions']:
                    if identifier not in items:
                        raise ValueError('intention absente, différée ou question bloquante : ' + identifier)
        for scope in task['scopes'] + task.get('check_scopes', []) + task.get('reads', []) + task.get('writes', []):
            # Un futur module peut ne pas encore exister ; son parent doit rester dans le projet.
            if Path(scope).is_absolute() or not (project / scope).resolve().is_relative_to(project) or scope in ('.', ''):
                raise ValueError('périmètre relatif borné requis')
        for dep in task.get('depends_on', []):
            if dep not in by_id or dep == task['id']:
                raise ValueError('dépendance inconnue ou réflexive')
    def visit(identifier, seen):
        if identifier in seen:
            raise ValueError('cycle dans les dépendances')
        for dep in by_id[identifier].get('depends_on', []):
            visit(dep, seen | {identifier})
    for identifier in ids:
        visit(identifier, set())


def read(release):
    release, project = location(release)
    plan = json.loads((release / 'plan.json').read_text())
    validate(plan, project)
    return plan, project


def contract_hash(task, project):
    contract = {key: task.get(key) for key in ('id', 'title', 'request', 'acceptance', 'scopes', 'risk', 'route', 'depends_on')}
    # An exact source excerpt isolates additions to another intention in a shared request.
    excerpt = task.get('request_excerpt')
    if excerpt is not None:
        if reference(project, task['request']).read_text().count(excerpt) != 1:
            raise ValueError('extrait source modifié ou ambigu')
        contract['request_excerpt'] = excerpt
    else:
        contract['request_sha256'] = flow.graph_hash(reference(project, task['request']))
    if task.get('intentions_file'):
        import odoo_intentions
        register = odoo_intentions.read(reference(project, task['intentions_file']))
        contract['intention_contracts'] = [{k: item.get(k) for k in ('id', 'text', 'purpose', 'constraints', 'decisions', 'questions', 'criteria', 'source')} for item in register['items'] if item['id'] in task.get('intentions', [])]
    for key in ('intentions', 'technical_reason', 'checks', 'reads', 'writes', 'execution', 'check_scopes', 'outputs'):
        if key in task:
            contract[key] = task[key]
    import hashlib
    return hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()


def task_status(task, project):
    if task.get('deferred'):
        return 'deferred', task['deferred']['reason']
    receipt = task.get('receipt')
    if receipt:
        try:
            if receipt.get('contract_sha256') != contract_hash(task, project):
                raise ValueError('contrat de tâche changé après réception')
            for item in (receipt['acceptance'], receipt['memory']):
                path = reference(project, item['path'])
                if flow.graph_hash(path) != item['sha256']:
                    raise ValueError('passation modifiée après validation')
            proof_path = reference(project, receipt['proof']['path'])
            if flow.graph_hash(proof_path) != receipt['proof']['sha256']:
                raise ValueError('preuve remplacée')
            primary_evidence = json.loads(proof_path.read_text())
            verify(primary_evidence, expected_project=project)
            covered_sources = set(primary_evidence['sources'])
            if task.get('checks'):
                recorded_checks = receipt.get('checks', {})
                if set(recorded_checks) != {c['id'] for c in task['checks']}:
                    raise ValueError('contrôles prescrits non réceptionnés')
                for check in task['checks']:
                    item = recorded_checks[check['id']]
                    checked_path = reference(project, item['path'])
                    if flow.graph_hash(checked_path) != item['sha256']:
                        raise ValueError('preuve de contrôle remplacée')
                    checked = json.loads(checked_path.read_text())
                    verify(checked, project, expected_environment=check['environment'])
                    if checked.get('command') != check['command']:
                        raise ValueError('commande différente du contrôle prescrit')
                    covered_sources.update(checked['sources'])
                required = fingerprint(project, task.get('check_scopes', task['scopes']) + task.get('reads', []))
                if not set(required) <= covered_sources:
                    raise ValueError('périmètre courant non couvert par les contrôles prescrits')
            return 'validated', 'preuve et passation toujours valides'
        except (OSError, ValueError, KeyError) as exc:
            return 'stale', str(exc)
    attempts = task.get('attempts', [])
    if not attempts:
        return 'pending', ''
    try:
        state = json.loads(reference(project, attempts[-1]['flow']).read_text())
    except (OSError, ValueError):
        return 'interrupted', 'état local absent : réception durable non validée ; réconcilier explicitement'
    if state['status'] == 'complete':
        return 'awaiting_receipt', 'graphe terminé ; preuve et consolidation attendues'
    if state['status'] in ('blocked', 'cancelled'):
        return 'blocked', state['status']
    return 'running', attempts[-1]['flow']


def receipt_hash(receipt):
    import hashlib
    return hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()


def result_hash(receipt):
    # Old receipts keep their conservative whole-receipt dependency semantics.
    return receipt.get('result_sha256') if receipt and receipt.get('result_sha256') else receipt_hash(receipt)



def statuses(plan, project):
    states = {task['id']: task_status(task, project) for task in plan['tasks']}
    by_id = {task['id']: task for task in plan['tasks']}
    for task in plan['tasks']:
        if states[task['id']][0] == 'validated':
            expected = task['receipt'].get('dependencies', {})
            current = {d: (result_hash if task['receipt'].get('dependency_version') == 2 else receipt_hash)(by_id[d].get('receipt')) for d in task.get('depends_on', [])}
            if expected != current:
                states[task['id']] = ('stale', 'réception d’une dépendance changée : nouvelle validation requise')
    # Propager les preuves périmées aux tâches qui en dépendaient.
    for _ in plan['tasks']:
        for task in plan['tasks']:
            deps = task.get('depends_on', [])
            bad = [d for d in deps if states[d][0] != 'validated']
            if bad and states[task['id']][0] == 'validated':
                states[task['id']] = ('stale', 'dépendances non validées : ' + ', '.join(bad))
    return states


def overlapping(first, second, project):
    return any((project / a).resolve().is_relative_to((project / b).resolve()) or
               (project / b).resolve().is_relative_to((project / a).resolve())
               for a in first for b in second)


def available(plan, project, identifier):
    states = statuses(plan, project)
    task = next(t for t in plan['tasks'] if t['id'] == identifier)
    if task.get('intentions_file'):
        import odoo_intentions
        items = {i['id']: i for i in odoo_intentions.read(reference(project, task['intentions_file']))['items']}
        if any(items[i]['questions'] or items[i]['status'] in ('clarify', 'deferred') for i in task.get('intentions', [])):
            return False, 'intention à clarifier ou différée'
    if states[identifier][0] != 'pending':
        return False, states[identifier][1] or states[identifier][0]
    deps = [d for d in task.get('depends_on', []) if states[d][0] != 'validated']
    if deps:
        return False, 'dépendances : ' + ', '.join(deps)
    for other in plan['tasks']:
        if other['id'] != identifier and states[other['id']][0] in ('running', 'awaiting_receipt', 'interrupted'):
            if overlapping(task['scopes'], other['scopes'], project):
                from odoo_candidate import isolated, active_for_task
                candidate = (other.get('attempts') or [{}])[-1].get('candidate')
                if candidate and active_for_task(other, project) and isolated(candidate, task):
                    continue
                return False, 'périmètre réservé par ' + other['id']
    return True, 'revendicable'


def save(release, plan):
    flow.write_state(release / 'plan.json', plan)


def initialise(release, definition):
    release, project = location(release)
    definition = deepcopy(definition)
    if definition.get('schema') == 2:
        for task in definition['tasks']:
            task['intentions_file'] = definition.get('intentions_file')
    validate(definition, project)
    plan = deepcopy(definition)
    if any(set(t) & {'receipt', 'attempts', 'deferred'} for t in plan['tasks']):
        raise ValueError('une définition ne peut importer un état validé')
    with flow.exclusive_lock(release / 'plan.json'):
        if (release / 'plan.json').exists():
            raise ValueError('plan existant : ne pas écraser son historique')
        for task in plan['tasks']:
            contract_hash(task, project)
        plan['history'] = [{'at': flow.now(), 'action': 'prepared'}]
        save(release, plan)


def append_tasks(release, definition):
    release, project = location(release)
    tasks = deepcopy(definition.get('tasks', []))
    if definition.get('schema') not in (1, 2) or not tasks:
        raise ValueError('ajout schema 1 avec tâches requis')
    if any(set(t) & {'receipt', 'attempts', 'deferred'} for t in tasks):
        raise ValueError('une définition ne peut importer un état validé')
    with flow.exclusive_lock(release / 'plan.json'):
        plan, project = read(release)
        if plan['schema'] == 2:
            for task in tasks:
                task['intentions_file'] = plan.get('intentions_file')
        plan['tasks'].extend(tasks)
        validate(plan, project)
        plan['history'].append({'at': flow.now(), 'action': 'added', 'tasks': [t['id'] for t in tasks]})
        save(release, plan)


def revise_tasks(release, definition, reason):
    if not reason:
        raise ValueError('source et motif de révision requis')
    release, project = location(release)
    with flow.exclusive_lock(release / 'plan.json'):
        plan, _ = read(release)
        for replacement in definition.get('tasks', []):
            task = next((t for t in plan['tasks'] if t['id'] == replacement.get('id')), None)
            if not task or set(replacement) & {'receipt', 'attempts', 'deferred'}:
                raise ValueError('révision d’un contrat existant sans état importé requise')
            if task_status(task, project)[0] in ('running', 'awaiting_receipt'):
                raise ValueError('terminer ou interrompre le flow avant de réviser')
            plan['history'].append({'at': flow.now(), 'action': 'contract_revised', 'reason': reason, 'task': deepcopy(task)})
            task.update(deepcopy(replacement))
        validate(plan, project)
        changed_ids = {t['id'] for t in definition.get('tasks', [])}
        for task in plan['tasks']:
            if task['id'] in changed_ids:
                contract_hash(task, project)
        save(release, plan)


def source_snapshot(project, scopes):
    return fingerprint(project, [s for s in scopes if (project / s).exists()], allow_empty=True)


def mutate(release, action, identifier, *, proof=None, acceptance=None, memory=None, reason=None, check_proofs=None):
    release, project = location(release)
    with flow.exclusive_lock(release / 'plan.json'):
        plan, project = read(release)
        task = next((t for t in plan['tasks'] if t['id'] == identifier), None)
        if task is None:
            raise ValueError('tâche inconnue')
        state, _ = task_status(task, project)
        if action == 'start':
            ready, why = available(plan, project, identifier)
            if not ready:
                raise ValueError(why)
            before = source_snapshot(project, task['scopes'])
            run_id = 'plan-' + identifier.lower() + '-' + uuid.uuid4().hex[:8]
            flow.ensure_local_flow_dirs(project)
            path = project / '.odoo-agents/flows' / (run_id + '.json')
            graph = ROOT / 'workflows/odoo-workflow.json'
            current = flow.new_state(project, 'development', run_id, graph)
            if task.get('resources'):
                from odoo_candidate import resources
                physical = resources(task['resources'])
                if not current.get('resource_registry'):
                    raise ValueError('ressources physiques : déclarer le registre partagé dans .odoo-agents/resources.json')
                current['execution_resources'] = physical
                code_root = project / task['scopes'][0] if len(task['scopes']) == 1 else project
                current.setdefault('resource_bindings', {}).update({'module_code': {'id': 'path:' + str(code_root.resolve())}, 'qa_db_module': {'id': physical['database']}})
            # Le graphe gère les verrous courts ; le plan réserve les périmètres de toute la tâche.
            current['plan_task'] = {'release': str(release), 'id': identifier, 'risk': task['risk']}
            flow.write_state(path, current)
            task.setdefault('attempts', []).append({'flow': str(path.relative_to(project)),
                                                   'at': flow.now(), 'sources_before': before})
            result = str(path)
        elif action == 'finish':
            attempts = task.get('attempts', [])
            if not attempts or json.loads(reference(project, attempts[-1]['flow']).read_text())['status'] != 'complete':
                raise ValueError('le graphe doit être terminé avant la réception')
            current_states = statuses(plan, project)
            if any(current_states[d][0] != 'validated' for d in task.get('depends_on', [])):
                raise ValueError('dépendances à réceptionner avant cette tâche')
            recorded_checks, check_results = {}, {}
            check_proofs = check_proofs or {}
            if task.get('checks'):
                checks = task['checks']
                if len(checks) == 1 and not check_proofs and proof:
                    check_proofs = {checks[0]['id']: proof}
                if set(check_proofs) != {c['id'] for c in checks}:
                    raise ValueError('une preuve pour chaque contrôle prescrit est requise')
                for check in checks:
                    checked_path = reference(project, check_proofs[check['id']])
                    checked = json.loads(checked_path.read_text())
                    verify(checked, project, expected_environment=check['environment'])
                    if checked.get('command') != check['command']:
                        raise ValueError('commande différente du contrôle prescrit : ' + check['id'])
                    recorded_checks[check['id']] = {'path': str(checked_path.relative_to(project)), 'sha256': flow.graph_hash(checked_path)}
                    check_results[check['id']] = {'sources': checked['sources'], 'command': checked['command'], 'environment': checked['environment']}
                if proof is None:
                    proof = check_proofs[checks[0]['id']]
                if proof not in check_proofs.values():
                    raise ValueError('preuve principale étrangère aux contrôles prescrits')
            proof_path = reference(project, proof or '')
            evidence = json.loads(proof_path.read_text())
            verify(evidence, expected_project=project)
            # Une preuve sur un fichier sans lien ne valide pas le périmètre de la tâche.
            required = fingerprint(project, task.get('check_scopes', task['scopes']) + task.get('reads', []))
            covered = set(evidence['sources'])
            for result in check_results.values():
                covered.update(result['sources'])
            if not set(required) <= covered:
                raise ValueError('preuve ne couvrant pas tout le périmètre')
            from odoo_candidate import valid
            candidate = attempts[-1].get('candidate')
            if candidate and not valid(candidate):
                raise ValueError('candidat QA modifié depuis son gel')
            receipt = {}
            for key, value in [('proof', proof), ('acceptance', acceptance), ('memory', memory)]:
                path = reference(project, value or '')
                if not path.read_text().strip():
                    raise ValueError('preuve vide : ' + key)
                receipt[key] = {'path': str(path.relative_to(project)), 'sha256': flow.graph_hash(path)}
            receipt['at'] = flow.now(); receipt['contract_sha256'] = contract_hash(task, project)
            by_id = {t['id']: t for t in plan['tasks']}
            if recorded_checks:
                receipt['checks'] = recorded_checks
            receipt['dependency_version'] = 2
            receipt['dependencies'] = {d: result_hash(by_id[d].get('receipt')) for d in task.get('depends_on', [])}
            # Dates, evidence filenames and measurements are history, not the delivered interface.
            receipt['result_sha256'] = receipt_hash({'contract': receipt['contract_sha256'],
                'sources': evidence['sources'], 'environment': evidence.get('environment'), 'acceptance': receipt['acceptance']['sha256'],
                'memory': receipt['memory']['sha256'], 'dependencies': receipt['dependencies'], 'checks': check_results})
            if task.get('receipt'):
                plan['history'].append({'at': flow.now(), 'action': 'previous_receipt', 'task_id': identifier, 'receipt': deepcopy(task['receipt'])})
            task['receipt'] = receipt
            result = 'validé ; contenu métier de la réception à relire par l’orchestrateur'
        elif action in ('reopen', 'defer'):
            if not reason:
                raise ValueError('décision motivée requise')
            if state in ('running', 'awaiting_receipt'):
                raise ValueError('libérer/terminer le graphe avant de modifier le plan')
            if action == 'defer':
                task['deferred'] = {'reason': reason, 'at': flow.now()}
            else:
                # L'historique contient la réception invalidée ; aucun faux statut conservé.
                plan['history'].append({'at': flow.now(), 'action': 'previous_attempt', 'task': deepcopy(task)})
                for key in ('receipt', 'attempts', 'deferred'):
                    task.pop(key, None)
            result = action
        else:
            raise ValueError('action inconnue')
        plan['history'].append({'at': flow.now(), 'action': action, 'task_id': identifier, 'reason': reason})
        save(release, plan)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'add', 'revise', 'status', 'changed', 'start', 'finish', 'reopen', 'defer'])
    parser.add_argument('release', type=Path)
    parser.add_argument('--file', type=Path)
    parser.add_argument('--check-proofs', type=Path, help='JSON identifiant de contrôle → chemin de preuve relatif')
    parser.add_argument('--task'); parser.add_argument('--proof'); parser.add_argument('--acceptance'); parser.add_argument('--memory'); parser.add_argument('--reason')
    args = parser.parse_args()
    if args.action in ('init', 'add', 'revise'):
        if not args.file:
            parser.error('--file requis')
        if args.action == 'revise':
            revise_tasks(args.release, json.loads(args.file.read_text()), args.reason)
        else:
            (initialise if args.action == 'init' else append_tasks)(args.release, json.loads(args.file.read_text()))
    elif args.action == 'changed':
        plan, project = read(args.release)
        task = next(t for t in plan['tasks'] if t['id'] == args.task)
        before = task['attempts'][-1]['sources_before']
        after = source_snapshot(project, task['scopes'])
        for name in sorted(before.keys() | after.keys()):
            if before.get(name) != after.get(name):
                print(name)
    elif args.action == 'status':
        plan, project = read(args.release); states = statuses(plan, project)
        for task in plan['tasks']:
            ready, why = available(plan, project, task['id'])
            print(f"{task['id']} · {states[task['id']][0]} · {'PRÊT' if ready else why} · {task['title']}")
    else:
        print(mutate(args.release, args.action, args.task, proof=args.proof, acceptance=args.acceptance, memory=args.memory, reason=args.reason, check_proofs=json.loads(args.check_proofs.read_text()) if args.check_proofs else None))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, flow.FlowError) as exc:
        sys.exit(str(exc))
