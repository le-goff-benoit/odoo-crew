import sys,json,subprocess
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'/home/blegoff/.odoo19-agents/scripts')
import odoo_effort as e, odoo_usage as u, odoo_release_guard as g
ROOT=Path('/tmp/odoo-effort-review-20260909')
RESULT=[]
def stamp(s): return f'2026-09-09T00:00:{s:02d}Z'
def row(kind,s=0,**payload): return dict(type=kind,timestamp=stamp(s),payload=payload)
def tok(n): return dict(input_tokens=n,cached_input_tokens=0,cache_write_input_tokens=0,output_tokens=n,total_tokens=n*2)
def count(thread,response,n,s): return row('token_usage_record',s,response_id=response,thread_id=thread,thread_token_usage=tok(n))
def meta(thread): return row('session_meta',id=thread,timestamp=stamp(0))
def ctx(turn,s): return row('turn_context',s,turn_id=turn,model='synthetic-model')
def done(turn,s,dur=None): return row('event_msg',s,type='task_complete',turn_id=turn,**({'duration_ms':dur} if dur is not None else {}))
def trace(name,rows):
 p=ROOT/(name+'.jsonl');p.write_text(''.join(json.dumps(r)+'\n' for r in rows));return p
LINE=dict(task='T01',title='Synthetic task',agent='odoo-developer',optimistic_minutes=1,likely_minutes=2,pessimistic_minutes=3,assumptions=['synthetic'],basis='synthetic',confidence='low')
def release(name):
 r=ROOT/name/'changelog/R';
 if r.exists():
  import shutil
  shutil.rmtree(ROOT/name)
 r.mkdir(parents=True,exist_ok=True);(r/'README.md').write_text('# Synthetic R\n');e.init(r)
 with patch.object(e,'now',return_value='2026-09-08T00:00:00Z'):e.estimate(r,{'lines':[LINE]})
 return r
def record(name,**values):RESULT.append(dict(case=name,**values))
# Missing second completed turn duration, with both token measurements present.
p=trace('partial-duration',[meta('partial'),ctx('a',1),count('partial','a',10,10),done('a',10,9000),ctx('b',20),count('partial','b',20,30),done('b',30)])
r=release('partial-duration');entry=e.import_usage(r,'T01','odoo-developer','codex',p);rep=e.report(r)
record('partial-duration',native=u.read_usage(p,'codex'),reported=rep['rows'][0],guard_accepted=bool(g.required_artifacts(r)))
# Timer and another session contain the same response identity (inheritance/dedup protection should work).
r=release('timer-duplicate');p=trace('timer-parent',[meta('parent'),ctx('a',1),count('parent','base',10,2)])
with patch.object(e,'now',return_value=stamp(3)):first=e.start(r,'T01','odoo-developer','codex',p)
with p.open('a') as f:f.write(json.dumps(count('parent','shared-response',20,10))+'\n'+json.dumps(done('a',10,9000))+'\n')
with patch.object(e,'now',return_value=stamp(11)):first=e.stop(r,first['id'],p)
c=trace('timer-child',[meta('child'),ctx('b',3),count('child','shared-response',10,10),done('b',10,7000)])
try:
 second=e.import_usage(r,'T01','odoo-tester','codex',c);duplicate_rejected=False
except ValueError as err:
 second=str(err);duplicate_rejected=True
