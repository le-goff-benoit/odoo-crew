from pathlib import Path
import shutil,json,hashlib
b=Path('/tmp/odoo-delegation-comparison-20260909');r=Path('/home/blegoff/.odoo19-agents');d=r/'docs/quality-lab/delegation-comparison-2026-09-09';e=d/'evidence'
def ignore(folder,names):
 p=Path(folder);return [n for n in names if n in ['.git','__pycache__'] or n.endswith('.pyc') or (p==b and n in ['distribution','design-native','design-metrics-summary.json']) or (p==b/'pm-style' and n=='native')]
shutil.copytree(b,e,ignore=ignore)
files={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(e.rglob('*')) if p.is_file()}
repo_paths=[*sorted((r/'benchmarks/delegation_comparison').rglob('*')),r/'roles/communication.md',r/'build.sh',r/'scripts/odoo_generated.py',r/'tests/test_odoo_generated.py',r/'tests/test_delegation_comparison_metrics.py',r/'.github/workflows/quality-lab.yml']
repository={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in repo_paths if p.is_file() and '__pycache__' not in p.parts}
(d/'EVIDENCE.json').write_text(json.dumps({'reference':'f6ea0b6851df5269dbec151bbdebe337d67707e8','files':files,'repository_files':repository,'scope':'Synthetic artifacts only. Native primary exports exclude incoming messages/reasoning; auxiliary exports metadata only. Historical absolute paths retained. Frozen original candidates remain unmodified.'},indent=2)+'\n')
print('Archived',len(files),'evidence files and',len(repository),'repository sources')
