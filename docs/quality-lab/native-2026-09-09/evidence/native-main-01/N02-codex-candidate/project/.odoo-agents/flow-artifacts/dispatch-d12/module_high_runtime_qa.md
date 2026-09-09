# QA exécution sensible — lab_dispatch, 19.0, mode tâche
Commande : `/bridge/labctl qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate`, via odoo_evidence.py.
Preuve actuelle : changelog/2026-09-09_01_recalcul-fiable-des-brouillons/preuves/test-vert.json et .log.
RECETTE : install=ok, update=ok, 0 failed, 0 errors, 7 tests, 0 skipped, 4 secondes. Les tests ciblés constituent aussi la suite entière de ce petit module.
C1/C2/C3/C4/C7 verts ; idempotence sans write également testée. Preuve historique avant correction : test-rouge.json/.log (7 failed, 0 errors) ; son empreinte ancienne est volontaire et ne sert pas à valider le code final.
Avertissements non bloquants : author absent (dette préexistante), options du pont --without-demo all / http-interface. Aucune erreur de modèle ou de vue.
Pas de parcours navigateur : aucune vue, asset ou interaction graphique livrée. Tours et désinstallation relèvent de la clôture non demandée.