rep=e.report(r)
record('timer-duplicate',timer=first,child=second,rejected=duplicate_rejected,reported_total=rep['totals']['tokens'])
# Timer native declared cost is available at both boundaries.
def claude(s,ident,amount):return {'type':'assistant','timestamp':stamp(s),'sessionId':'cs','message':{'type':'message','id':ident,'model':'synthetic-model','usage':{'input_tokens':10,'cache_read_input_tokens':0,'cache_creation_input_tokens':0,'output_tokens':10}}}
def money(s,n):return {'type':'result','timestamp':stamp(s),'session_id':'cs','total_cost_usd':n}
r=release('timer-native-cost');p=trace('cost',[claude(1,'m1',0),money(2,1)])
with patch.object(e,'now',return_value=stamp(3)):entry=e.start(r,'T01','odoo-developer','claude',p)
with p.open('a') as f:f.write(json.dumps(claude(8,'m2',0))+'\n'+json.dumps(money(10,3))+'\n')
with patch.object(e,'now',return_value=stamp(11)):entry=e.stop(r,entry['id'],p)
record('timer-native-cost',baseline=entry['baseline']['provider_cost'],final_native=u.read_usage(p,'claude')['provider_cost'],timer_provider_cost=entry['provider_cost'],report_cost=e.report(r)['rows'][0]['costs'])
# Scope edits without plan.json (supported standalone estimation route).
r=release('scope-no-plan');(r/'demande.md').write_text('Initial request')
p=trace('scope',[meta('scope'),ctx('a',1),count('scope','scope-r',10,10),done('a',10,9000)])
e.import_usage(r,'T01','odoo-developer','codex',p);before=e.report(r)
(r/'demande.md').write_text('Changed request: now includes additional permission changes')
try:e.check_report(r);accepted=True
except ValueError:accepted=False
record('scope-no-plan',check_accepted=accepted,scope_changed=e.report(r)['rows'][0]['scope_changed'])
# Revision applicability not recorded at timer start; original forecast remains distinguishable but no per-entry reference.
r=release('revision-entry');p=trace('revision',[meta('revision'),ctx('a',1),count('revision','revision-0',10,2)])
with patch.object(e,'now',return_value=stamp(3)):entry=e.start(r,'T01','odoo-developer','codex',p)
e.estimate(r,{'lines':[dict(LINE,likely_minutes=3)]},'Added acceptance criterion')
with p.open('a') as f:f.write(json.dumps(count('revision','revision-1',20,10))+'\n')
with patch.object(e,'now',return_value=stamp(11)):entry=e.stop(r,entry['id'],p)
record('revision-entry',entry_keys=list(entry),initial_revision=e.report(r)['initial_revision'],latest_revision=e.report(r)['latest_revision'])
(ROOT/'results.json').write_text(json.dumps(RESULT,indent=2))
for result in RESULT:print(result['case'],json.dumps(result)[:900])
# Start with model unknown, then actual model becomes visible.
r=release('late-model');p=trace('late-model',[meta('late'),count('late','late-baseline',0,0)])
with patch.object(e,'now',return_value=stamp(1)):entry=e.start(r,'T01','odoo-developer','codex',p)
with p.open('a') as f:f.write(''.join(json.dumps(x)+'\n' for x in [ctx('a',2),count('late','late-answer',10,10),done('a',10,8000)]))
with patch.object(e,'now',return_value=stamp(11)):entry=e.stop(r,entry['id'],p)
record('late-model',baseline_model=entry['baseline']['model'],final_model=u.read_usage(p,'codex')['model'],entry_model=entry['model'],warnings=entry['warnings'])
# Two prices for exactly the same UTC date use distinct text timestamps.
r=release('equivalent-tariff-instant')
card=dict(provider='codex',model='synthetic-model',effective_at='2026-01-01T00:00:00Z',currency='USD',basis='api_equivalent',source='synthetic rate fixture only',scope='synthetic',input_per_million=1,cached_input_per_million=1,cache_write_input_per_million=1,output_per_million=1)
e.rates(r,{'cards':[card]})
try:e.rates(r,{'cards':[dict(card,effective_at='2026-01-01T01:00:00+01:00',input_per_million=99)]});rejected=False
except ValueError:rejected=True
record('equivalent-tariff-instant',accepted_cards=e.state(r)['rate_cards'],conflict_rejected=rejected)
# Full history inheritance removal with own thread boundary; adjacent windows and overlap.
r=release('windows');p=trace('windows',[meta('window'),ctx('a',1),count('window','window-0',10,5),count('window','window-1',20,10),done('a',10,9000),ctx('b',11),count('window','window-2',30,20),done('b',20,9000)])
a=e.import_usage(r,'T01','odoo-developer','codex',p,stamp(5),stamp(10));b=e.import_usage(r,'T01','odoo-tester','codex',p,stamp(10),stamp(20))
try:e.import_usage(r,'T01','odoo-tester','codex',p,stamp(9),stamp(20)); overlap=False
except ValueError:overlap=True
record('windows',first_tokens=a['tokens']['total_tokens'],second_tokens=b['tokens']['total_tokens'],total=e.report(r)['totals']['tokens'],overlap_rejected=overlap)
child=trace('inherited',[meta('child'),meta('parent'),ctx('parent-turn',1),count('parent','parent-response',200,2),row('event_msg',3,type='thread_settings_applied',thread_id='child'),ctx('child-turn',4),count('child','child-response',10,10),done('child-turn',10,6000)])
record('inheritance',native=u.read_usage(child,'codex'))
# CLI uses real native parser and produces all export files.
cp=subprocess.run([sys.executable,'/home/blegoff/.odoo19-agents/scripts/odoo_usage.py','read','--provider','codex','--source',str(child)],text=True,capture_output=True)
record('cli-native',exit=cp.returncode,tokens=json.loads(cp.stdout)['tokens']['total_tokens'])
e.report(r); files=[]
for name in e.REPORT_FILES:
 orig=(r/name).read_bytes();(r/name).write_text('tampered')
 try:g.required_artifacts(r); rejected=False
 except (ValueError,json.JSONDecodeError):rejected=True
 (r/name).write_bytes(orig);files.append(dict(file=name,rejected=rejected))
