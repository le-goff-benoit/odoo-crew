from pathlib import Path
import json,sys,threading,time,subprocess
ROOT=Path('/home/blegoff/.odoo19-agents');BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import odoo_bench_native as n
folder=BASE/'codex-N03';folder.mkdir()
project=folder/'project';n.copy_project(ROOT/'benchmarks/native/cases/N03/project',project)
home=folder/'home';home.mkdir();bridge=folder/'bridge';bridge.mkdir()
(bridge/'labctl').write_text(n.CLIENT);(bridge/'labctl').chmod(0o755)
pack=BASE/'candidate'
for args in [['git','init','-q',str(project)],['git','-C',str(project),'add','.'],['git','-C',str(project),'-c','user.name=Quality Lab','-c','user.email=lab@example.invalid','commit','-qm','Dossier synthétique initial']]:n.execute(args).check_returncode()
built=n.execute(n.sandbox(home,project,pack)+['bash',str(n.HOME_PATH/'.odoo19-agents/build.sh')],env=n.provider_environment());(folder/'build.log').write_text(built.stdout);built.check_returncode()
case=json.loads((ROOT/'benchmarks/native/cases/N03/case.json').read_text());lab=n.Lab(folder,pack,project,case);server=None
try:
 lab.start();server=n.Bridge(str(bridge/'control.sock'),n.Handler);server.lab=lab;threading.Thread(target=server.serve_forever,daemon=True).start()
 (project/'demande-originale.md').write_text(case['request']+'\n')
 (project/'LAB.md').write_text('''# Laboratoire synthétique Odoo 19.0
Exécute la demande originale jusqu'au résultat prévu par /odoo-new, avec le vrai graphe et les profils figés du référentiel monté dans le sandbox. Projet /work modifiable, sources et référentiel en lecture seule. Aucun accès à un client ou une production. Toutes les écritures sur cette copie synthétique sont autorisées. Studio est installé, aucun module custom, aucun écran à modifier.

Toutes les commandes du projet se jouent par le wrapper hôte :
python3 /tmp/odoo-fidelity-20260909/codex_control.py bash -lc '<commande dans /work>'
Il monte le projet à /work et le référentiel à ~/.odoo19-agents, crée un /tmp privé à chaque appel et conserve les fichiers du projet et du home entre les appels. Ne stocke donc aucune preuve dans /tmp. Ne démarre pas Docker ou une autre stack. /bridge/labctl shell FICHIER.py permet un shell Odoo sur lab_client (env disponible, commit explicite pour conserver les écritures). Les appels Studio passent par les vrais scripts odoo_pack.py et XML-RPC. Les champs initiaux portent les XML-ID studio_customization.lab_seed_*.

Délègue les voies QA indépendantes à de vrais sous-agents dans une même vague quand les verrous sont compatibles. L'orchestrateur seul pilote le flow et fusionne les preuves ; les enfants écrivent des fragments isolés et ne délèguent pas. Les autres agents partagent le projet : aucun écrasement du travail d'autrui. Donne à chaque enfant son périmètre et ce wrapper. Utilise au plus deux enfants simultanés afin de conserver le slot du superviseur ; au plus huit enfants dans tout ce run.

'''+'RPC local : '+lab.url+', base lab_client, admin/admin (identifiants jetables du banc).\n')
 n.atomic_json(folder/'state.json',{'status':'ready','mode':'codex_collaboration_cooperative','url':lab.url,'started_at':n.now(),'deadline_seconds':1800})
 deadline=time.monotonic()+1800
 while not (folder/'finish.request').exists() and time.monotonic()<deadline:time.sleep(1)
 result=lab.oracle();n.atomic_json(folder/'oracle.json',result)
 n.atomic_json(folder/'state.json',{'status':'closed','reason':'requested' if (folder/'finish.request').exists() else 'deadline','oracle':result})
finally:
 if server:server.shutdown();server.server_close()
 lab.close()
 cleanup={}
 for kind in ['container','network','volume']:
  args=['docker',kind,'ls','-q','--filter','label=com.docker.compose.project='+lab.prefix]
  if kind=='container':args.insert(3,'-a')
  p=subprocess.run(args,text=True,capture_output=True);cleanup[kind]={'returncode':p.returncode,'remaining':p.stdout.splitlines()}
 n.atomic_json(folder/'cleanup.json',cleanup)
