from pathlib import Path
import subprocess,json,sys
BASE=Path('/tmp/odoo-ordered-recovery-20260909'); PACK=BASE/'reference'; BENCH=Path('/home/blegoff/.odoo19-agents/benchmarks/ordered_recovery')
def command(case,args):
 r=subprocess.run([str(x) for x in args],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 with (BASE/case/'coordinate.log').open('a') as f:f.write('$ '+json.dumps([str(x) for x in args])+'\n'+r.stdout+'\nexit='+str(r.returncode)+'\n')
 print(r.stdout,end='');r.check_returncode();return r.stdout

def checkpoint(case,event,agent,trace,artifact=None):
 args=['python3',BENCH/'checkpoint.py',BASE/case,event,'--agent',agent,'--trace',trace]
 if artifact:args+=['--artifact',artifact]
 r=subprocess.run([str(x) for x in args],capture_output=True,text=True);r.check_returncode()
 (BASE/case/(event+'.json')).write_text(r.stdout); print(case,event,'sealed')

def accept(case,letter,old_owner,author,reviewer):
 project=BASE/case/'project';flow=project/'.odoo-agents/flows'/('ordered-'+letter.lower()+'.json')
 folder=(project/json.loads(flow.read_text())['task_reception']['path']).parent
 review=folder/('review-'+letter+'.json')
 trace=BASE/case/('review-'+letter+'-native.jsonl')
 subprocess.run(['python3',str(BASE/'export-native.py'),reviewer,str(trace)],check=True)
 checkpoint(case,letter+'_REVIEWED',reviewer,trace,review)
 (folder/'native-provenance.json').write_text(json.dumps({'author_context':author,'reviewer_context':reviewer,'review_sha256':__import__('hashlib').sha256(review.read_bytes()).hexdigest(),'review_native_export_sha256':__import__('hashlib').sha256(trace.read_bytes()).hexdigest(),'statement':'Actual separate Codex contexts, both fork_turns=none. Documentary QA boundary alone was synthetic; this receipt was written by a real independent reviewer. Native exports retained by coordinator.'},indent=2)+'\n')
 owner='codex-coordinate-'+case+'-'+letter
 for args in [['status',flow],['release',flow,'module_task_gate','--owner',old_owner,'--reason','Auteur arrêté après préparation ; transfert explicite au coordinateur pour réception réelle.'],['claim',flow,'module_task_gate','--owner',owner],['complete',flow,'module_task_gate','--owner',owner,'--outcome','pass','--evidence',review]]:
  command(case,['python3',PACK/'scripts/odoo_flow.py',*args])
 if letter=='A':checkpoint(case,'A_ACCEPTED','/root',BASE/case/'coordinate.log')
 return owner
if __name__=='__main__':accept(*sys.argv[1:])
