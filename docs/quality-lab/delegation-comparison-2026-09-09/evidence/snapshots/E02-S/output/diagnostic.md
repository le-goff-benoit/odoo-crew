# SYN-42 — Diagnostic support, série 19.0

## Verdict et périmètre de preuve

**Bug custom : dépendance `unit_price` absente du calcul stocké `amount`.** La cause est étayée par le code fourni, les sources locales Odoo 19.0 et une trace synthétique indépendante. Il ne s'agit ni d'un défaut de multiplication ni d'une demande de changer la règle de gratuité.

Aucune exécution Odoo, aucun accès client, aucune reproduction sur base réelle, aucun correctif et aucune réparation de données n'ont été effectués. Le test rouge ci-dessous est proposé, non exécuté. La trace a été fournie avec le cas ; elle n'a pas été produite pendant cette intervention.

## Demande conservée

> Le montant reste à 30 quand je passe le prix de 10 à 12 pour une quantité de 3. C'est apparu après notre modification du calcul stocké. Merci de diagnostiquer, proposer un contournement et préparer la suite, sans modifier le module ni réparer de données pour l'instant. Nous vendons aussi des lignes gratuites ; il faut les conserver.

Original inchangé : [demande.md](../demande.md).

## Chaîne de preuves

| Pièce consultée | Constat | Portée |
| --- | --- | --- |
| Briefing exécuté avec `--offline` | Série 19.0 ; aucune instance déclarée ; aucune release ouverte | Aucun état déployé vérifié |
| [Manifest](../project/lab_qualification/__manifest__.py) | Version locale `19.0.1.0.0` | Version de dépôt uniquement |
| [models.py](../project/lab_qualification/models.py), lignes 9–11 et 20–23 | `amount` est stocké ; calcul `quantity * unit_price` ; `@api.depends` ne déclare que `quantity` | La modification du prix seul ne déclare pas le montant à recalculer |
| `/home/blegoff/odoo-sources/19.0/odoo/orm/decorators.py:244` | `depends` conserve les dépendances dans `_depends` | Mécanisme standard de la série cible |
| `/home/blegoff/odoo-sources/19.0/odoo/orm/fields.py:561` | `get_depends` collecte les dépendances de la méthode de calcul | Le framework ne déduit pas celles-ci de la multiplication |
| `/home/blegoff/odoo-sources/19.0/odoo/orm/models.py:6754` | `modified` prépare le recalcul des champs stockés dépendants | Cohérent avec un déclencheur manquant |
| [Trace fournie](../pieces/orm-trace.jsonl), séquences 1–3 | Création à 3 × 10 : 30 ; prix seul à 12 : 30 ; écriture explicite de quantité 3 : 36 | Valeurs annoncées après flush et relecture, dans un scénario synthétique |
| [Décisions](../pieces/decisions.md), D-17 ; trace séquence 4 | Ligne gratuite confirmée, quantité 2, prix 0, montant 0 | Gratuité voulue et approuvée, sans nouvel arbitrage |
| [Vue](../project/lab_qualification/views/quantity.xml) | Affichage direct des champs ; bouton de confirmation existant | Aucun calcul d'affichage distinct dans la vue fournie |

La pièce [dependencies-source.md](../pieces/dependencies-source.md) a servi de piste ; la définition de `depends` a aussi été lue directement dans les sources locales.

## Pistes et impact

- Données : la trace décrit des entrées cohérentes. Le montant devient périmé après une écriture du prix ; ce n'est pas la preuve d'une erreur de saisie. Des montants déjà stockés peuvent rester faux.
- Usage : changer le prix sans changer la quantité est un parcours légitime. Une ligne offerte n'est pas une erreur d'usage.
- Configuration ou droits : aucun blocage d'écriture dans la trace ; le prix passe bien à 12. Aucune configuration de base réelle n'a été inspectée, donc aucune exclusion globale de cette piste chez un client.
- Code custom : omission concrète dans les dépendances, cohérente avec la trace ; cause retenue pour le matériel fourni.
- Standard : le fonctionnement documenté des dépendances explique le symptôme ; aucun élément n'étaye un bug standard.
- Déploiement : version réellement installée et date d'apparition inconnues. Le lien temporel avec la modification du calcul vient du ticket, pas d'un historique vérifié.

Impact démontré : **une ligne synthétique incohérente, SYN-42-L7**, montant 30 au lieu de 36, soit un écart de −6. Une seconde ligne synthétique, FREE-2, illustre une gratuité valide. Nombre d'enregistrements clients et d'utilisateurs touchés : inconnu. Durée et éventuelles conséquences sur des documents commerciaux ou comptables : non établies. Le modèle fourni ne prouve aucune liaison à la facturation.

