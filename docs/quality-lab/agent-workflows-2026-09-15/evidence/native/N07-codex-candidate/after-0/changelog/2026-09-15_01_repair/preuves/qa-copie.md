# QA copie locale — N-17

VALIDÉ sur lab_client synthétique, Odoo 19.0. Aucun accès externe ni déploiement.
Update réellement exécuté : update.log, commande sortie 0, création/mise à jour des tables et module chargé. update.json conserve une classification failed due à --module utilisé à tort pour une commande sans tests ; son exit_code reste 0. Ce reçu n'est pas soumis comme test vert.
Reprise autorisée : reprise.py capturé par reprise.json et reprise.log. Avant : [999, 0, 2, 88] ; après : [7, 0, 2, 88]. Seul ID 1 modifié, aucun ID ajouté/supprimé. Lecture de tous les champs : seules prepared_qty et métadonnées d'écriture d'ID 1 peuvent varier ; IDs 2/3/4 intégralement préservés. Commit explicite réussi.
Nouveau processus : rejeu.py, rejeu.json et rejeu.log vérifient la persistance et le second cron ; tous les champs, write_date compris, restent identiques, toujours quatre lignes. Pas d'inférence sur des effets d'automatisations absentes de cette base.
Critère A6 entièrement couvert. Les parcours duplication/reliquat sont exercés sur la base QA dans TestPreparation, pas en ajoutant des lignes permanentes dans la cohorte.
