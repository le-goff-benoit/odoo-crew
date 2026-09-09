import json,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path('/tmp/odoo-effort-review-20260909/add-task-cli')
SCRIPT='/home/blegoff/.odoo19-agents/scripts/odoo_effort.py'
ROOT.mkdir(exist_ok=True)
def setup(name):
 p=ROOT/name/'changelog/R';p.mkdir(parents=True,exist_ok=True);(p/'README.md').write_text('# Synthetic add-task\n');return p
def cli(*args):
 r=subprocess.run([sys.executable,SCRIPT,*map(str,args)],capture_output=True,text=True)
 return {'args':list(map(str,args)),'exit':r.returncode,'stdout':json.loads(r.stdout) if r.returncode==0 else r.stdout,'stderr':r.stderr}
r=setup('without-plan');calls=[]
calls.append(cli('init',r));calls.append(cli('add-task',r,'--task','PAST','--title','Past synthetic execution'))
calls.append(cli('import-usage',r,'--task','PAST','--agent','odoo-developer','--provider','codex','--source','/tmp/odoo-effort-review-20260909/partial-duration.jsonl'))
# Use source with fully known time to test legacy execution independently of duration partiality.
r2=setup('known-time');calls.append(cli('init',r2));calls.append(cli('add-task',r2,'--task','PAST','--title','Past synthetic execution'))
calls.append(cli('import-usage',r2,'--task','PAST','--agent','odoo-developer','--provider','codex','--source','/tmp/odoo-effort-review-20260909/inherited.jsonl'))
report=cli('report',r2);calls.append(report)
before=(r2/'effort.json').read_bytes();different=cli('add-task',r2,'--task','PAST','--title','Unexpected different title');calls.append(different)
unchanged=(r2/'effort.json').read_bytes()==before
rp=setup('with-plan');(rp/'demande.md').write_text('Synthetic plan request');(rp/'plan.json').write_text(json.dumps({'tasks':[dict(id='T01',title='Plan task',request='changelog/R/demande.md',acceptance=['A'],scopes=['changelog/R/demande.md'],risk='normal',route='standard',depends_on=[])]}))
calls.append(cli('init',rp));outside=cli('add-task',rp,'--task','OUTSIDE','--title','Outside');calls.append(outside)
data=report['stdout'];row=data['rows'][0]
checks={'no_estimates':json.loads((r2/'effort.json').read_text())['estimates']==[], 'actual_known':row['actual_minutes']==0.1,'forecast_unknown':row['initial'] is None and row['revised'] is None and data['totals']['planned_initial_minutes'] is None and data['totals']['planned_revised_minutes'] is None,'variance_unknown':row['delta_minutes'] is None and row['delta_percent'] is None,'different_title_rejected':different['exit']!=0,'rejected_title_preserves_state':unchanged,'task_outside_plan_rejected':outside['exit']!=0}
result={'verdict':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'calls':calls,'script_sha256':hashlib.sha256(Path(SCRIPT).read_bytes()).hexdigest()}
Path('/tmp/odoo-effort-review-20260909/add-task-review.json').write_text(json.dumps(result,indent=2))
print(json.dumps(checks,indent=2))
