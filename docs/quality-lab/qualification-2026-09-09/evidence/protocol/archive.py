from pathlib import Path
import hashlib,json,shutil,sys
BASE=Path(__file__).resolve().parent
ROOT=Path('/home/blegoff/.odoo19-agents')
sys.path.insert(0,str(ROOT/'scripts'))
from odoo_bench_native import copy_project
DEST=ROOT/'docs/quality-lab/qualification-2026-09-09/evidence/native'
DEST.mkdir(parents=True,exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in sys.argv[1:]:
 src=BASE/name; dst=DEST/name
 dst.mkdir(parents=True,exist_ok=False)
 for p in src.iterdir():
  if p.is_file() and p.suffix in {'.json','.md','.log','.txt'} and not p.name.startswith('raw'):
   shutil.copy2(p,dst/p.name)
  elif p.is_dir() and (p.name=='project' or p.name.startswith('after-')):
   copy_project(p,dst/p.name)
 for raw in src.glob('raw*.jsonl'):
  selected=[];ids=set()
  for line in raw.read_text().splitlines():
   try:event=json.loads(line)
   except ValueError:continue
   h=hashlib.sha256((line+'\n').encode()).hexdigest()
   if event.get('type')=='system' and event.get('subtype') in {'task_started','task_progress','task_notification'}:
    selected.append({'event_sha256':h,'event':event})
   for block in event.get('message',{}).get('content',[]):
    if block.get('type')=='tool_use' and 'odoo_flow.py' in json.dumps(block.get('input',{})):
     ids.add(block['id']);selected.append({'event_sha256':h,'block':block})
    elif block.get('type')=='tool_result' and block.get('tool_use_id') in ids:
     selected.append({'event_sha256':h,'block':block})
  (dst/(raw.stem+'-flow-events.json')).write_text(json.dumps({'raw_sha256':digest(raw),'events':selected},ensure_ascii=False,indent=2)+'\n')
 print(name,'archived')
