import importlib.util,json,sys
from pathlib import Path
ROOT=Path('/home/blegoff/.odoo19-agents')
spec=importlib.util.spec_from_file_location('reception_tests',ROOT/'tests/test_odoo_reception.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
flow=mod.flow
results={}
# Real claim handoff A -> B; B signs reception and completes own gate.
t=mod.ReceptionTests();t.setUp()
try:
 p=t.ready();review,data=t.receipt(t.prepare(p)); b='codex-new-orchestrator'
 flow.release_claim(p,t.graph,'module_task_gate',t.owner,'Transfert explicite de responsabilité')
 flow.claim_node(p,t.graph,'module_task_gate',b)
 data['reviewer']=b;review.write_text(json.dumps(data))
 try:
  state=flow.complete_claimed_node(p,t.graph,'module_task_gate','pass',[str(review)],None,b,False)
  results['owner_handoff']={'outcome':state['events'][-1]['outcome'],'reviewer':b,'completion_owner':b}
 except flow.FlowError as exc: results['owner_handoff']={'rejected':str(exc)}
finally:t.doCleanups()
# Publication concurrent change after gate passes; no graph route repairs its receipt.
t=mod.ReceptionTests();t.setUp()
try:
 p=t.ready();review,data=t.receipt(t.prepare(p));t.finish(p,'module_task_gate',[review])
 memory=t.root/'.odoo-agents/JOURNAL.md';memory.write_text(memory.read_text()+'\nUne autre tâche terminée.')
 flow.claim_node(p,t.graph,'journal_task',t.owner)
 (t.root/'.odoo-agents/PROJECT.md').write_bytes((t.root/'project-draft.md').read_bytes())
 errs={}
 for name,fn in [('reprepare',lambda:t.prepare(p,'bundle-new.json')),('journal_done',lambda:t.finish(p,'journal_task',[memory],'done')),('journal_blocked',lambda:t.finish(p,'journal_task',[memory],'blocked'))]:
  try:fn();errs[name]='ACCEPTED'
  except flow.FlowError as e:errs[name]=str(e)
 state=flow.load_json(p);results['postpass']={'errors':errs,'status':state['status'],'ready':flow.ready_nodes(state,state['graph_snapshot']),'journal_outcomes':flow.node_outcomes(state['graph_snapshot'],'journal_task')}
finally:t.doCleanups()
# QA coverage pinned to spec A, reception independently reviews spec B: tool does not bind them.
t=mod.ReceptionTests();t.setUp()
try:
 p=t.ready();bound=t.root/'bound-spec.md';bound.write_text("## Critères d'acceptation\n- [ ] Une obligation différente.\n")
 cov=t.root/'coverage.json';flow.bind_criteria(p,t.graph,bound,cov,t.owner)
 data=json.loads(cov.read_text());data['criteria'][0].update(status='covered',evidence=[{'path':'runtime.log','sha256':mod.reception.digest((t.root/'runtime.log').read_bytes())}]);cov.write_text(json.dumps(data))
 review,data=t.receipt(t.prepare(p));state=t.finish(p,'module_task_gate',[review,cov]);results['spec_mismatch']={'outcome':state['events'][-1]['outcome'],'coverage_spec':state['qa_contract']['source'],'reception_spec':'spec.md'}
finally:t.doCleanups()
print(json.dumps(results,ensure_ascii=False,indent=2))
