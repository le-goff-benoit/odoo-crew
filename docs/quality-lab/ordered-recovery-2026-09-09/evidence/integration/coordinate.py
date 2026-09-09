from pathlib import Path
import json,subprocess,sys
BASE=Path('/tmp/odoo-ordered-recovery-20260909'); I=BASE/'integration'; P=I/'run/project'; R=P/'changelog/2026-09-09_01_quantite-positive-a-la-confirmation'; PACK=BASE/'reference'; F=next((P/'.odoo-agents/flows').glob('plan-a-*.json')); OWNER='codex-integration-orchestrateur'
def call(*args):
 argv=[str(x) for x in args]; result=subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 with (I/'coordinate.log').open('a') as stream:stream.write('$ '+json.dumps(argv,ensure_ascii=False)+'\n'+result.stdout+'\nexit='+str(result.returncode)+'\n')
 print(result.stdout,end='');result.check_returncode();return result.stdout
def flow(*args):return call('python3',PACK/'scripts/odoo_flow.py',*args)
def claim(node,owner=OWNER):return flow('claim',F,node,'--owner',owner)
def complete(node,outcome,evidence,owner=OWNER):return flow('complete',F,node,'--owner',owner,'--outcome',outcome,'--evidence',evidence)
if __name__=='__main__':flow(*sys.argv[1:])
