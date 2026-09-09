# QA copie sensible — lab_client synthétique, Odoo 19.0
Autorisation : demande utilisateur et LAB.md ; D-12 fait foi. Aucun accès hors pont du laboratoire.
Défaut reproduit sur les deux dossiers réels synthétiques avant correction puis rollback vérifié (defaut-copie.log). Mise à niveau réussie avec /bridge/labctl update, preuve update-copie.json/.log.
Reprise exacte : reprise/recalculate_drafts.py, deux exécutions dans deux shells distincts (reprise-1.json/.log, reprise-2.json/.log). Empreintes du module ET du script enregistrées.
Premier passage : seul id 1 LEGACY_DRAFT modifié, 999 → 20. id 2 LEGACY_DONE reste 777, write_date original conservé. Les états et les 4 lignes (write_date inclus) sont identiques.
Second passage : changed_ids=[], états/totaux/write_date/lignes identiques au premier résultat persisté.
Lecture finale dans une troisième session indépendante : lecture-finale.log. Vérification automatique des trois preuves et de l'inventaire initial : preuves/verify_idempotence.py, résultat preuves/idempotence.log, code 0.
Critères C5/C6 verts ; la copie reste corrigée, reprise commitée. Aucun test laissé en base ; aucun nouvel enregistrement. La QA de clôture n'a pas été exécutée, conformément au périmètre de la release ouverte.
