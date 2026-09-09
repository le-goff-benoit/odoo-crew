import hashlib
import json
from pathlib import Path
import re
import shutil

BASE = Path(__file__).resolve().parent
ROOT = Path('/home/blegoff/.odoo19-agents')
out = ROOT / 'docs/quality-lab/consolidation-2026-09-09/evidence'
out.mkdir(parents=True, exist_ok=True)
def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
for pattern in ('protocol*.json', '*hashes.json', 'replay.py', 'rpc_experiment*.py', 'rpc-red.log', 'rpc-green.log', 'suite.log', 'build-isolated.log', 'parity-isolated.log'):
    for src in BASE.glob(pattern): copy(src, out/src.name)
for name in ('reference', 'candidate', 'candidate-v2'):
    copy(BASE/name/'roles/orchestration.md', out/'variants'/(name+'.md'))
for src in BASE.glob('held-*-input'):
    for p in src.rglob('*'):
        if p.is_file(): copy(p, out/'fixtures'/src.name/p.relative_to(src))
summary=[]
for name in ('known-reference','known-candidate','held-negative-candidate','held-positive-candidate','known-v2','held-t42-v2'):
    folder=BASE/name
    result=json.loads((folder/'result.json').read_text())
    parsed=json.loads((folder/'parsed.json').read_text())
    for filename in ('result.json','parsed.json','prompt.txt','input-hashes.json'):
        copy(folder/filename,out/name/filename)
    for path in (folder/'project/changelog').glob('*/qa.md'):
        copy(path,out/name/'qa.md')
    copy(folder/'project/.odoo-agents/flows/d31-jours-negatifs.json',out/name/'flow.json')
    # Conserver les sorties humaines claim/complete et leur provenance exacte,
    # sans exporter le home fournisseur ni le flux contenant tous les prompts.
    selected=[]; ids=set()
    for line in (folder/'raw.jsonl').read_text().splitlines():
        try: event=json.loads(line)
        except ValueError: continue
        for part in event.get('message',{}).get('content',[]):
            keep=False
            if part.get('type')=='tool_use' and re.search(r'odoo_flow\.py (?:claim|complete|status)\b', str(part.get('input',{}))):
                ids.add(part['id']);keep=True
            elif part.get('type')=='tool_result' and part.get('tool_use_id') in ids:
                keep=True
            if keep: selected.append({'source_event_sha256':hashlib.sha256(line.encode()).hexdigest(),'part':part})
    (out/name/'flow-operations.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in selected))
    gates=[e for e in result['new_events'] if e['node']=='module_high_gate']
    expected='non-pass' if name in ('known-reference','known-candidate','held-negative-candidate','known-v2') else 'pass'
    correct=None if not gates else ((gates[-1]['outcome']!='pass') if expected=='non-pass' else gates[-1]['outcome']=='pass')
    changed=[]
    before=json.loads((folder/'input-hashes.json').read_text())
    after=result['output_hashes']
    for key in before:
        if before[key]!=after.get(key):changed.append(key)
    summary.append({'id':name,'execution':result['status'],'seconds':result['seconds'],'model':parsed['actual_model'],
                    'expected':expected,'gate':gates[-1]['outcome'] if gates else None,'decision_conformant':correct,
                    'completed_event':parsed['completed_event'],'provider_error':parsed['provider_error'],
                    'changed_existing_files':changed,'raw_sha256':hashlib.sha256((folder/'raw.jsonl').read_bytes()).hexdigest()})
for name in ('rpc-runtime','rpc-runtime-calibrated'):
    folder=BASE/name
    for pattern in ('result.json','cleanup.json','environment.json','bridge-*.log','bridge-events.json','oracle*.log','setup.log','seed.log'):
        for src in folder.glob(pattern):copy(src,out/name/src.name)
    for src in (folder/'project').glob('*.json'):copy(src,out/name/'requests'/src.name)
(out/'evaluation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
sources={}
for relative in ('odoo/orm/models.py','odoo/service/model.py','addons/rpc/controllers/xmlrpc.py'):
    p=Path('/home/blegoff/odoo-sources/19.0')/relative
    sources[relative]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'odoo-source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
hashes={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256.json'}
(out/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
