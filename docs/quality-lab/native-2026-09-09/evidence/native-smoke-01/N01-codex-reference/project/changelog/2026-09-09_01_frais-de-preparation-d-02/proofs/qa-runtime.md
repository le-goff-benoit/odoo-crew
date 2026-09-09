# QA exécution — VALIDÉ

Codex testeur · lab_rental · 19.0 (manifest) · QA de tâche.
Commande concluante : `/bridge/labctl qa lab_rental --update --tags /lab_rental:TestPreparationFee`.
Preuve : `qa-install-update.log`, code retour 0 ; installation 3 s, update 4 s, tests 4 s (11 s total).
Résultat Odoo réel : 7 tests, 0 échec, 0 erreur, 0 ignoré ; les sept méthodes TestPreparationFee apparaissent dans le log.
C1–C5 couverts. Pas de parcours navigateur puisque aucun écran modifié.
Réserve préexistante : manifest sans author, avertissement répété 8 fois dans les 3 chargements (manifest inchangé, déjà présent dans la base git).

Les appels `--quick` puis `--quick --fresh --no-template` ont été écartés : zéro test, module non installé. Le script teste l'existence de la base pour choisir `-u`, pas l'état d'installation du module. L'installation explicite via le même pont résout le problème sans modifier le dispositif.
Candidate odoo-feedback : exiger un nombre de tests non nul et choisir -i/-u d'après l'état du module ; ne pas considérer `0 failed ... of 0 tests` comme validation.
