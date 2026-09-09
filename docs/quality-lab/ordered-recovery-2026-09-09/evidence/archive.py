from pathlib import Path
import json,shutil,hashlib
B=Path('/tmp/odoo-ordered-recovery-20260909'); R=Path('/home/blegoff/.odoo19-agents/docs/quality-lab/ordered-recovery-2026-09-09'); E=R/'evidence';E.mkdir(parents=True,exist_ok=True)
exclude={'.git','__pycache__','dist'}
def copytree(src,dst):
 for p in src.rglob('*'):
  if not p.is_file() or any(part in exclude for part in p.relative_to(src).parts) or p.suffix=='.pyc':continue
  q=dst/p.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ['O01','O02','O03','audit','corpus-review','corpus/amendment','native-final','integration']:
 if (B/name).exists():copytree(B/name,E/name)
for name in ['protocol.json','candidate-manifest.json','odoo-request.md','trace-provenance.json','root-barriers-native.jsonl','root-barriers-native.manifest.json','calibration-final.json','ci-calibration.log','unit-tests.log','build-isolated.log','parity-isolated.log','build-active.log','parity-active.log','metrics.json','metrics.py','coordinate.py','export-native.py','export-native-v1.py','export-spawn.py','archive.py']:
 if (B/name).is_file():shutil.copy2(B/name,E/name)
files={p.relative_to(E).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(E.rglob('*')) if p.is_file()}
(R/'EVIDENCE.json').write_text(json.dumps({'format':'quality-lab-evidence/1','reference':'c19e80540917709e1c8d59325a696aa27a7fc5ce','policy':'Synthetic local task and allowlisted native records only; no full session, incoming messages, system/developer messages or assistant analysis exported. Historical absolute paths identify original runs; archive integrity checked by this relative manifest. No client data or credentials. Public synthetic PostgreSQL password retained for reproducibility.','files':files},ensure_ascii=False,indent=2)+'\n');print(len(files),'files',sum(x['bytes'] for x in files.values()),'bytes')
