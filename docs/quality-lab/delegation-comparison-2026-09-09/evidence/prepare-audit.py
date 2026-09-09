from pathlib import Path
import json,shutil,hashlib,datetime
b=Path('/tmp/odoo-delegation-comparison-20260909');r=Path('/home/blegoff/.odoo19-agents')
rows=json.loads((b/'run-ledger.json').read_text());assert len(rows)==6 and all(x['status']=='finished' for x in rows)
a=b/'audit';a.mkdir()
mapping={'Q7':'E01-S','V4':'E01-D','M8':'E02-S','R3':'E02-D','K6':'E03-S','Z2':'E03-D'}
(b/'audit-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
for label,run in mapping.items():
 src=b/'snapshots'/run;dst=a/label;dst.mkdir()
 for name in ['project','pieces']:
  if (src/name).exists():shutil.copytree(src/name,dst/name)
 for name in ['demande.md','task.md']:
  if (src/name).exists():shutil.copy2(src/name,dst/name)
 (dst/'output').mkdir()
 for name in ['analyse.md','diagnostic.md','qa.md','PROJECT.md','JOURNAL.md','result.md']:
  if (src/'output'/name).exists():shutil.copy2(src/'output'/name,dst/'output'/name)
 shutil.copy2(r/'benchmarks/delegation_comparison/cases'/run[:3]/'private/rubric.json',dst/'rubric.json')
 (dst/'identity.json').write_text(json.dumps({'label':label,'case':run[:3]})+'\n')
shutil.copy2(b/'communication-rubric.json',a/'communication-rubric.json')
(a/'reviews').mkdir()
(a/'instructions.md').write_text('''Tu es le relecteur indépendant de six réponses Odoo identifiées Q7,V4,M8,R3,K6,Z2. Tu ne connais pas leur organisation et ne dois pas chercher à la déduire. Aucun accès aux autres dossiers de campagne, métriques, variantes ou traces natives. Pas de délégation, pas de modification de code, pas de test runtime. Avant lecture de code Odoo, exécute le briefing offline pour le projet fourni avec le script /home/blegoff/.odoo19-agents/scripts/odoo_briefing.py ; sources 19.0 en lecture seule si utile.

Pour chaque dossier, confronte demande, pièces, projet initial (dans corpus public de référence indiqué ci-dessous uniquement) et livrables. Le projet du dossier est la sortie du candidat, pas nécessairement l'initial. Les rubriques préexistent aux réponses. Ne remplace pas la vérification sémantique par des mots-clés. Vérifie les citations déterminantes et la conservation des décisions/mémoire. L'exécution Odoo E03 sera contrôlée séparément par l'orchestrateur ; ici évalue le code, les tests fournis et l'honnêteté du rapport, en marquant les affirmations runtime à vérifier. Ne refuse pas mécaniquement un E03 en attendant cet audit runtime, mais n'atteste pas son exécution.

Écris reviews/LABEL.json : {case,reviewer,independent:true,checks:[{id,pass,evidence}],score:{business:0..4,coverage:0..2,evidence:0..2,useful_synthesis:0..2,total:0..10},critical_issues:[],pm:{criteria:[{criterion,score:0|1|2|null,evidence}],total,max},runtime_claims_to_verify:[]}.
Les checks doivent reprendre tous et seulement les IDs de rubric.json. Les preuves citent fichier et extrait exact. Une question inutile ou un jargon gênant se note honnêtement ; question qualité N/A quand aucune décision n'est nécessaire. Conserve les observations négatives sans proposer de réparer les sorties. Écris aussi reviews/synthesis.md, sans comparaison d'organisation. Aucun autre fichier écrit. Budget 15 minutes.

Corpus public initial autorisé pour comparaison : /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/cases/E01/public, E02/public, E03/public. Seuls ces dossiers publics, les dossiers d'audit et les sources Odoo/référentiel nécessaires sont autorisés. Ne lis pas les oracles privés autres que les rubriques fournies.
''')
(a/'INPUTS.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{str(p.relative_to(a)):hashlib.sha256(p.read_bytes()).hexdigest() for p in a.rglob('*') if p.is_file()}},indent=2)+'\n')
print('Independent audit packets ready')
