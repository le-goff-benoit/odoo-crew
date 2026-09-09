import importlib.util, sys, json, time, threading, hashlib
from pathlib import Path
ROOT=Path('/home/blegoff/.odoo19-agents')
BASE=Path('/tmp/odoo-delegation-20260909')
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('delegation_experiment',BASE/'runner_delegation.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.ROOT=BASE/'resume-corpus'
folder=BASE/'N04-claude-resumed'
if folder.exists(): raise SystemExit('Dossier déjà utilisé ; aucun rejeu silencieux')
stop=threading.Event();started=time.monotonic()
def monitor():
 positions={}
 with (BASE/'resume-timeline.jsonl').open('w') as out:
  while not stop.wait(.05):
   for path in folder.glob('raw-*.jsonl'):
    with path.open() as stream:
     stream.seek(positions.get(str(path),0))
     while True:
      pos=stream.tell();line=stream.readline()
      if not line or not line.endswith('\n'): break
      positions[str(path)]=stream.tell()
      try: event=json.loads(line)
      except ValueError: continue
      entry={'received_seconds':round(time.monotonic()-started,3),'offset':pos,'event_sha256':hashlib.sha256(line.encode()).hexdigest(),'event':event}
      out.write(json.dumps(entry,ensure_ascii=False)+'\n');out.flush()
thread=threading.Thread(target=monitor,daemon=True);thread.start()
case=json.loads((mod.ROOT/'benchmarks/native/cases/N04/case.json').read_text())
try:
 state=mod.trial(folder,BASE/'reference',case,'claude',{'model':'opus','effort':'medium'},600)
 print(json.dumps(state,ensure_ascii=False))
finally:
 time.sleep(.2);stop.set();thread.join(timeout=1)
