from pathlib import Path
import json,hashlib,importlib.util
b=Path('/tmp/odoo-delegation-comparison-20260909');p=Path('/home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/native_metrics.py');s=importlib.util.spec_from_file_location('m',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
names=['comparison_design','comparison_corpus','comparison_runtime','comparison_quality','pm_reference','pm_candidate','pm_quality'];out=b/'auxiliary-native';out.mkdir(exist_ok=True);rows=[]
for source in Path('/home/blegoff/.codex/sessions/2026/09/09').glob('*.jsonl'):
 with source.open() as f:
  try:first=json.loads(next(f))
  except (ValueError,StopIteration):continue
 name=m.agent_path(first)
 if name not in ['/root/'+n for n in names]:continue
 raw=source.read_bytes();owned=m.own_records([json.loads(l) for l in raw.splitlines()]);records=[a for r in owned if (a:=m.allowed(r)) is not None and a['type']!='response_item']
 target=out/(name.split('/')[-1]+'.jsonl');target.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records));row=m.summarize(records);row.update(export=target.name,export_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),source_snapshot_sha256=hashlib.sha256(raw).hexdigest());row.pop('tool_calls');row.pop('child_spawns');rows.append(row)
(out/'metrics.json').write_text(json.dumps({'threads':rows,'scope':'Auxiliary metadata only: no messages or tool content exported. Preparation, common reviews and separate communication test excluded from primary timing. Root cumulative turn spans earlier campaigns and is not attributable, not zero.'},indent=2)+'\n')
print([(r['agent'],r['complete']) for r in rows])
