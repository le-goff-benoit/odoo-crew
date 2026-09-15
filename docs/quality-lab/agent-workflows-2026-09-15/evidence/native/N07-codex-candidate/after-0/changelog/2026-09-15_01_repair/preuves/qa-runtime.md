# QA exécution — N-17

VALIDÉ, QA de tâche renforcée, Odoo 19.0, preuves développeur réutilisées sans rejouer le vert inchangé.
Tests-rouge.log : 14 assertions échouées, 0 erreur, 9 méthodes (sous-tests compris dans les échecs), 16 secondes. Les échecs portent les attentes N-17 et non des erreurs de chargement.
Tests-vert.json/log : 0 échec, 0 erreur, 9 tests, 0 ignoré ; RECETTE install=ok update=ok, 9 secondes. Le framework annonce 11 dans les statistiques de classe avec préparation/nettoyage ; 9 méthodes métier réellement exécutées.
A1 : test_cron_mixed_cohort_and_replay et test_cron_nonpositive_and_fractional_remaining, drafts automatiques/manuels, done manuels/automatiques, quantité négative ramenée à zéro, petites fractions.
A2 : test_manual_zero_then_cron et test_manual_nonzero_then_cron ; saisies zéro/non-zéro, sélection multiple de saisie.
A3 : test_duplicate_then_cron ; quatre combinaisons état/manual, source inchangée par copy, demande complète au cron.
A4 : test_remainder_then_cron et test_remainder_fractional ; reste, parent, source done préservée, cron et rejeu.
A5 : test_remainder_nonpositive et test_remainder_requires_singleton ; vide sans création/modification et singleton contrôlé par ValueError attendue.
Manifest sans author : avertissement préexistant. Pont : --without-demo all avertit en 19.0, Odoo applique True ; aucun module ignoré, aucune vue modifiée.
Aucun écran, droit nouveau ou canal RPC imposé par N-17. ORM réel et entrée _cron_prepare exercés ; aucune tâche ir.cron configurée dans la copie, aucune planification inventée. Aucun tour navigateur, désinstallation ou recette complète de release dans cette tâche.
