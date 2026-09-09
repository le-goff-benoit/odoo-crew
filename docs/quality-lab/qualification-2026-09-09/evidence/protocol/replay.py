import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path('/home/blegoff/.odoo19-agents')
sys.path.insert(0, str(ROOT / 'scripts'))
from odoo_bench_native import copy_project, export_revision, sandbox, native_command, execute, provider_environment, source_hashes
from odoo_bench import parse_output
from odoo_flow import new_state, complete_node, ready_nodes

BASE = Path(__file__).resolve().parent
config = json.loads((BASE / 'protocol.json').read_text())
config.update(config['native'])
config['timeout_seconds'] = config['native']['seconds_per_call']
pack = BASE / ('candidate-v2' if sys.argv[1].endswith('v2') else 'candidate' if sys.argv[1].endswith('candidate') else 'reference')
if not pack.exists():
    export_revision(config['reference'], pack)
folder = BASE / sys.argv[1]
folder.mkdir()
home = folder / 'home'; home.mkdir()
work = folder / 'project'
if sys.argv[1].startswith('held-'):
    kind = 't42' if 't42' in sys.argv[1] else 'negative' if 'negative' in sys.argv[1] else 'positive'
    copy_project(BASE / ('held-' + kind + '-input'), work)
    release = next((work / 'changelog').glob('2026-*'))
    flowpath = work / '.odoo-agents/flows/d31-jours-negatifs.json'
    state = new_state(work, 'development', 'd31-jours-negatifs', pack / 'workflows/odoo-workflow.json')
    state['project'] = '/work'
    state['graph'] = '/home/blegoff/.odoo19-agents/workflows/odoo-workflow.json'
    entries = [('briefing', 'development', 'revue_fonctionnelle.md'), ('functional_review', 'module_high_risk', 'revue_fonctionnelle.md'), ('module_implementation_high_risk', 'done', 'static.md'), ('module_high_static_qa', 'done', 'static.md'), ('module_high_runtime_qa', 'done', 'runtime.md'), ('module_client_copy_qa', 'done', 'client.md')]
    for node, outcome, proof in entries:
        complete_node(state, state['graph_snapshot'], node, outcome, ['/work/changelog/' + release.name + '/' + proof], 'Attestation synthétique du dossier T41')
    flowpath.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
else:
    original = ROOT / 'docs/quality-lab/delegation-2026-09-09/evidence/resumed/project'
    copy_project(original, work)
    release = next((work / 'changelog').glob('2026-*'))
    # Retirer les résultats postérieurs à la jointure, jamais les preuves d'entrée.
    for name in ('qa.md',):
        (release / name).unlink(missing_ok=True)
    previous = ROOT / 'docs/quality-lab/delegation-2026-09-09/evidence/interrupted/project'
    for name in ('JOURNAL.md', 'PROJECT.md'):
        shutil.copy2(previous / '.odoo-agents' / name, work / '.odoo-agents' / name)
    for name in ('README.md',):
        src = previous / 'changelog' / release.name / name
        if src.exists(): shutil.copy2(src, release / name)
    flowpath = work / '.odoo-agents/flows/d31-jours-negatifs.json'
    old = json.loads(flowpath.read_text())
    state = new_state(work, 'development', old['run_id'], pack / 'workflows/odoo-workflow.json')
    state['project'] = '/work'
    state['graph'] = '/home/blegoff/.odoo19-agents/workflows/odoo-workflow.json'
    for event in old['events'][:6]:
        complete_node(state, state['graph_snapshot'], event['node'], event['outcome'], event['evidence'], event['note'])
        state['events'][-1] = event
    assert ready_nodes(state, state['graph_snapshot']) == ['module_high_gate']
    flowpath.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
(folder / 'input-hashes.json').write_text(json.dumps(source_hashes(work), indent=2))
built = execute(sandbox(home, work, pack) + ['bash', '/home/blegoff/.odoo19-agents/build.sh'], env=provider_environment())
(folder / 'build.log').write_text(built.stdout); built.check_returncode()
prompt = '''Projet synthétique de laboratoire Odoo 19.0. Reprise en contexte neuf au nœud module_high_gate du flow .odoo-agents/flows/d31-jours-negatifs.json. Les trois voies QA ont terminé ; leurs preuves originales et la revue fonctionnelle sont dans les fichiers. Lis les profils /odoo-new et odoo-tester et les fichiers nécessaires, puis effectue la consolidation et enregistre l'issue réelle dans le flow, avec qa.md comme preuve. Arrête-toi juste après la jointure : ne démarre aucune étape aval, ne modifie ni le code, ni la spécification, ni les fragments QA. Les contrôles exécutés dans les fragments sont les preuves d'entrée de cet exercice, aucune nouvelle base ni exécution Odoo n'est disponible ; ne présente pas leur reprise en fichier comme une exécution nouvelle. Les sources et le dispositif sont en lecture seule ; seul /work est modifiable. Préserve la portée de la demande et laisse la release ouverte. Rends le verdict et ce qui reste à faire.'''
(folder / 'prompt.txt').write_text(prompt)
start = time.monotonic()
with (folder / 'raw.jsonl').open('w') as out, (folder / 'stderr.log').open('w') as err:
    proc = subprocess.Popen(sandbox(home, work, pack, provider='claude') + (native_command('claude', config) + ['--max-budget-usd', str(config['native']['max_budget_usd'])]), stdin=subprocess.PIPE, stdout=out, stderr=err, text=True, env=provider_environment(), start_new_session=True)
    status = 'executed'
    try: proc.communicate(prompt, timeout=config['timeout_seconds'])
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL); proc.wait(); status = 'timeout'
parsed = parse_output(folder / 'raw.jsonl', 'claude')
(folder / 'parsed.json').write_text(json.dumps(parsed, ensure_ascii=False, indent=2))
final = json.loads(flowpath.read_text())
result = {'status': status, 'returncode': proc.returncode, 'seconds': round(time.monotonic()-start,2), 'new_events': final['events'][6:], 'claims': final['claims'], 'output_hashes': source_hashes(work)}
(folder / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({k:v for k,v in result.items() if k != 'output_hashes'}, ensure_ascii=False))