Gravité retenue pour le scénario : **bloquant pour l'utilisation fiable du montant**, car une valeur stockée est fausse. Le périmètre réel reste à mesurer avant de chiffrer l'impact client.

## Contournement proposé, sans exécution

Immédiatement, contrôler le montant par quantité × prix après tout changement de prix et suspendre l'utilisation des lignes incohérentes dans les documents ou décisions qui reposent sur ce montant. Cette mesure ne modifie aucune donnée.

La séquence 3 fournit une piste technique : une écriture ORM explicite de la quantité inchangée déclenche le recalcul. Un technicien pourra l'essayer sur une copie autorisée, avec contrôle avant/après. Ce n'est pas une réparation effectuée ni une consigne d'écriture en production. Ressaisir la même quantité dans l'écran peut ne rien envoyer au serveur ; un simple rafraîchissement n'est pas un recalcul. Éviter de faire varier artificiellement la quantité sur une ligne confirmée sans examiner ses effets métier.

## Test rouge proposé — non exécuté

À implémenter ensuite dans un test transactionnel Odoo 19.0, par le développeur. Ne pas appeler directement `_compute_amount` : cela masquerait l'absence du déclencheur.

1. Créer une ligne nommée `SYN-42-L7`, quantité 3, prix 10, puis la confirmer par `action_confirm`.
2. Flusher les écritures et calculs, invalider le cache des champs contrôlés, relire par l'ORM. Vérifier état confirmé et montant 30.
3. Écrire **uniquement** `unit_price = 12`, sans réécrire la quantité.
4. Flusher, invalider le cache et relire. Vérifier quantité 3, prix 12, état confirmé et **montant 36**. Le défaut fourni laisse 30 selon la trace : c'est l'échec attendu, pas un échec exécuté pendant cette épreuve.
5. Garder ce scénario en non-régression après correction ; vérifier aussi qu'un changement de quantité à 4 donne 48.

Tests complémentaires à préparer pour préserver les décisions :

- Créer une ligne nommée `FREE-2`, quantité 2, prix 0 ; la confirmer ; après flush et relecture, montant 0 et état confirmé, sans exception.
- Sur une ligne payante confirmée, passer uniquement le prix à 0 ; après flush et relecture, attendre montant 0 et confirmation conservée. Couvrir aussi le retour à un prix positif.
- Conserver la quantité zéro en brouillon et le refus des quantités négatives ; ne pas imposer un prix strictement positif ni une interdiction de confirmer à prix zéro.

## Suite préparée et responsabilités

Le développeur doit d'abord exécuter le test proposé sur une base locale autorisée et consigner son résultat rouge. La reprise de développement `/odoo-new` n'est pas engagée ici ; aucune porte de passage fondée sur un test exécuté n'est réputée franchie.

La correction attendue, sans l'appliquer ici, est de déclarer tous les champs effectivement lus par le calcul, dont le prix, tout en gardant le calcul stocké et la gratuité D-17. Critère de réception : changement de prix seul correctement persisté après flush/relecture, changement de quantité toujours pris en compte, lignes gratuites confirmables. QA par le testeur sur les fichiers et scénarios concernés. SYN-11 reste clos ; aucun changement du bouton.

Issue de diagnostic pour la seule correction du déclencheur : `bug`. La reprise de montants déjà stockés constitue un périmètre distinct sensible aux données existantes : route `bug_sensitive` avec analyse préalable. Le support devra d'abord comparer les montants stockés au produit quantité × prix sur une copie autorisée, compter les écarts et examiner leurs usages. Une réparation éventuelle demandera une preuve avant/après sur cette copie et une confirmation humaine propre à l'opération en production. **Corriger le déclencheur ne prouve pas que tous les anciens montants seront remis à jour.** Aucun recalcul global n'est demandé maintenant.

## Brouillon de réponse client — non envoyé

Le calcul fourni ne se relance pas lorsque seul le prix change.
Cela explique le montant 30 conservé au lieu de 36 dans le scénario reçu.
Les lignes gratuites restent autorisées, y compris après confirmation.
En attendant, contrôlez le produit quantité × prix et mettez de côté les lignes incohérentes.
Nous avons préparé un test pour vérifier le problème et la future correction.
Aucun code ni aucune donnée n'a été modifié.
Le nombre de lignes concernées chez vous reste à établir sur une copie de vos données.
Le délai de correction sera fixé après cette vérification ; aucun délai n'est engagé ici.

## Opérations réalisées

Exécution : `python3 /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo_briefing.py /tmp/odoo-delegation-comparison-20260909/runs/E02-S/project --offline` ; lectures locales des pièces, du rôle support et des sources citées ; rédaction des seuls livrables dans `output/` ; contrôle documentaire de conservation du journal. Aucun serveur ni test Odoo exécuté.
