# QA d'exécution de tâche — N-17, 19.0

Preuve réutilisée sans changement de code : green.json et green.log.
Commande réelle : /bridge/labctl qa lab_preparation --quick --tags /lab_preparation:TestLabPreparation.
RECETTE : install=ok update=ok, 0 failed, 0 error(s) of 9 tests, skipped=0 ; durée totale 7 s.
Neuf méthodes (les sous-tests augmentent le nombre d'assertions en échec du rouge). Tous les parcours A1–A5 sont joués : mélange draft automatique/manuels/done, zéro et 2.125 manuels, copy puis cron, reliquat positif puis deux crons, zéro/négatif sans création, singleton, petit solde 0.003, canal ir.cron.
Rouge métier confirmé avant correction : red-confirmed.log, 9 failed, 0 errors of 9 tests. red.json et red-confirmed.json décrivent volontairement le code initial et sont historiques, non preuves fraîches du correctif. L'erreur technique du premier test cron est documentée dans implementation.md.
Verdict : VALIDÉ. Trois warnings du pont/manifest préexistants (sans vue touchée), aucune erreur d'exécution. Pas de recette complète ni désinstallation, prévues à la clôture.
