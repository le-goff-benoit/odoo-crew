import json, sys, subprocess
from pathlib import Path
ROOT = Path('/home/blegoff/.odoo19-agents')
sys.path.insert(0, str(ROOT/'scripts'))
import odoo_bench_native as native
BASE=Path(__file__).resolve().parent
case=json.loads((ROOT/'benchmarks/native/cases'/sys.argv[1]/'case.json').read_text())
command=native.native_command
native.native_command=lambda provider, config: command(provider,config)+['--max-budget-usd','12']
folder=BASE/('complete-'+case['id']+'-replay')
result=native.trial(folder,BASE/'candidate',case,'claude',{'model':'opus','effort':'medium','delegate':False},900)
identity=json.loads((folder/'environment.json').read_text()) if (folder/'environment.json').exists() else None
cleanup={}
if identity:
 for kind in ('container','network','volume'):
  args=['docker',kind,'ls','--filter','label=com.docker.compose.project='+identity['prefix'],'-q']
  if kind=='container': args.insert(3,'-a')
  check=subprocess.run(args,capture_output=True,text=True)
  cleanup[kind]={'returncode':check.returncode,'remaining':check.stdout.splitlines()}
(folder/'cleanup-independent.json').write_text(json.dumps(cleanup,indent=2)+'\n')

print(json.dumps({'case':case['id'],'status':result.get('status'),'oracle':result.get('oracle')},ensure_ascii=False))
