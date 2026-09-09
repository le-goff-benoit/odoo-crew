from pathlib import Path
import json,time,datetime,subprocess,sys,hashlib,shutil
B=Path('/tmp/odoo-delegation-comparison-20260909');R=Path('/home/blegoff/.odoo19-agents');LEDGER=B/'run-ledger.json'
def save(rows):LEDGER.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
action,name=sys.argv[1:3];rows=json.loads(LEDGER.read_text());agent='/root/comp_'+name.lower().replace('-','_')
if action=='start':
 assert not any(r['status']=='running' for r in rows)
 protocol=json.loads((B/'protocol.json').read_text());assert name==protocol['order'][len(rows)]
 frozen=json.loads((B/'FROZEN.json').read_text())
 for p,digest in frozen['files'].items():
  prefix,rel=p.split('/',1)
  if prefix=='bench':file=R/'benchmarks/delegation_comparison'/rel
  elif rel.startswith(name+'/'):file=B/'runs'/rel
  else:continue
  assert hashlib.sha256(file.read_bytes()).hexdigest()==digest,str(file)
 rows.append({'run':name,'agent':agent,'status':'running','dispatch_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'dispatch_monotonic_ns':time.monotonic_ns()});save(rows);print('Started',name)
elif action=='finish':
 row=next(r for r in rows if r['run']==name);assert row['status']=='running'
 native=B/'native'/name
 p=subprocess.run(['python3',str(R/'benchmarks/delegation_comparison/native_metrics.py'),'--sessions','/home/blegoff/.codex/sessions/2026/09/09','--agent',agent,'--output',str(native)],check=True,capture_output=True,text=True)
 metrics=json.loads((native/'metrics.json').read_text());assert metrics['complete'],metrics
 snapshot=B/'snapshots'/name;shutil.copytree(B/'runs'/name,snapshot,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git'))
 row.update(status='finished',collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),collected_monotonic_ns=time.monotonic_ns(),snapshot=str(snapshot),metrics=str(native/'metrics.json'),hashes={str(p.relative_to(snapshot)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(snapshot.rglob('*')) if p.is_file()});save(rows)
 print(json.dumps({k:v for k,v in metrics.items() if k!='threads'},ensure_ascii=False))
else:raise SystemExit(action)
