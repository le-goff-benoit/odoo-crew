Le premier témoin a effectivement refusé les accès étrangers en XML-RPC, avec
`faultCode = 4`, mais l'oracle cherchait à tort le nom Python de l'exception
dans le message. Le transport `/xmlrpc/2` de la source 19.0
`addons/rpc/controllers/xmlrpc.py`, lignes 28 et 37–38, transforme explicitement
`AccessError` en code 4 avec `str(e)` seul.

Correction factuelle de l'oracle : code 4 et message non vide. Les réponses
originales sont conservées, puis réévaluées sans appel Odoo. Aucun changement
de règle, de droits ni de contrat. Un nouveau run du témoin et du mutant porte
le total à trois variantes exécutées, dans le budget fixé.
