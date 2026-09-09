# QA exécution — tentative 1

`runtime.json` et `runtime.log` : vraie installation Odoo 19.0 sur lab_qa, 14 s.
10 méthodes exécutées, zéro assertion échouée, 6 erreurs dans les sous-cas des deux tests de valeurs négatives.
Cause : tests attendant ValidationError alors que les contraintes SQL lèvent psycopg2.errors.CheckViolation dans un TransactionCase sans couche RPC. Le refus est effectif, mais l'assertion de type d'exception est incorrecte.
Les huit tests de calcul passent. C6 est rouge ; aucun verdict global vert possible.
Reprise demandée : utiliser l'exception SQL et la mise en silence ciblée du logger selon les précédents Odoo, puis rejouer lint et tests.
