from coordinate import *
import shutil,hashlib
assert (I/'qa/result.md').is_file(), 'QA result required'
shutil.copytree(I/'qa',R/'preuves/qa',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
call('python3',PACK/'scripts/odoo_evidence.py','verify',R/'preuves/qa/verification.evidence.json')
for node,fragment in [('module_high_static_qa','static.md'),('module_high_runtime_qa','runtime.md'),('module_client_copy_qa','copy.md')]:complete(node,'done',R/'preuves/qa'/fragment,'codex-odoo-tester')
flow('status',F);claim('module_high_gate')
coverage=json.loads((R/'criteria.json').read_text())
notes=[
'AC01 : deux tests brouillon explicit/défaut et write ; assertions montant et quantité relues.',
'AC02 : borne 1 nouvelle et positif 3 initial, confirmation et montants 10/30.',
'AC03 : refus bouton puis relecture après savepoint.',
'AC04 : recordset positif puis nul, échec et conservation des deux lignes.',
'AC05 : create confirmé nul explicite/défaut refusés, quantité 1 acceptée.',
'AC06 : write état/quantité invalides, éditions simultanée et positive acceptées.',
'AC07 : load réel création et mise à jour .id, erreurs et conservation identité/valeurs.',
'AC08 : quatre tests initiaux conservés et négatifs nouveaux sous utilisateur interne.',
'AC09 : utilisateur interne non su ; ACL/vue identiques au baseline.',
'AC10 : contrôle QA SQL live des deux bases, IDs/valeurs identiques, contrainte validée seulement sur copie.',
'AC11 : aucun script de migration/réparation ; jeu initial valide conservé. Historique invalide non exercé.',
'AC12 : rouge/vert identiques, lint et update/tests réels vérifiés indépendamment ; preuves soumises à réception à cette porte. Publication mémoire et réception du plan sont obligations suivantes, non déclarées accomplies ici.'
]
for row,note in zip(coverage['criteria'],notes):
 row['status']='covered';row['note']=note
 names=['preuves/qa/result.md','preuves/qa/verification.evidence.json']
 row['evidence']=[{'path':(R/name).relative_to(P).as_posix(),'sha256':hashlib.sha256((R/name).read_bytes()).hexdigest()} for name in names]
(R/'criteria.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
flow('qa-report',F,'module_high_gate','--coverage',R/'criteria.json','--output',R/'qa.md','--outcome','pass','--owner',OWNER)
D=R/'reception';D.mkdir(exist_ok=True)
project=(P/'.odoo-agents/PROJECT.md').read_text()+'''\n## Résultat acquis de la tâche A\nLa règle persistante impose quantity > 0 pour state=confirmed, tout en autorisant zéro au brouillon et en conservant le refus des négatifs. Les canaux bouton, create, write et load ont été contrôlés, y compris confirmation groupée et utilisateur interne non superutilisateur.\nQA de tâche validée : mêmes 20 tests, 8 échecs métier sur le code initial puis 20/20 après correction ; 16 nouveaux tests et quatre anciens. La QA indépendante réutilise ces exécutions après contrôle de fraîcheur et vérifie directement images, schéma et conservation des trois lignes de chaque base.\nLa copie synthétique porte la nouvelle contrainte ; ordered_seed conserve le schéma initial. ACL, vue et version manifest 19.0.1.0.0 conservées. Aucun redressement historique.\nPortée : Odoo 19.0, données synthétiques valides ; pas de navigateur, recette complète, copie client ni qualification d’un historique invalide. Les réceptions et l’état opérationnel sont dans le plan de la release ; celle-ci reste ouverte.\n'''
journal=(P/'.odoo-agents/JOURNAL.md').read_text()+'''\n## 2026-09-09 — Quantité positive à la confirmation\nDemande : conserver zéro au brouillon et refuser les confirmés non positifs, par bouton et canaux ORM/import.\nFait : contrainte persistante ajoutée, négatifs toujours refusés, aucune modification de droits/vue ni réparation historique.\nVerdict acquis : QA de tâche VALIDÉE ; 8 échecs métier sur 20 au rouge puis mêmes 20/20 au vert, lint 0 erreur/avertissement.\nContrôle indépendant : tests relus et réutilisés, contrôle live des deux bases ; trois IDs et valeurs initiaux conservés, contrainte nouvelle uniquement sur copie.\nAppris : un contrôle neuf de fraîcheur/copie peut réutiliser les tests valables ; il ne constitue pas une nouvelle exécution de ces tests.\nPortée : copie synthétique Odoo 19.0, pas de données client ni d’historique invalide testé ; détails et réceptions dans la release.\nReste ouvert : release, recette complète et tâche C témoin non exécutée ; état des tâches dans plan.json.\n'''
(D/'PROJECT-propose.md').write_text(project);(D/'JOURNAL-propose.md').write_text(journal)
files=[R/'qa.md',R/'criteria.json',R/'preuves/qa/result.md',R/'preuves/qa/static.md',R/'preuves/qa/runtime.md',R/'preuves/qa/copy.md',R/'preuves/qa/verification.evidence.json',R/'preuves/qa/verification.evidence.log',R/'preuves/qa/verification.json',R/'preuves/developer/result.md',R/'preuves/developer/verification.json',R/'preuves/developer/lint.log']
files += list((R/'preuves/developer/red').glob('test-*.log'))+list((R/'preuves/developer/green').glob('test-*.log'))
args=['prepare-reception',F,'--source',R/'demande.md','--source',R/'consolidation-contrat.md','--spec',R/'revue_fonctionnelle.md','--scope','lab_qualification']
for file in files:args+=['--evidence',file]
args+=['--memory','.odoo-agents/PROJECT.md='+str(D/'PROJECT-propose.md'),'--memory','.odoo-agents/JOURNAL.md='+str(D/'JOURNAL-propose.md'),'--output',D/'bundle.json','--owner',OWNER]
flow(*args)
