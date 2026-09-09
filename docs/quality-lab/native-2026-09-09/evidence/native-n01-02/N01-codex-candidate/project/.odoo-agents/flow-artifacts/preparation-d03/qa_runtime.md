# QA exécution D-03 — VALIDÉ
Série 19.0, module lab_rental, mode tâche renforcée.
Installation fraîche sur lab_qa : runtime-install.json/log, -i lab_rental, TestPreparationFee 8/8, 0 erreur/échec/ignoré, 12 s.
Point de contrôle sur base chaude : runtime-update.json/log, --quick --update sans restriction de classe, suite complète du module (8 méthodes), -u exécuté.
D3-C1 à C4 couverts par les huit méthodes ; stockage vérifié après flush/invalidation pour toutes les valeurs. D3-C5 doit aussi être prouvé sur les témoins persistants par la voie copie.
Le rouge préalable runtime-red.json reste historique : nouveau barème contre ancien compute, 11 assertions en échec, puis mêmes tests verts après correction.
Tours et désinstallation non joués, réservés à la clôture ; aucun écran modifié.
