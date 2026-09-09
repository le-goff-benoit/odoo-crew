from coordinate import *
import hashlib
D=R/'reception';review=json.loads((D/'review.json').read_text())
assert review['verdict']=='pass' and review['mode']=='independent'
flow('complete',F,'module_high_gate','--owner',OWNER,'--outcome','pass','--evidence',R/'qa.md','--evidence',R/'criteria.json','--evidence',D/'review.json')
flow('status',F);claim('journal_task')
publication=flow('publish-memory',F,'--owner',OWNER)
(R/'publication.md').write_text('# Publication exacte des mémoires\n\nCommande publique publish-memory sous revendication journal_task. Résultat réel :\n\n```text\n'+publication+'```\n')
bundle=json.loads((D/'bundle.json').read_text())
for item in bundle['memory']:
 assert hashlib.sha256((P/item['target']).read_bytes()).hexdigest()==item['draft']['sha256']
complete('journal_task','done',R/'publication.md');claim('task_done');complete('task_done','done',R/'publication.md')
(R/'reception-plan-A.md').write_text('# Réception de A\n\nLes 12 obligations sont satisfaites dans leur ordre : analyse figée, code et mêmes attentes rouge/vert, QA indépendante, réception documentaire indépendante positive, publication exacte des deux drafts puis flow terminé. Les 20 tests sont ceux du développeur, réutilisés par la QA après revue et 88 contrôles neufs de fraîcheur/copie. Aucun nouveau test Odoo en QA.\n\nPortée : Odoo 19.0, copie synthétique restaurée et jeu initial valide. Aucun historique invalide, navigateur, recette complète ni déploiement qualifié. Release ouverte ; C demeure un témoin de disponibilité non exécuté.\n')
(R/'consolidation-A.md').write_text('# Consolidation de A\n\nPROJECT et JOURNAL ont été publiés par l’API et sont identiques aux drafts reçus. Ils transmettent zéro au brouillon, positivité persistante des confirmés, canaux/imports/atomicité/droits conservés, succès acquis 20/20 après 8 échecs rouges et validation indépendante de copie. Les limites synthétiques/19.0/backend et l’absence de réparation historique restent explicites. La preuve exacte de publication est publication.md ; le détail de réception est reception/review.json.\n')
call('python3',PACK/'scripts/odoo_plan.py','finish',R,'--task','A','--proof',(R/'preuves/qa/verification.evidence.json').relative_to(P),'--acceptance',(R/'reception-plan-A.md').relative_to(P),'--memory',(R/'consolidation-A.md').relative_to(P))
call('bash',PACK/'scripts/odoo-release.sh','done',R,'1','QA validée : 20/20 tests réutilisés après revue indépendante, 88 contrôles QA neufs, réception et mémoire publiées')
status=call('python3',PACK/'scripts/odoo_plan.py','status',R);(I/'plan-final.txt').write_text(status)
plan=json.loads((R/'plan.json').read_text());tasks={t['id']:t for t in plan['tasks']};assert tasks['A'].get('receipt') and not tasks['C'].get('attempts')
state=json.loads(F.read_text());assert state['status']=='complete' and not state['claims'];assert not json.loads((F.parent/'resource-locks.json').read_text())['claims']
assert '<!-- release ouverte -->' in (R/'README.md').read_text()
(I/'completion.json').write_text(json.dumps({'flow':str(F),'status':state['status'],'claims':state['claims'],'accepted_reception':state['accepted_reception'],'memory_exact':True,'release_open':True,'plan_status':status,'no_new_odoo_tests_in_qa':True,'task_C_not_executed':True},ensure_ascii=False,indent=2)+'\n')
