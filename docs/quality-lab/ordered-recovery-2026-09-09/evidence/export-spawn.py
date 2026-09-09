from pathlib import Path
import os,json,sys
name=sys.argv[1];out=Path(sys.argv[2]);src=list(Path('/home/blegoff/.codex/sessions/2026/09/09').glob('*'+os.environ['CODEX_THREAD_ID']+'*.jsonl'))[0]
records=[json.loads(l) for l in src.open()];chosen=[];ids=set()
for x in records:
 p=x.get('payload',{})
 if x.get('type')=='response_item' and p.get('type')=='function_call' and p.get('name')=='spawn_agent':
  try:a=json.loads(p['arguments'])
  except Exception:continue
  if a.get('task_name')==name:chosen.append(x);ids.add(p['call_id'])
for x in records:
 p=x.get('payload',{})
 if x.get('type')=='response_item' and p.get('type')=='function_call_output' and p.get('call_id') in ids:chosen.append(x)
assert chosen,(name,'no native spawn');out.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in chosen));print(name,len(chosen),'native spawn records')
