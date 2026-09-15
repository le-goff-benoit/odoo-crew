import json, subprocess, tempfile, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(tempfile.mkdtemp(prefix='knowledge-eval-v2-20260915-'))
P=BASE/'project'; R=P/'changelog'/'shared-test'; R.mkdir(parents=True)
(BASE/'location.txt').write_text(str(BASE))
Path('/tmp/knowledge-evaluation-v2-location').write_text(str(BASE))
log=[]
def put(path,text):
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text)
def js(path,data): put(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def run(script,*args,expected=0):
 cmd=['python3',str(ROOT/'scripts'/script),*map(str,args)]
 p=subprocess.run(cmd,text=True,capture_output=True)
 record={'argv':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 log.append(record); js(BASE/'commands.json',log)
 print(script, args[0] if args else '',p.returncode,flush=True)
 if p.returncode!=expected: raise RuntimeError(record)
 return p.stdout
def ref(path):return {'path':str(path.relative_to(P)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def publish(id,kind,statement,source,task='T01',accepted=False,supersedes=None):
 row={'schema':1,'id':id,'kind':kind,'state':'accepted' if accepted else 'proposed','statement':statement,'author':'codex-evaluation','task':task,'scope':[],'sources':[ref(source)]}
 if accepted:row.update(reviewed_by='synthetic-business-owner',review=ref(source))
 if accepted and kind=='decision':row.update(affects_tasks=['T02'],impact_reason='Le fuseau modifie T02 ; T01 ne porte que sur les exclusions inter-sociétés, inchangées.')
 if supersedes:row['supersedes']=supersedes
 target=BASE/'fragments'/f'{id}.json';js(target,row)
 run('odoo_knowledge.py','publish',P,'--release','shared-test','--file',target)
 return row
def brief(task,name):
 target=R/'knowledge-readings'/f'{name}.json'
 run('odoo_knowledge.py','brief',P,'--release','shared-test','--task',task,'--role','analyst','--output',target)
 return target
put(R/'README.md','# Release synthétique ouverte\nÉvaluation documentaire uniquement.\n')
put(R/'demande.md','T01 : déterminer les exclusions du regroupement.\nT02 : établir la fenêtre de traitement.\nT03 : réunir les deux règles dans une note de décision.\n')
put(P/'.odoo-agents'/'config','series=19.0\n')
put(R/'pieces'/'regles.csv','type,regroupement\nclient,oui\ninter-societe,non\n')
put(R/'pieces'/'precision.md','# Précision métier synthétique\nLe terme « jour » reste ambigu entre UTC et Europe/Zurich.\n')
put(R/'pieces'/'decision-v1.md','# Arbitrage synthétique v1\nLe responsable métier retient Europe/Zurich pour T02 ; exclusion des inter-sociétés confirmée. T01 ne définit que les exclusions et reste indépendante du fuseau.\n')
tasks=[]
for t in ['T01','T02','T03']:
 put(P/'work'/t/'note.md',f'# {t}\nAnalyse documentaire synthétique.\n')
 tasks.append({'id':t,'title':f'Analyse documentaire {t}','request':'changelog/shared-test/demande.md','route':'standard','risk':'normal','acceptance':['La note cite les sources et distingue les questions des décisions.'],'scopes':[f'work/{t}'],'depends_on':['T01','T02'] if t=='T03' else []})
js(BASE/'definition.json',{'schema':1,'shared_memory':True,'tasks':tasks})
run('odoo_plan.py','init',R,'--file',BASE/'definition.json')
for name in ['regles.csv','precision.md']:
 run('odoo_documents.py',P,'--add',f'changelog/shared-test/pieces/{name}','--id',name.split('.')[0],'--version','1','--status','reference')
flows={}
for t in ['T01','T02']:
 output=run('odoo_plan.py','start',R,'--task',t); flows[t]=output.splitlines()[0]
js(BASE/'flows.json',flows)
publish('K01','discovery','Les livraisons inter-sociétés sont exclues du regroupement.',R/'pieces'/'regles.csv')
publish('K02','question','Le jour de traitement est-il UTC ou Europe/Zurich ?',R/'pieces'/'precision.md',task='T02')
early=brief('T02','T02-during-work')
publish('K03','decision','Le jour de traitement est Europe/Zurich ; les inter-sociétés restent exclues.',R/'pieces'/'decision-v1.md',task='T02',accepted=True,supersedes='K02')
run('odoo_knowledge.py','verify',P,'--file',early,expected=2)
print('BASE',BASE,flush=True)

flows=json.loads((BASE/'flows.json').read_text())
put(R/'briefing.md','# Briefing synthétique\nProjet fictif série 19.0. Aucun serveur/base/source Odoo consulté. Mission fonctionnelle documentaire.\n')
notes={'T01':'Les inter-sociétés sont exclues du regroupement (pieces/regles.csv, K01).','T02':'Le jour de traitement est Europe/Zurich, arbitrage K03 / decision-v1.md ; les inter-sociétés restent exclues.'}
for t in ['T01','T02']:
 put(P/'work'/t/'note.md',f'# {t}\n'+notes[t]+'\nAnalyse seule ; aucune modification ni livraison Odoo.\n')
 put(R/f'{t}-acceptance.md',f'# Réception documentaire {t}\n'+notes[t]+'\nCritère : source citée et question résolue par arbitrage synthétique.\n')
 put(R/f'{t}-memory.md',f'# Acquis {t}\n'+notes[t]+'\n')
 put(R/f'{t}-journal.md',f'{t} — Analyse documentaire sourcée réalisée dans une fixture, sans développement Odoo.\n')
 for node,outcome,evidence in [('briefing','development',R/'briefing.md'),('functional_review','answer',R/f'{t}-acceptance.md'),('journal_task','done',R/f'{t}-journal.md')]:
  run('odoo_flow.py','claim',flows[t],node,'--owner','codex-eval-orchestrator')
  run('odoo_flow.py','complete',flows[t],node,'--outcome',outcome,'--evidence',evidence,'--owner','codex-eval-orchestrator')
 run('odoo_evidence.py','run','--project',P,'--scope',f'work/{t}','--output',R/'proofs'/f'{t}.json','--environment','synthetic-documentary','--','python3','-c',f"from pathlib import Path; t=Path('work/{t}/note.md').read_text(); assert {notes[t]!r} in t; assert 'aucune modification' in t")

for t in ['T01','T02']:
 run('odoo_flow.py','claim',flows[t],'task_done','--owner','codex-eval-orchestrator')
 run('odoo_flow.py','complete',flows[t],'task_done','--outcome','done','--evidence',R/f'{t}-acceptance.md','--owner','codex-eval-orchestrator')
early2=brief('T02','T02-before-other-receipt')
for t in ['T01','T02']:
 knowledge=brief(t,f'{t}-final')
 if t=='T02':
  run('odoo_plan.py','finish',R,'--task',t,'--proof',f'changelog/shared-test/proofs/{t}.json','--acceptance',f'changelog/shared-test/{t}-acceptance.md','--memory',f'changelog/shared-test/{t}-memory.md','--knowledge',str(early2.relative_to(P)),expected=1)
 run('odoo_plan.py','finish',R,'--task',t,'--proof',f'changelog/shared-test/proofs/{t}.json','--acceptance',f'changelog/shared-test/{t}-acceptance.md','--memory',f'changelog/shared-test/{t}-memory.md','--knowledge',str(knowledge.relative_to(P)))

def snapshot(label):
 output=run('odoo_plan.py','status',R)
 put(BASE/'states'/f'{label}.txt',output)
 brief('T03',label)
snapshot('01-before-new-decision')
put(R/'pieces'/'decision-v2.md','# Arbitrage métier synthétique v2\nPour T02, remplacer Europe/Zurich par UTC. T02 est reportée puis devra être reprise et réceptionnée. T01 décrit seulement les exclusions inter-sociétés : inchangées, sans reprise. T03 attend les acquis courants de T01 et T02.\n')
publish('K04','decision','Le jour de traitement est désormais UTC ; T02 doit être reprise, les exclusions inter-sociétés T01 restent inchangées.',R/'pieces'/'decision-v2.md',task='T02',accepted=True,supersedes='K03')
snapshot('02-after-new-decision')
run('odoo_knowledge.py','verify',P,'--file',R/'knowledge-readings/01-before-new-decision.json',expected=2)
run('odoo_plan.py','start',R,'--task','T03',expected=1)
run('odoo_plan.py','defer',R,'--task','T02','--reason','Arbitrage métier v2 : report T02, fenêtre UTC à reprendre ; T01 inchangée.')
snapshot('03-after-defer')
run('odoo_plan.py','reopen',R,'--task','T02','--reason','Reprise explicitement prévue par pieces/decision-v2.md, remplacement du fuseau par UTC.')
snapshot('04-after-reopen')
output=run('odoo_plan.py','start',R,'--task','T02'); newflow=output.splitlines()[0]
snapshot('05-restart-T02')
put(P/'work/T02/note.md','# T02 reprise\nFenêtre UTC selon K04 et pieces/decision-v2.md. Les inter-sociétés restent exclues (T01/K01 inchangées). Analyse documentaire seule, aucune livraison Odoo.\n')
put(R/'T02-v2-acceptance.md','# Réception T02 v2\nLa note respecte UTC, conserve l’exclusion inter-sociétés et cite K04.\n')
put(R/'T02-v2-memory.md','# Acquis T02 v2\nFenêtre UTC selon K04 et decision-v2.md ; les inter-sociétés restent exclues selon T01/K01. Aucun déploiement.\n')
put(R/'T02-v2-journal.md','T02 reprise documentaire réceptionnée selon arbitrage v2.\n')
for node,outcome,evidence in [('briefing','development',R/'briefing.md'),('functional_review','answer',R/'T02-v2-acceptance.md'),('journal_task','done',R/'T02-v2-journal.md'),('task_done','done',R/'T02-v2-acceptance.md')]:
 run('odoo_flow.py','claim',newflow,node,'--owner','codex-eval-orchestrator')
 run('odoo_flow.py','complete',newflow,node,'--outcome',outcome,'--evidence',evidence,'--owner','codex-eval-orchestrator')
run('odoo_evidence.py','run','--project',P,'--scope','work/T02','--output',R/'proofs/T02-v2.json','--environment','synthetic-documentary','--','python3','-c',"from pathlib import Path; t=Path('work/T02/note.md').read_text(); assert 'Fenêtre UTC' in t; assert 'inter-sociétés restent exclues' in t; assert 'Europe/Zurich' not in t")
reading=brief('T02','T02-v2-final')
run('odoo_plan.py','finish',R,'--task','T02','--proof','changelog/shared-test/proofs/T02-v2.json','--acceptance','changelog/shared-test/T02-v2-acceptance.md','--memory','changelog/shared-test/T02-v2-memory.md','--knowledge',str(reading.relative_to(P)))
snapshot('06-after-new-receipt')
run('odoo_plan.py','start',R,'--task','T03')
snapshot('07-T03-started')
# Passation seule : les sources décrivent les règles et le besoin restant, sans état d’exécution.
Q=BASE/'handoff-only'; S=Q/'changelog'/'handoff'
put(S/'README.md','# Passation documentaire synthétique, sans plan\n')
put(S/'demande.md','# Demande brute du responsable métier\nD01 a préparé les exclusions de regroupement : les inter-sociétés sont exclues. La prochaine tâche D02 devra vérifier la fenêtre UTC avant toute application. Aucun ordre de démarrage ni compte rendu d’exécution D02 n’est présent dans cette passation.\n')
put(S/'decision.md','# Arbitrage brut confirmé\nRetenir UTC pour la règle de jour. Conserver l’exclusion inter-sociétés. Cet arbitrage fixe la règle ; il ne déclare pas D02 exécutée, réceptionnée, disponible dans un planning ou déployée.\n')
put(S/'passation.md','# Passation de D01\nLa règle d’exclusion est décrite. D02 est la prochaine tâche nommée dans la demande. Son état d’exécution n’a pas été transmis. Lire la demande et l’arbitrage UTC.\n')
def qref(path):return {'path':str(path.relative_to(Q)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
row={'schema':1,'id':'H01','kind':'decision','state':'accepted','statement':'UTC retenu ; les inter-sociétés restent exclues.','author':'synthetic-owner','scope':[],'sources':[qref(S/'decision.md')],'reviewed_by':'synthetic-owner','review':qref(S/'decision.md')}
js(BASE/'fragments/H01.json',row)
run('odoo_knowledge.py','publish',Q,'--release','handoff','--file',BASE/'fragments/H01.json')
for name in ['demande.md','passation.md']:
 run('odoo_documents.py',Q,'--add',f'changelog/handoff/{name}','--id',name.split('.')[0],'--version','1','--status','reference')
run('odoo_knowledge.py','brief',Q,'--release','handoff','--task','D02','--role','analyst','--output',BASE/'handoff-D02-reading.json')
run('odoo_knowledge.py','verify',Q,'--file',BASE/'handoff-D02-reading.json')
run('odoo_context.py',Q,'--release','handoff','--task','D02','--role','analyst','--query','fenêtre UTC')
print('COMPLETE',BASE)
