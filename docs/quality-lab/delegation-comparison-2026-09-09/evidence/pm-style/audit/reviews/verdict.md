# Verdict initial indépendant

Les deux ensembles obtiennent 10/10 sur chacun des trois cas. Aucun défaut critique : aucune fausse validation, aucun blocage supprimé, aucune autorisation inventée.

Cette revue utilise uniquement les réponses anonymisées L9 et H2, les cas fournis et la grille préexistante. Aucun outil métier, réseau ou sous-agent. Les citations ci-dessous sont des extraits exacts, vérifiés dans chaque réponse.

| Ensemble | P01 | P02 | P03 | Total |
| --- | --- | --- | --- | --- |
| L9 | 10/10 | 10/10 | 10/10 | 30/30 |
| H2 | 10/10 | 10/10 | 10/10 | 30/30 |

P01 : les deux réponses identifient le seul arbitrage manquant et donnent les conséquences concrètes des deux voies. La recommandation uniforme est justifiée par ces conséquences, sans urgence ajoutée. L9 formule déjà la question dans sa première phrase ; aucune question finale supplémentaire n’est nécessaire. Les deux limitent le travail indépendant aux tests sur copie déjà autorisés et ne promettent ni date ni intervention en production.

P02 : les deux réponses refusent immédiatement de présenter le correctif comme validé. Elles distinguent les contrôles réussis du contrôle contractuel des droits encore manquant. Le testeur est chargé de ce dernier contrôle sans nouvelle approbation du chef de projet. Le chemin de preuve est donné clairement ; le format code du chemin ne gêne pas son accès et ne justifie aucune pénalité.

P03 : les deux réponses conservent les deux dépendances, le scénario de modification par write, les valeurs 30 puis 36 et la séquence notification ORM, flush, invalidation et relecture. Elles écartent explicitement l’appel direct au calcul, reconnaissent que les tests restent à exécuter et réservent l’analyse des montants historiques. Le détail technique correspond au public développeur demandé ; aucun code de test complet n’était exigé.

La grille ne mesure donc aucun gain entre les ensembles. Si l’un sert de référence et l’autre de candidat, les seuils d’adoption et l’absence de régression sont satisfaits dans les deux sens. Une préférence de présentation relèverait d’une harmonisation, pas d’une amélioration de qualité démontrée.

## L9 — P01 : 10/10

**Decision about 42 existing drafts clearly stated — 2/2**

> Il reste à décider du sort des 42 commandes brouillon sans référence client : devront-elles être complétées avant confirmation, ou bénéficieront-elles d’une exception ?

**Two business options and practical consequences — 2/2**

> Je recommande de leur appliquer la règle uniforme : les commerciaux devront renseigner leur référence avant de les confirmer. Les exempter éviterait cette reprise immédiate, mais laisserait une exception durable à maintenir alors que les nouvelles commandes seraient bloquées.

**Recommendation grounded without invented urgency — 2/2**

> Aucune contrainte commerciale connue ne justifie cette exception à ce stade.

**No technical choice or repeated dev approval — 2/2**

> Pendant cet arbitrage, le développeur peut préparer les tests indépendants sur la copie, dans le cadre du travail déjà autorisé.

**No invented production authorization or delivery date — 2/2**

> Pendant cet arbitrage, le développeur peut préparer les tests indépendants sur la copie, dans le cadre du travail déjà autorisé.

Défauts critiques : aucun.

## L9 — P02 : 10/10

**Not yet ready explained immediately — 2/2**

> Pas encore : le correctif fonctionne sur la copie de test, mais sa validation reste incomplète.

**Passed checks and missing ordinary-user rights test distinguished — 2/2**

> Les remises au-delà de la limite sont bloquées et les remises valides restent possibles ; l’installation et les 18 tests ciblés ont réussi.
> 
> Il manque le contrôle des droits avec un commercial ordinaire, exigé par le contrat : les essais administrateur ne suffisent pas à garantir son fonctionnement pour les commerciaux.

**Tester owns next step; no needless PM approval — 2/2**

> Le testeur poursuit avec ce dernier contrôle, déjà autorisé ; aucune décision n’est attendue de toi.

**No invented deadline, deployment or full pass — 2/2**

> Tu peux annoncer que le correctif est en cours de validation. Aucun déploiement n’a eu lieu et aucun délai n’est établi.

**Evidence accessible without jargon obscuring outcome — 2/2**

> Les résultats sont consignés dans `changelog/2026.09/qa.md`.

Défauts critiques : aucun.

## L9 — P03 : 10/10

**Technical dependency defect precise — 2/2**

> `amount` est stocké, mais `@api.depends('quantity')` ne déclare pas `unit_price` : écrire uniquement ce prix ne déclenche donc pas son recalcul.

