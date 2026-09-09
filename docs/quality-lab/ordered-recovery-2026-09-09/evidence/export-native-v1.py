from pathlib import Path
import argparse,json,hashlib
p=argparse.ArgumentParser();p.add_argument('agent');p.add_argument('output',type=Path);a=p.parse_args()
found=[]
for src in Path('/home/blegoff/.codex/sessions/2026/09/09').glob('*.jsonl'):
 try:meta=json.loads(src.open().readline())['payload']
 except Exception:continue
 origin=meta.get('source',{});spawn=origin.get('subagent',{}).get('thread_spawn',{}) if isinstance(origin,dict) else {}
 if spawn.get('agent_path')==a.agent:found.append((src,meta))
assert len(found)==1,(a.agent,len(found))
src,meta=found[0];raw=src.read_bytes();rows=[]
for line in raw.splitlines():
 try:x=json.loads(line)
 except ValueError:continue
 typ=x.get('type');payload=x.get('payload',{})
 if typ=='session_meta':x['payload']={k:v for k,v in payload.items() if k in ('id','timestamp','source','agent_nickname','agent_role','model_provider')}
 elif typ=='turn_context':x['payload']={k:v for k,v in payload.items() if k in ('turn_id','model','effort','reasoning_effort')}
 elif typ=='token_usage_record':pass
 elif typ=='response_item':
  keep=payload.get('type') in ('function_call','function_call_output','custom_tool_call','custom_tool_call_output')
  keep=keep or (payload.get('type')=='message' and payload.get('role')=='assistant' and payload.get('channel')=='final')
  if not keep:continue
 else:continue
 rows.append(x)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
manifest={'agent':a.agent,'thread_id':meta['id'],'source_snapshot_sha256':hashlib.sha256(raw).hexdigest(),'export_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'records':len(rows),'policy':'Allowlisted native session records: agent provenance, model/effort, tool calls/results, final answer and usage. All system/developer/user messages, analysis and other events omitted. Source is live append-only; hash identifies bytes at export time.'}
a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(a.agent,len(rows))
