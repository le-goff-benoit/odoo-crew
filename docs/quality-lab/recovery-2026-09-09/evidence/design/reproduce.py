import json, sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path[:0]=[str(BASE/'reference/scripts'), str(BASE/'reference/tests')]
import odoo_flow as flow
import odoo_plan as plan
import odoo_reception as reception
from test_odoo_reception import ReceptionTests
case=ReceptionTests(); case.setUp(); temporary_root=case.root; case.root=BASE/'project'; case.root.mkdir(exist_ok=True)
import shutil
shutil.copytree(temporary_root,case.root,dirs_exist_ok=True)
path=case.ready(); pinned=case.prepare(path); review,_=case.receipt(pinned)
case.finish(path,'module_task_gate',[review]); flow.claim_node(path,case.graph,'journal_task',case.owner)
original=path.read_bytes(); before_memory={p:(case.root/p).read_bytes() for p in reception.TARGETS}
(case.root/'.odoo-agents/JOURNAL.md').write_text('Publication concurrente à conserver.')
results={'reference':'8d2b940','fixture':'synthetic ready-gate tokens, no Odoo execution','state':str(path)}
def attempt(key,fn):
 try: fn(); results[key]={'unexpected':'success'}
 except Exception as e: results[key]={'error':str(e),'state_unchanged':path.read_bytes()==original}
attempt('check_bases_after_concurrent_publication',lambda: reception.verify_bundle(case.root,pinned))
attempt('complete_journal_after_concurrent_publication',lambda: case.finish(path,'journal_task',[case.root/'runtime.log'],'done'))
attempt('prepare_new_reception_after_pass',lambda: case.prepare(path,'v2.json'))
attempt('complete_journal_blocked_outcome',lambda: case.finish(path,'journal_task',[case.root/'runtime.log'],'blocked'))
release=case.root/'changelog/R'; release.mkdir(parents=True); (release/'README.md').write_text('Fixture release')
p={'schema':1,'tasks':[{'id':'T1','title':'Test','request':'request.md','acceptance':['Calcul préservé'],'scopes':['module'],'risk':'normal','route':'module','attempts':[{'flow':str(path.relative_to(case.root))}]}],'history':[]}
plan.save(release,p)
attempt('plan_reopen_running_flow',lambda:plan.mutate(release,'reopen','T1',reason='Publication concurrente'))
# Interruption after one manually copied draft: original guard rejects both resume directions.
for p,b in before_memory.items(): (case.root/p).write_bytes(b)
(case.root/'.odoo-agents/PROJECT.md').write_bytes((case.root/'project-draft.md').read_bytes())
attempt('check_bases_after_one_copy',lambda:reception.verify_bundle(case.root,pinned))
attempt('complete_journal_after_one_copy',lambda:case.finish(path,'journal_task',[case.root/'runtime.log'],'done'))
results['position']=flow.state_summary(flow.load_json(path),flow.load_json(case.graph))
(BASE/'reproduction.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
case.doCleanups()
