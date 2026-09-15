Réception documentaire terminée. `/work/reception.json` écrit ; aucun autre fichier touché (les cinq pièces d'`input/` sont inchangées).

**Lectures mesurées via `/bridge/read-source`** : profil `odoo-tester.md`, puis les références qu'il désigne pour ce mandat — `docs/roles/qa-reception.md` (mode réception ; pas de bundle, donc `TASK_RECEPTION.md` écarté à raison) et `docs/DELIVERY_GUARD.md` pour cadrer ce que « déploiement vérifié » exigerait — puis les cinq pièces.

**Décision : accept**, les trois axes en accept.

- **Demande ↔ contrat** — toutes les obligations sont retrouvées avec leurs bornes et leurs négations : seuil du 7ᵉ jour inclus (C2 : 7 → 2 CHF, 10 → 8 CHF, cohérent avec 4 jours × 2 CHF), nullité au 6ᵉ (C1), exclusion des prêts *même prolongés* testée sur le cas prolongé (C3), société B hors changement (C4), périmètre local sans déploiement (C5). Les deux ajouts de la revue sont qualifiés plutôt qu'acceptés tacitement : le chiffre de 3 CHF en C4 est une concrétisation de la non-régression (conséquence justifiée, sous réserve qu'il s'agisse bien de la valeur antérieure) et C5 restreint au lieu d'élargir.
- **Contrat → preuves** — les cinq critères ont une observation attestée qui correspond sur société, opération et jour ; le critère composé C2 est couvert par ses **deux** conditions (A7 et A10), pas par une seule. C5 est satisfait par une négation explicite de l'attestation.
- **Sources → mémoire** — la contribution déjà publiée de T04 (fuseau Europe/Zurich) est reprise mot pour mot, sens et portée intacts ; l'entrée nouvelle transmet le **résultat reçu** et sa limite, pas seulement l'existence d'une preuve, et ne déborde pas du local vers le déployé.

`local_scope_received: true`, `prior_memory_preserved: true`, `deployment_verified: false`.

Portée de mon verdict, telle que consignée dans `limitations` : les cinq observations sont des **attestations reçues** sur une fixture synthétique déclarée documentaire — je juge leur portée et leur correspondance au contrat, je ne les ai ni rejouées ni présentées comme de nouvelles exécutions, et aucun test Odoo n'a été lancé. J'atteste donc la cohérence et la traçabilité du dossier, non une re-vérification indépendante du code. Aucune preuve `odoo-deployment-observation/1` n'est présente ni requise ici, et la valeur de référence de 3 CHF n'a pas de source antérieure jointe pour la recouper.