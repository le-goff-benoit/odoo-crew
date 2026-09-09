import json, sys
from pathlib import Path
sys.path[:0]=['/home/blegoff/.odoo19-agents/scripts','/home/blegoff/.odoo19-agents/tests']
from test_odoo_recovery import RecoveryTests
from odoo_reception import verify_bundle
results=[]
for content in ['', '\n   \n']:
 c=RecoveryTests(); c.setUp()
 try:
  (c.root/'.odoo-agents/JOURNAL.md').write_text(content)
  p=c.ready(); pin=c.prepare(p)
  try:
   verify_bundle(c.root,pin)
   r,review=c.receipt(pin)
   review['checks']['source_memory']['citations']=[item for item in review['checks']['source_memory']['citations'] if item['quote'].strip()]
   r.write_text(json.dumps(review))
   c.finish(p,'module_task_gate',[r]); verdict='pass'
  except Exception as e: verdict=f'{type(e).__name__}: {e}'
  results.append({'case':'existing blank journal','bytes':len(content),'result':verdict})
 finally:c.doCleanups()
Path('/tmp/odoo-recovery-20260909/review/adversarial-fixed.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
