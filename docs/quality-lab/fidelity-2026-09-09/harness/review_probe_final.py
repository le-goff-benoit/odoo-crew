import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path('/home/blegoff/.odoo19-agents')
spec=importlib.util.spec_from_file_location('reception_tests',ROOT/'tests/test_odoo_reception.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);flow=mod.flow
results={'file_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['scripts/odoo_flow.py','scripts/odoo_reception.py','tests/test_odoo_reception.py']}}
def rejected(fn,p):
 before=p.read_bytes();registry=flow.registry_path(flow.load_json(p));old_registry=registry.read_bytes()
 try:fn();return {'unexpected':'accepted'}
 except flow.FlowError as exc:return {'refused':str(exc),'state_unchanged':p.read_bytes()==before,'registry_unchanged':registry.read_bytes()==old_registry}
for self_review in (True,False):
 t=mod.ReceptionTests();t.setUp()
 try:
  p=t.ready();review,data=t.receipt(t.prepare(p));b='codex-new-orchestrator'
  flow.release_claim(p,t.graph,'module_task_gate',t.owner,'Transfert explicite de responsabilité');flow.claim_node(p,t.graph,'module_task_gate',b)
  data['reviewer']=b if self_review else 'codex-reviewer-distinct';review.write_text(json.dumps(data))
  fn=lambda:flow.complete_claimed_node(p,t.graph,'module_task_gate','pass',[str(review)],None,b,False)
  results['owner_self' if self_review else 'owner_distinct']=rejected(fn,p) if self_review else {'outcome':fn()['events'][-1]['outcome']}
 finally:t.doCleanups()
for bind_first in (True,False):
 t=mod.ReceptionTests();t.setUp()
 try:
  p=t.ready();bound=t.root/'bound-spec.md';bound.write_text("## Critères d'acceptation\n- [ ] Une obligation différente.\n");cov=t.root/'coverage.json'
  if not bind_first:review,_=t.receipt(t.prepare(p))
  flow.bind_criteria(p,t.graph,bound,cov,t.owner)
  data=json.loads(cov.read_text());data['criteria'][0].update(status='covered',evidence=[{'path':'runtime.log','sha256':mod.reception.digest((t.root/'runtime.log').read_bytes())}]);cov.write_text(json.dumps(data))
  fn=(lambda:t.prepare(p)) if bind_first else (lambda:t.finish(p,'module_task_gate',[review,cov]))
  results['spec_bind_first' if bind_first else 'spec_prepare_first']=rejected(fn,p)
 finally:t.doCleanups()
t=mod.ReceptionTests();t.setUp()
try:
 p=t.ready();state=flow.load_json(p);state['plan_task']={'release':str(t.root/'changelog/release'),'id':'T01','risk':'normal'};flow.write_state(p,state)
 results['plan_refused']=rejected(lambda:t.prepare(p),p)
finally:t.doCleanups()
print(json.dumps(results,ensure_ascii=False,indent=2))
