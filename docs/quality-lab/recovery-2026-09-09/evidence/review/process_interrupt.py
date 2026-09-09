import json, multiprocessing, os, signal, sys
from pathlib import Path
sys.path[:0]=['/home/blegoff/.odoo19-agents/scripts','/home/blegoff/.odoo19-agents/tests']
from test_odoo_recovery import RecoveryTests,flow,reception
c=RecoveryTests();c.setUp()
try:
 p,_=c.accepted(); before=p.read_bytes()
 def child():
  original=reception.atomic_publish
  def killed(target,content):
   original(target,content)
   os.kill(os.getpid(),signal.SIGKILL)
  reception.atomic_publish=killed
  flow.publish_memory(p,c.graph,c.owner)
 process=multiprocessing.get_context('fork').Process(target=child);process.start();process.join(10)
 if process.is_alive():process.kill();process.join();raise RuntimeError('child timeout')
 actions=flow.publish_memory(p,c.graph,c.owner)
 c.finish(p,'journal_task',[c.root/'.odoo-agents/JOURNAL.md'],'done')
 result={'child_exitcode':process.exitcode,'resume_actions':actions,'journal_outcome':flow.load_json(p)['events'][-1]['outcome'],'manual_state_repair':False}
 print(json.dumps(result,ensure_ascii=False,indent=2))
 Path('/tmp/odoo-recovery-20260909/review/process-interrupt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
finally:c.doCleanups()