record('closure-export-integrity',checks=files)
# Real plan request-content change freshness.
r=release('scope-plan');request=r/'demande.md';request.write_text('Initial scope')
plan={'tasks':[dict(id='T01',title='Synthetic task',request='changelog/R/demande.md',acceptance=['A'],scopes=['changelog/R/demande.md'],risk='normal',route='standard',depends_on=[])]}
(r/'plan.json').write_text(json.dumps(plan));e.estimate(r,{'lines':[LINE]},'Link to plan');e.report(r);request.write_text('Changed scope')
try:e.check_report(r);rejected=False
except ValueError:rejected=True
record('scope-plan',stale_rejected=rejected,scope_changed=e.report(r)['rows'][0]['scope_changed'])
(ROOT/'results.json').write_text(json.dumps(RESULT,indent=2))
for item in RESULT[5:]:print(item['case'],json.dumps(item)[:700])
# Resume same dedicated native session, refresh in place with history, and idempotent reread.
r=release('resume');p=trace('resume',[meta('resume'),ctx('a',1),count('resume','resume-1',10,10),done('a',10,9000)])
a=e.import_usage(r,'T01','odoo-developer','codex',p)
with p.open('a') as f:f.write(''.join(json.dumps(x)+'\n' for x in [ctx('b',11),count('resume','resume-2',20,20),done('b',20,9000)]))
b=e.import_usage(r,'T01','odoo-developer','codex',p);c=e.import_usage(r,'T01','odoo-developer','codex',p)
record('resume',same_id=a['id']==b['id']==c['id'],entries=len(e.state(r)['entries']),history=len(c['history']),seconds=c['seconds'],tokens=c['tokens']['total_tokens'])
# Native cache categories priced once, then declared cost takes precedence over calculated price.
r=release('cache');p=trace('cache',[meta('cache'),ctx('a',1),row('token_usage_record',10,thread_id='cache',response_id='cache-r',thread_token_usage=dict(input_tokens=1000,cached_input_tokens=600,cache_write_input_tokens=100,output_tokens=200,total_tokens=1200)),done('a',10,9000)])
e.import_usage(r,'T01','odoo-developer','codex',p);e.rates(r,{'cards':[dict(card,input_per_million=10,cached_input_per_million=1,cache_write_input_per_million=12.5,output_per_million=20)]})
record('native-cache-cost',cost=e.report(r)['rows'][0]['costs'][0]['cost']['amount'],expected=.00885)
# Partial revisions preserve unaffected roles, and first revision remains unchanged.
r=release('partial-revision');initial=e.state(r)['estimates'][0]
e.estimate(r,{'lines':[dict(LINE,agent='odoo-tester')]},'Add QA');e.estimate(r,{'lines':[dict(LINE,likely_minutes=3)]},'Revise implementation')
record('partial-revision',initial_unchanged=e.state(r)['estimates'][0]==initial,latest_roles=[x['agent'] for x in e.state(r)['estimates'][-1]['lines']])
(ROOT/'results.json').write_text(json.dumps(RESULT,indent=2))
