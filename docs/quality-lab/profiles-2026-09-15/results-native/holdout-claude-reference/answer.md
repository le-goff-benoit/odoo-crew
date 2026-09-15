`/work/reception.json` est écrit et validé (JSON valide, toutes les citations vérifiées comme sous-chaînes exactes des pièces). Aucun autre fichier touché.

**Décision : reject** — les trois axes sont en échec.

- **Demande ↔ contrat** : la demande exclut les prêts, « même lorsqu'ils sont prolongés » ; C1 et C2 les placent dans le barème et facturent 2 CHF au septième jour. Le reste du contrat (barème société A, société B inchangée, périmètre local) est fidèle.
- **Contrat → preuves** : P1 n'atteste que deux locations de la société A (A7, A10) ; le sixième jour, les prêts et la société B sont déclarés non observés. C1, C3 et le volet « prêt » de C2 n'ont aucune observation — donc `local_scope_received: false`. Les deux succès techniques sont conservés dans `preserved_observations`, et je ne réclame pas de rejeu pour un dossier déclaré documentaire.
- **Sources → mémoire** : le draft perd l'exclusion des prêts, affirme un déploiement en production terminé et toutes les sociétés validées (contredit par la demande et par P1 — `deployment_verified: false`), et laisse tomber la contribution publiée par T04 sur le fuseau Europe/Zurich (`prior_memory_preserved: false`). Il transmet la conservation de la preuve au lieu du résultat reçu.

Limites consignées dans le fichier : mode documentaire uniquement, aucune exécution, aucun bundle donc ni hash ni empreinte de code — la fraîcheur et l'intégrité des pièces ne sont pas contrôlables ici.