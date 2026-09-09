from pathlib import Path
import json,sys,subprocess
ROOT=Path('/home/blegoff/.odoo19-agents')
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import odoo_bench_native as native
variant=sys.argv[1];folder=BASE/('full-N03-'+variant)
command=native.native_command
native.native_command=lambda provider,config:command(provider,config)+['--max-budget-usd','12']
case=json.loads((ROOT/'benchmarks/native/cases/N03/case.json').read_text())
result=native.trial(folder,BASE/variant,case,'claude',{'model':'opus','effort':'medium','delegate':True},1200)
cleanup={}
if (folder/'environment.json').exists():
 identity=json.loads((folder/'environment.json').read_text())
 for kind in ('container','network','volume'):
  args=['docker',kind,'ls','-q','--filter','label=com.docker.compose.project='+identity['prefix']]
  if kind=='container':args.insert(3,'-a')
  check=subprocess.run(args,capture_output=True,text=True)
  cleanup[kind]={'returncode':check.returncode,'remaining':check.stdout.splitlines()}
(folder/'cleanup-independent.json').write_text(json.dumps(cleanup,indent=2)+'\n')
print(json.dumps({'status':result.get('status'),'oracle':result.get('oracle'),'cleanup':cleanup},ensure_ascii=False))
