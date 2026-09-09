from pathlib import Path
import json,subprocess,hashlib
B=Path('/tmp/odoo-ordered-recovery-20260909')
names=['ordered_cases','local_odoo_options','odoo_bootstrap','odoo_analysis','o01_author_a','o02_author_a','o03_author_a','o01_author_b','o01_review_a','o02_review_a','o03_review_a','o01_review_b','o01_resume','o02_resume','o03_resume','o01_resume/review_recovery','ordered_audit','corpus_review','odoo_implementation','odoo_qa','odoo_receipt']
execution={'o01_author_a','o02_author_a','o03_author_a','o01_author_b','o01_resume','o02_resume','o03_resume','odoo_implementation','odoo_qa'}
rows=[]
for name in names:
 matches=[]
 for p in Path('/home/blegoff/.codex/sessions/2026/09/09').glob('*.jsonl'):
  m=json.loads(p.open().readline())['payload'];s=m.get('source',{});sp=s.get('subagent',{}).get('thread_spawn',{}) if isinstance(s,dict) else {}
  if sp.get('agent_path')=='/root/'+name:matches.append((p,m))
 if not matches:continue
 assert len(matches)==1
 p,m=matches[0];xs=[json.loads(l) for l in p.read_text().splitlines()];ctx=[x['payload'] for x in xs if x['type']=='turn_context'];usage=[x['payload'] for x in xs if x['type']=='token_usage_record'];ends=[x['payload'] for x in xs if x['type']=='event_msg' and x['payload'].get('type')=='task_complete']
 out=B/'native-final'/(name.replace('/','--')+'.jsonl');subprocess.run(['python3',str(B/'export-native.py'),'/root/'+name,str(out)],check=True,capture_output=True)
 rows.append({'agent':'/root/'+name,'category':'execution' if name in execution else 'auxiliary','thread_id':m['id'],'started_at':m.get('timestamp'),'completed_turns':len(ends),'turns':[{k:v for k,v in e.items() if k in ('turn_id','started_at','completed_at','duration_ms','time_to_first_token_ms')} for e in ends],'max_turn_duration_ms':max([e.get('duration_ms',0) for e in ends],default=0),'active_duration_ms':sum(e.get('duration_ms',0) for e in ends),'last_completion':ends[-1].get('completed_at') if ends else None,'model_effort':sorted({(c.get('model'),c.get('effort')) for c in ctx}),'thread_tokens':usage[-1].get('thread_token_usage') if usage else None,'usage_records':len(usage),'native_export':str(out.relative_to(B))})
result={'method':'One final cumulative thread_token_usage per actual child thread; never sum turn/thread cumulative counters. Active duration sums task_complete durations, excludes idle barriers. Elapsed campaign/root work separate. No monetary cost inferred; native collaboration consumes tokens, paid CLI calls zero. Root excluded because session spans previous campaigns.','agents':rows,'counts':{c:sum(r['category']==c for r in rows) for c in ['execution','auxiliary']}}
result['totals']={key:sum((row['thread_tokens'] or {}).get(key,0) for row in rows) for key in {key for row in rows for key in (row['thread_tokens'] or {})}}
result['all_contexts_completed']=all(row['completed_turns'] for row in rows) and len(rows)==len(names)
result['maximum_turn_seconds']=max([row['max_turn_duration_ms'] for row in rows],default=0)/1000
(B/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result['counts'])
