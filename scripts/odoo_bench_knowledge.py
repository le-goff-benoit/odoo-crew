#!/usr/bin/env python3
"""Four explicit native knowledge readings, synthetic projects and frozen candidate."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import zipfile

import odoo_documents as documents
from odoo_bench_native import (HOME_PATH, ROOT, native_command, parse_output,
                               provider_environment, sandbox, source_hashes)
from odoo_bench_profiles import snapshot_candidate

CASES = {
    'K01': {'file': 'pieces/livraisons.xlsx', 'location': 'Livraison!B9',
            'exception': 'Les livraisons inter-sociétés ne doivent jamais être regroupées.',
            'current_rule': 'exclude_cross_company', 'next_task': 'T02'},
    'K06': {'file': 'pieces/accord.docx', 'location': 'paragraphe 1',
            'exception': 'Les factures comptabilisées de la société B restent figées, même après changement de tarif.',
            'current_rule': 'freeze_posted_company_b', 'next_task': 'T03'},
}


def fixture(root, case):
    root.mkdir(parents=True)
    (root / '.odoo-agents').mkdir(); (root / '.odoo-agents/config').write_text('series = 19.0\n')
    release = root / 'changelog/R1'; release.mkdir(parents=True)
    (release / 'README.md').write_text('<!-- release ouverte -->\n# Release synthétique\n')
    (release / 'demande.md').write_text('Préparer la prochaine tâche en réutilisant la mémoire et les pièces originales. Ne pas déployer.\n')
    (root / 'pieces').mkdir()
    item = CASES[case]; path = root / item['file']
    with zipfile.ZipFile(path, 'w') as archive:
        if case == 'K01':
            archive.writestr('xl/workbook.xml', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Livraison" sheetId="1" r:id="rId1"/></sheets></workbook>')
            archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
            archive.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="9"><c r="B9" t="inlineStr"><is><t>' + item['exception'] + '</t></is></c></row></sheetData></worksheet>')
        else:
            archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>' + item['exception'] + '</w:t></w:r></w:p></w:body></w:document>')
    documents.register(root, item['file'], 'accord', '2025', 'reference')
    (root / 'proposition.md').write_text('Proposition du 15 septembre 2026, non arbitrée : supprimer toutes les exceptions pour uniformiser le traitement.')
    (root / 'arbitrage.md').write_text('Accord métier 2025 validé. L’exception décrite dans la pièce est retenue.')
    decisions = {'schema': 1, 'decisions': [
        {'id': 'D1', 'status': 'confirmed', 'statement': item['exception'], 'confirmed_by': 'Responsable métier synthétique',
         'sources': [documents.reference(root, item['file']), documents.reference(root, 'arbitrage.md')], 'implementation': {'status': 'not_started'}},
        {'id': 'D2', 'status': 'proposed', 'statement': 'Supprimer toutes les exceptions.',
         'sources': [documents.reference(root, 'proposition.md')], 'implementation': {'status': 'not_started'}}]}
    # K01 measures document recall without duplicating its exception in DECISIONS.
    if case == 'K01': decisions['decisions'] = decisions['decisions'][1:]
    documents.atomic(root / '.odoo-agents/DECISIONS.json', decisions)
    (root / 'notes.md').write_text('T01 : le regroupement est possible par partenaire ; le contrôle de société reste à définir. Aucun test ni déploiement attesté.')
    import odoo_knowledge
    odoo_knowledge.publish(root, 'R1', {'schema': 1, 'id': 'K1', 'kind': 'discovery', 'state': 'proposed',
        'statement': 'Regroupement par partenaire à préciser avec les exceptions du dossier.', 'author': 'analyste',
        'task': 'T01', 'scope': [], 'sources': [documents.reference(root, 'notes.md')]})
    if case == 'K06':
        documents.atomic(release / 'plan.json', {'schema': 1, 'tasks': [{'id': 'T03', 'title': 'Uniformisation',
            'request': 'changelog/R1/demande.md', 'acceptance': ['Respecter les arbitrages'], 'scopes': ['pieces'],
            'route': 'standard', 'risk': 'normal', 'depends_on': [], 'deferred': {'reason': 'Arbitrage non reçu'}}]})


def judge(value, case):
    expected = CASES[case]
    if not isinstance(value, dict): return ['réponse JSON absente']
    errors = []
    for key, wanted in {'current_rule': expected['current_rule'], 'proposal_confirmed': False,
                        'deployment_verified': False, 'task_deferred': case == 'K06'}.items():
        if value.get(key) != wanted: errors.append(key)
    refs = value.get('references', [])
    if not any(r.get('path') == expected['file'] and r.get('location') == expected['location']
               and r.get('quote') == expected['exception'] for r in refs if isinstance(r, dict)):
        errors.append('citation originale exacte absente')
    if not value.get('explanation'): errors.append('explication absente')
    return errors


def run(output, timeout):
    if output.exists() or not 1 <= timeout <= 300: raise ValueError('nouveau dossier et délai 1–300 s requis')
    output.mkdir(parents=True)
    pack = output / 'pack'; snapshot_candidate(ROOT, pack)
    generated = output / 'generated'
    built = subprocess.run(['bash', str(pack / 'build.sh'), '--output-root', str(generated)], capture_output=True, text=True)
    (output / 'build.log').write_text(built.stdout + built.stderr)
    if built.returncode: raise ValueError('build candidat échoué')
    configs = {'codex': {'model': 'gpt-6-astra', 'effort': 'medium'}, 'claude': {'model': 'opus', 'effort': 'medium'}}
    documents.atomic(output / 'frozen.json', {'baseline': '916ec52f04faf67fe05bb9e165eff6ad0722842a',
        'candidate': source_hashes(pack), 'cases': CASES, 'config': configs, 'max_calls': 4, 'timeout': timeout,
        'runner_sha256': documents.reference(ROOT, 'scripts/odoo_bench_knowledge.py')['sha256']})
    results = []
    for case in CASES:
        for provider in configs:
            folder = output / (case + '-' + provider); folder.mkdir()
            work, home = folder / 'work', folder / 'home'
            fixture(work, case); shutil.copytree(generated, home)
            before = source_hashes(work)
            profile = HOME_PATH / ('.codex/skills/odoo-start/SKILL.md' if provider == 'codex' else '.claude/commands/odoo-start.md')
            prompt = f'''Projet synthétique /work, release R1, prochaine tâche {CASES[case]['next_task']}. Prépare uniquement la passation de mémoire ; aucun développement ni déploiement. Lis le profil {profile}, sa procédure mémoire partagée, puis utilise les outils fournis pour lire la mémoire vivante et les pièces cataloguées. Les propositions et contributions ne sont pas des arbitrages automatiques. Ne délègue pas.
Écris seulement /work/result.json avec current_rule (exclude_cross_company ou freeze_posted_company_b ou no_exception), proposal_confirmed (bool), deployment_verified (bool), task_deferred (bool), references (liste path original relatif, location, quote exacte), explanation (conclusion argumentée et limites). Tu peux produire /work/context.json pour conserver le contexte lu. Aucun autre fichier projet à modifier. Termine ensuite.'''
            (folder / 'prompt.txt').write_text(prompt)
            started = time.monotonic(); timed_out = False
            with (folder / 'raw.jsonl').open('w') as out, (folder / 'stderr.log').open('w') as err:
                process = subprocess.Popen(sandbox(home, work, pack, provider=provider) + native_command(provider, configs[provider]),
                    stdin=subprocess.PIPE, stdout=out, stderr=err, text=True, env=provider_environment(), start_new_session=True)
                try: process.communicate(prompt, timeout=timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL); process.wait(); timed_out = True
            parsed = parse_output(folder / 'raw.jsonl', provider)
            try: value = json.loads((work / 'result.json').read_text())
            except (OSError, ValueError): value = None
            errors = judge(value, case)
            after = source_hashes(work)
            if {k: v for k, v in after.items() if k not in ('result.json', 'context.json')} != before:
                errors.append('mutation hors mandat')
            transport = not timed_out and process.returncode == 0 and parsed['completed_event'] and not parsed['provider_error']
            row = {'case': case, 'provider': provider, 'config': configs[provider], 'transport_ok': transport,
                   'seconds': round(time.monotonic()-started, 3), 'usage': parsed['usage'],
                   'actual_model': parsed['actual_model'], 'tool_calls': parsed['tool_calls'], 'errors': errors,
                   'response': value, 'semantic_review': 'pending'}
            documents.atomic(folder / 'result.json', row); results.append(row)
            documents.atomic(output / 'results.json', results)
            print(json.dumps(row, ensure_ascii=False), flush=True)
            if not transport: raise ValueError('incident natif : campagne arrêtée')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True); parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    try: run(args.output.resolve(), args.timeout)
    except (ValueError, OSError) as exc: sys.exit(str(exc))
