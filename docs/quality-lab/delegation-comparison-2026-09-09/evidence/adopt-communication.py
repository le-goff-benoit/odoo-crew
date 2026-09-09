"""Apply the reviewed common instruction only after its signed decision exists."""
from pathlib import Path
import json,shutil
r=Path('/home/blegoff/.odoo19-agents');b=Path('/tmp/odoo-delegation-comparison-20260909')
assert all(x['status']=='finished' for x in json.loads((b/'run-ledger.json').read_text()))
decision=json.loads((b/'pm-style/decision.json').read_text());assert decision['status']=='adopted'
shutil.copy2(b/'pm-style/communication.md',r/'roles/communication.md')
p=r/'build.sh';s=p.read_text();needle='emit() {\n';assert s.count(needle)==1
s=s.replace(needle,'''# Corps commun aux agents, commandes et skills ; une seule source éditable.
emit_role_body() {
    cat "$HERE/roles/$1.md"
    printf '\\n'
    cat "$HERE/roles/communication.md"
}

emit() {
''');needle='cat "$HERE/roles/$role.md"';assert s.count(needle)==5;s=s.replace(needle,'emit_role_body "$role"');p.write_text(s)
p=r/'scripts/odoo_generated.py';s=p.read_text();needle='        body = (root / "roles" / f"{role}.md").read_text(encoding="utf-8")\n';assert s.count(needle)==1;s=s.replace(needle,needle+'        body += "\\n" + (root / "roles/communication.md").read_text(encoding="utf-8")\n');p.write_text(s)
print('Common communication instruction adopted in canonical sources; active generation still pending validation')
