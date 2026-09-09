import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path('/home/blegoff/.odoo19-agents')
BASE=Path(__file__).resolve().parent
OUT=ROOT/'docs/quality-lab/coverage-2026-09-09/evidence'
OUT.mkdir(parents=True,exist_ok=True)
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for pattern in ['*protocol.json','protocol.json','*hashes.json','calibration.json','calibrate.py','replay.py','extension-*.log','suite.log','build-isolated.log','parity-isolated.log','archive.py']:
    for p in BASE.glob(pattern):copy(p,OUT/p.name)
for folder in ['calibration','held-positive-input','held-negative-input']:
    for p in (BASE/folder).rglob('*'):
        if p.is_file() and not p.name.endswith('.lock'):copy(p,OUT/'fixtures'/folder/p.relative_to(BASE/folder))
for variant in ['reference','candidate','candidate-v2']:
    for name in ['roles/orchestration.md','scripts/odoo_flow.py','scripts/odoo_coverage.py']:
        p=BASE/variant/name
        if p.exists():copy(p,OUT/'variants'/variant/name)
results=[]
for name in ['known-reference','known-candidate','held-positive-candidate','held-negative-v2']:
    folder=BASE/name
    result=json.loads((folder/'result.json').read_text())
    parsed=json.loads((folder/'parsed.json').read_text())
    for filename in ['result.json','parsed.json','prompt.txt','input-hashes.json']:
        copy(folder/filename,OUT/name/filename)
    statefile=folder/'project/.odoo-agents/flows/d31-jours-negatifs.json'
    copy(statefile,OUT/name/'flow.json')
    state=json.loads(statefile.read_text())
    for p in (folder/'project/changelog').rglob('*'):
        if p.is_file() and (p.name in ['qa.md','revue_fonctionnelle.md','static.md','client.md','runtime.md','export.csv'] or 'coverage' in p.name):
            copy(p,OUT/name/'release'/p.name)
    relevant=[];ids=set();metrics=None
    for raw in (folder/'raw.jsonl').read_text().splitlines():
        try:event=json.loads(raw)
        except ValueError:continue
        if event.get('type')=='result':metrics={k:event.get(k) for k in ['total_cost_usd','duration_ms','usage','modelUsage','is_error']}
        for part in event.get('message',{}).get('content',[]):
            keep=False
            if part.get('type')=='tool_use' and re.search(r'odoo_flow\.py (?:claim|complete|status|bind-criteria)\b',str(part.get('input',{}))):
                ids.add(part['id']);keep=True
            elif part.get('type')=='tool_result' and part.get('tool_use_id') in ids:keep=True
            if keep:relevant.append({'source_event_sha256':hashlib.sha256(raw.encode()).hexdigest(),'part':part})
    (OUT/name/'flow-operations.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in relevant))
    (OUT/name/'provider-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
    gates=[event for event in result['new_events'] if event['node']=='module_high_gate']
    results.append({'id':name,'execution':result['status'],'seconds':result['seconds'], 'actual_model':parsed['actual_model'],
                    'actual_effort':parsed['actual_effort'],'contract_bound':bool(state.get('qa_contract')),
                    'outcome':gates[-1]['outcome'] if gates else None,'total_cost_usd_cli':metrics.get('total_cost_usd') if metrics else None,
                    'raw_sha256':hashlib.sha256((folder/'raw.jsonl').read_bytes()).hexdigest()})
(OUT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
hashes={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256.json'}
(OUT/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