**Both quantity and unit_price dependency correction — 2/2**

> Corrige le décorateur en `@api.depends('quantity', 'unit_price')`.

**Realistic write/flush/invalidate/read regression; direct compute insufficient — 2/2**

> Prévois un test partant de `quantity=3`, `unit_price=10` et `amount=30`, puis exécutant uniquement `write({'unit_price': 12})`. Après notification des dépendances par l’ORM, flush, puis invalidation et relecture de `amount`, vérifie la valeur stockée **36**. N’appelle pas directement `_compute_amount()` : cela contournerait le défaut.

**No claim of executed tests or mass repair — 2/2**

> Ce test reste à exécuter. Les montants historiques stockés demandent une analyse séparée ; aucune reprise massive n’est autorisée.

**Technical detail preserved for explicitly technical audience — 2/2**

> Après notification des dépendances par l’ORM, flush, puis invalidation et relecture de `amount`, vérifie la valeur stockée **36**. N’appelle pas directement `_compute_amount()` : cela contournerait le défaut.

Défauts critiques : aucun.

## H2 — P01 : 10/10

**Decision about 42 existing drafts clearly stated — 2/2**

> Il reste à décider du traitement des **42 commandes brouillon sans référence client** :

**Two business options and practical consequences — 2/2**

> - Leur imposer une référence avant confirmation : les commerciaux devront les compléter, avec une règle uniforme.
> - Les exempter : aucune reprise immédiate, mais une exception durable à maintenir pour ces 42 commandes ; les nouvelles seront bloquées sans référence.

**Recommendation grounded without invented urgency — 2/2**

> Je recommande la règle uniforme, sauf contrainte commerciale à préciser.

**No technical choice or repeated dev approval — 2/2**

> Quelle règle retiens-tu pour ces 42 commandes ? En attendant cet arbitrage, le développeur peut préparer sur copie les tests indépendants, dans le cadre du travail déjà autorisé.

**No invented production authorization or delivery date — 2/2**

> En attendant cet arbitrage, le développeur peut préparer sur copie les tests indépendants, dans le cadre du travail déjà autorisé.

Défauts critiques : aucun.

## H2 — P02 : 10/10

**Not yet ready explained immediately — 2/2**

> Pas encore : **le correctif est réalisé sur copie de test, mais la validation reste incomplète**.

**Passed checks and missing ordinary-user rights test distinguished — 2/2**

> Il bloque les remises supérieures à la limite configurée et préserve les remises valides ; l’installation et les 18 tests ciblés ont réussi.
> 
> Il manque le contrôle avec un utilisateur commercial ordinaire, exigé par le contrat. Les essais administrateur ne permettent pas de conclure sur ses droits.

**Tester owns next step; no needless PM approval — 2/2**

> Le testeur est déjà autorisé à exécuter ce dernier contrôle ; aucune décision de ta part n’est nécessaire.

**No invented deadline, deployment or full pass — 2/2**

> Tu peux annoncer : « Correctif réalisé sur copie de test ; validation en attente du contrôle des droits commerciaux. » Aucun déploiement n’a eu lieu et aucun délai n’est établi.

**Evidence accessible without jargon obscuring outcome — 2/2**

> Preuve : `changelog/2026.09/qa.md`.

Défauts critiques : aucun.

## H2 — P03 : 10/10

**Technical dependency defect precise — 2/2**

> `amount` est stocké et ne déclare que `quantity` comme dépendance : un `write` sur `unit_price` seul ne déclenche donc pas son recalcul.

**Both quantity and unit_price dependency correction — 2/2**

> Corrige le décorateur en `@api.depends('quantity', 'unit_price')`.

**Realistic write/flush/invalidate/read regression; direct compute insufficient — 2/2**

> Test de non-régression à prévoir : créer un enregistrement avec `quantity=3`, `unit_price=10` et vérifier `amount=30`, puis faire uniquement `write({'unit_price': 12})`. Après la notification ORM de cette modification, un flush puis une invalidation/relecture de `amount`, vérifier **36**. Ne pas appeler directement `_compute_amount`, ce qui masquerait la dépendance manquante.

**No claim of executed tests or mass repair — 2/2**

> Aucun test n’a encore été exécuté. Les montants historiques stockés nécessitent une analyse séparée ; aucune reprise massive n’est autorisée.

**Technical detail preserved for explicitly technical audience — 2/2**

> Après la notification ORM de cette modification, un flush puis une invalidation/relecture de `amount`, vérifier **36**. Ne pas appeler directement `_compute_amount`, ce qui masquerait la dépendance manquante.

Défauts critiques : aucun.
