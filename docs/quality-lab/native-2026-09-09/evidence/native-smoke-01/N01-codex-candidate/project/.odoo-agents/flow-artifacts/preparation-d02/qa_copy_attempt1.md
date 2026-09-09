# QA copie synthétique — tentative 1

`update_attempt1.json/log` : mise à niveau réelle de lab_client réussie.
`seed_before.log` : quatre témoins créés avant changement, totaux 30/40/50/40.
`after_update_before_recompute.log` : totaux encore 30/40/50/40 après update ; nécessité de reprise prouvée.
`recompute_attempt1.log` puis `copy_check_attempt1.log` : reprise exécutée, quatre totaux persistés 30/52/62/40, mêmes noms/jours/tarifs/types.
Rejeu d'idempotence et nettoyage à terminer avec la QA finale après correction des tests négatifs. C7 partiellement validé à cette tentative ; pas de verdict global vert.
