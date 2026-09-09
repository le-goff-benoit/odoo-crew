from pathlib import Path
import subprocess,sys,json,time,hashlib,uuid
ROOT=Path('/home/blegoff/.odoo19-agents');BASE=Path(__file__).resolve().parent;folder=BASE/'codex-N03'
sys.path.insert(0,str(ROOT/'scripts'))
import odoo_bench_native as n
# Cooperative boundary: every supplied shell command gets the same writable
# project/home and read-only candidate/sources; no provider credentials mounted.
command=n.sandbox(folder/'home',folder/'project',BASE/'candidate',folder/'bridge')
for relative in ['benchmarks','tests','docs/quality-lab']:
 command += ['--tmpfs',str(n.HOME_PATH/'.odoo19-agents'/relative)]
started=time.monotonic();p=subprocess.run(command+sys.argv[1:],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=n.provider_environment())
out=folder/'commands';out.mkdir(exist_ok=True);key=time.strftime('%H%M%S')+'-'+uuid.uuid4().hex[:8]
(out/(key+'.log')).write_text(p.stdout)
(out/(key+'.json')).write_text(json.dumps({'argv':sys.argv[1:],'exit_code':p.returncode,'seconds':round(time.monotonic()-started,2),'log':key+'.log','sha256':hashlib.sha256(p.stdout.encode()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print(p.stdout,end='');sys.exit(p.returncode)
