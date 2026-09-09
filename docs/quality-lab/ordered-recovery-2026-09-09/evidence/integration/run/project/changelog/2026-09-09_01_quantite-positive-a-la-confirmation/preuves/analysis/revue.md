# Revue fonctionnelle — quantité strictement positive à la confirmation

**Projet** laboratoire `project` · **série** 19.0 · **module concerné** `lab_qualification` · **voie recommandée** module existant.

Analyse préalable du 9 septembre 2026, sur code initial 19.0.1.0.0 et copie synthétique locale. Aucun code du module, test métier, document partagé ou état de workflow modifié par l'analyste. Le briefing fourni a été réutilisé.

## 1. Ce que je comprends

En tant qu'utilisateur interne, je veux préparer un enregistrement avec une quantité éventuellement nulle puis le confirmer uniquement avec une quantité strictement positive, afin que les confirmations soient exploitables par l'équipe.

**Problème réel** : le module accepte actuellement `confirmed` avec zéro parce que son bouton écrit seulement l'état ; la seule contrainte interdit les négatifs. La demande est saine et le delta est limité. Il s'agit d'un scénario synthétique de qualification, sans fréquence ni coût client mesuré : ne pas lui attribuer un retour sur investissement réel.

**Source du contrat** : `/tmp/odoo-ordered-recovery-20260909/odoo-request.md`, lignes 8–14 (règle et canaux), 16–21 (module, droits et données), 23–25 (livraison et preuves). Les critères ci-dessous sont établis avant développement et résultats de QA.

## 2. Verdict standard Odoo 19.0

**ÇA EXISTE PARTIELLEMENT** : le mécanisme de contrainte existe ; la règle métier sur `lab.qualification` reste à ajouter dans le module custom.

Preuves vérifiées dans les sources locales en lecture seule :

- `/home/blegoff/odoo-sources/19.0/odoo/orm/table_objects.py:79` : `models.Constraint` porte une contrainte SQL et son message ; `apply_to_database` l'applique sur la table du modèle. C'est le point d'extension recommandé.
- `/home/blegoff/odoo-sources/19.0/addons/stock/models/stock_storage_category.py:64` : `_positive_quantity` utilise déjà `CHECK(quantity > 0)` pour une capacité de stockage. Cette règle appartient à un autre modèle et interdit zéro sans condition : elle ne configure pas le modèle du laboratoire.
- `/home/blegoff/odoo-sources/19.0/odoo/orm/decorators.py:88` : `api.constrains` est une alternative Python ; sa documentation avertit que son déclenchement dépend des champs transmis à `create`/`write`. Une protection uniquement dans le bouton ne couvre pas le contrat.
- `/home/blegoff/odoo-sources/19.0/odoo/orm/models.py:895` : `load(fields, data)` est le canal d'import ORM ; il appelle `_load_records`, recueille les erreurs et utilise des savepoints. L'import doit être vérifié par ce canal, pas déduit seulement d'un test du bouton.
- Recherche exacte `lab\.qualification|lab_qualification` dans les arbres `19.0/addons`, `19.0-enterprise`, `19.1/addons`, `19.1-enterprise` : aucun résultat. Ce modèle n'y est pas fourni. Le modèle existant et la règle initiale sont dans `/tmp/odoo-ordered-recovery-20260909/integration/run/project/lab_qualification/models.py:4`, quantité entière ligne 9, contrainte non négative ligne 16, bouton lignes 23–24.

**Série suivante** : saas~19.1 fournit toujours `Constraint` dans `/home/blegoff/odoo-sources/19.1/odoo/orm/table_objects.py:85` et la positivité de capacité dans `/home/blegoff/odoo-sources/19.1/addons/stock/models/stock_storage_category.py:64`. Aucun modèle standard successeur identifié pour `lab.qualification`. Conserver les noms du modèle et des champs actuels ; aucun renommage ou futur standard à reproduire. La forme `models.Constraint` reste compatible avec les deux séries inspectées. La présente intervention cible exclusivement 19.0.

### Existant en base, vérifié avant de recommander du code

Lecture ORM sans commit sur `ordered_copy`, terminée par rollback : `/tmp/odoo-ordered-recovery-20260909/integration/analysis/inventory_readonly.py` ; preuve brute `/tmp/odoo-ordered-recovery-20260909/integration/evidence/shell-ordered_copy-20260909-184301-327a40eb.log` (marqueur `ANALYST_READONLY_JSON`).

Résultat : un module custom installé, aucun champ manuel sur le modèle, aucune action serveur, aucune règle d'enregistrement, une vue formulaire sans héritage. `base.automation` et `web_studio` ne sont pas installés. Une ACL donne CRUD à `base.group_user`. Aucun doublon de personnalisation identifié. Les modules installés sont consignés dans la preuve brute.

La référence `ordered_seed` et sa copie `ordered_copy` portent les mêmes données :

| ID | État | Quantité | Prix unitaire | Montant |
|---|---|---:|---:|---:|
| 1 | draft | 0 | 10 | 0 |
| 2 | draft | 3 | 10 | 30 |
| 3 | confirmed | 3 | 10 | 30 |

Zéro confirmé invalide dans la copie. Preuves initiales : `integration/evidence/inventory-ordered_seed-20260909-183759-07173621.inventory.json`, `integration/evidence/inventory-ordered_copy-20260909-183801-79429f03.inventory.json`, sous la racine `/tmp/odoo-ordered-recovery-20260909/`. `integration/evidence/bootstrap-result.json` atteste le dump/restaure effectif, la conservation des IDs/valeurs et le hash du dump `ordered_seed.dump`. La copie est synthétique, ce n'est pas une copie client.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration native | Très faible | Aucune option existante identifiée pour cette invariant sur le modèle custom ; une consigne de saisie ne garantit pas les canaux ORM/import | Quasi nul, mais besoin non couvert | Non |
| Studio / configuration en base | Faible à moyen, avec installation supplémentaire | Automatisation à maintenir sur création/écriture ; garde transactionnelle et déclencheurs à qualifier ; pas de surcharge de méthode ni tests Python via Studio, code limité à safe_eval | Requalification des déclencheurs et du code stocké à chaque migration | Non : module existant et voie explicitement demandée |
| Code custom | Faible : contrainte et tests ciblés | Invariant persistant couvrant bouton, créations, écritures et imports ; aucun nouvel écran | Rejouer les tests et vérifier le schéma lors de chaque migration | **Oui**, dans `lab_qualification` |

L'usage de `models.Constraint` dans le module reste du code custom utilisant un mécanisme standard, pas une configuration native déjà disponible. Aucun module Stock ou Studio à installer pour obtenir cette règle.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | Haute | Vérifier seulement `action_confirm` | Création directe, écriture d'état ou modification de quantité contourneraient la règle | Porter l'invariant au niveau du modèle/table ; garder le bouton comme entrée existante |
| 2 | Haute | Remplacer la contrainte par une positivité globale | Les brouillons à zéro deviennent invalides, contrairement au contrat | Conserver la non-négativité et ajouter la condition liée à `confirmed` |
| 3 | Haute | Confirmation groupée partielle | Certaines lignes pourraient être confirmées avant l'erreur | Une seule opération transactionnelle ; tester un recordset mêlant quantités positive et nulle, puis relire toutes les lignes après annulation |
| 4 | Haute | Contrôle insuffisant de mise à niveau | Un succès du processus ne prouve ni la présence de la contrainte ni la préservation des données | Contrôler le schéma effectif, les logs et les IDs/valeurs sur la copie ; ne jamais corriger automatiquement un historique invalide |
| 5 | Moyenne | Confondre copie et référence | Les tests pourraient altérer la preuve initiale | Updates/tests/écritures uniquement sur `ordered_copy` ; inventaire final distinct des deux bases |
| 6 | Moyenne | Modifier des droits pour faciliter les tests | La demande interdit tout élargissement | ACL et vue inchangées ; preuve avec utilisateur interne non superutilisateur, sans sudo pour les opérations métier |

Le modèle n'a ni société, ni devise, ni archive, ni état annulé, ni portail spécifique. Ajouter ces dimensions créerait un périmètre nouveau. Les montants sont un calcul synthétique `quantity * unit_price`, sans écriture comptable ou mouvement de stock. La quantité est entière : la borne positive minimale testable est 1, sans précision décimale à arbitrer.

## 5. Questions bloquantes

Aucune dans ce scénario synthétique déjà spécifié. La recommandation module correspond à la demande explicite. Aucun arbitrage humain supplémentaire nécessaire pour cette analyse.

## 6. Hypothèses retenues (à défaut de réponse)

- L'état final `confirmed` implique une quantité entière supérieure à zéro ; les autres comportements existants ne sont pas redéfinis. En particulier, la demande n'interdit pas un retour ORM au brouillon ni n'ajoute de verrouillage général après confirmation.
- La confirmation groupée concerne un appel au bouton sur un recordset ; elle ne nécessite pas de nouvel écran liste ou d'action groupée graphique.
- Le message indique clairement qu'une quantité strictement positive est requise pour un confirmé ; aucun texte exact ni traduction supplémentaire n'est imposé. Utiliser le mécanisme de message standard du framework.
- Le jeu initial étant valide, aucune migration corrective de données n'est nécessaire. Si une autre copie contient un confirmé nul, arrêter sa réception, documenter le cas et demander une décision séparée ; ne pas inventer une quantité de remplacement.
- Les erreurs sont observées avec les mécanismes propres au canal : exception/contrainte pour ORM et bouton, message d'erreur pour `load`. La preuve backend couvre l'appel du bouton ; aucun test navigateur nouveau n'est demandé pour cette évolution sans interface nouvelle.

## 7. Spécification

### Modèle de données

Conserver `lab.qualification`, ses champs et la contrainte existante contre les négatifs. Ajouter une contrainte conditionnelle exprimant : si `state` vaut `confirmed`, `quantity` doit être strictement positive. Choix technique recommandé : `models.Constraint`, cohérent avec le modèle actuel et la série 19.0 ; ne pas mettre le contrôle seulement dans le bouton. Ne pas ajouter de champ requis, modèle, groupe, règle d'accès ou dépendance fonctionnelle.

### Comportement

Autoriser la préparation à zéro et la confirmation positive. Refuser la création directe d'un confirmé à zéro, l'écriture d'un état confirmé sur une quantité nulle, et l'écriture de zéro sur un confirmé. La même règle couvre les créations/écritures via import ORM. Une confirmation groupée invalide échoue intégralement dans sa transaction : aucune autre ligne sélectionnée ne reste confirmée. Les négatifs restent refusés en création comme en écriture. Les montants valides continuent de suivre le calcul existant.

### Interface

Conserver le formulaire et son bouton `Confirm` dans `lab_qualification/views/quantity.xml`. Aucun nouvel écran. La tentative interdite reçoit l'erreur explicite du modèle.

### Sécurité

Conserver exactement l'ACL dans `lab_qualification/security/ir.model.access.csv` : CRUD pour utilisateurs internes (`base.group_user`), sans accès supplémentaire. Aucune nouvelle règle d'enregistrement et aucun contournement `sudo` nécessaire au traitement métier.

### Reprise de données

Appliquer la mise à niveau à `ordered_copy` uniquement. Préserver les trois identités, noms, états, quantités, prix et montants initiaux. Vérifier la présence effective de la nouvelle contrainte si cette voie est retenue. Préserver `ordered_seed` comme référence ; ne lui appliquer ni update ni nouveaux tests. Aucun nettoyage ou redressement automatique des enregistrements historiques.

### Hors périmètre

Nouvelle interface, nouvelles règles multi-société, portail, stock/comptabilité, correction historique automatique, déploiement distant, fermeture de release et recette complète de release. Les livrables de cette intervention restent analyse, implémentation, QA de tâche avec rouge/vert, réception indépendante, mémoire et réception du plan.

## 8. Critères d'acceptation

Les valeurs attendues ci-dessous viennent du contrat et du jeu initial, pas de la méthode à tester. La QA doit garder une trace identifiable des scénarios effectivement démarrés et de leurs résultats ; les quatre tests initiaux seuls ne couvrent pas le delta.

- [ ] **AC01 — Brouillon zéro** (demande 8–9) : étant donné une création au brouillon avec quantité explicite 0, puis une création sans quantité, quand elles sont enregistrées, alors elles sont acceptées avec quantité 0 et montant 0 ; une écriture de zéro sur un brouillon reste permise.
- [ ] **AC02 — Borne positive et bouton** (9–10) : étant donné un brouillon quantité 1, prix 10, quand `action_confirm()` est appelé, alors il devient confirmé, quantité 1 et montant 10. Le cas positif initial quantité 3 reste fonctionnel avec montant 30.
- [ ] **AC03 — Bouton zéro** (9–10) : étant donné un brouillon quantité 0, quand le bouton est appelé, alors l'opération est refusée et, après rollback/savepoint et relecture, il reste brouillon, quantité 0, montant 0.
- [ ] **AC04 — Confirmation groupée atomique** (11–12) : étant donné des brouillons quantité 3 et 0, quand leur recordset est confirmé en une opération, alors elle échoue ; après annulation et relecture, les deux états et leurs quantités/montants restent initiaux. Placer la ligne positive avant la nulle rend observable une implémentation erronée qui traiterait les lignes successivement.
- [ ] **AC05 — Créations directes** (9–10) : étant donné une création directe `confirmed`, quand la quantité vaut 0 ou est omise (défaut 0), alors elle est refusée et aucun nouvel enregistrement invalide ne subsiste ; quantité 1 doit être acceptée.
- [ ] **AC06 — Écritures directes** (9–10, 12–13) : écrire l'état `confirmed` sur un brouillon à zéro, ou écrire quantité 0 sur un confirmé positif, est refusé ; les valeurs précédentes persistent après annulation. Une écriture simultanée état confirmé/quantité 1 est acceptée. Modifier la quantité d'un confirmé vers une autre valeur positive reste possible.
- [ ] **AC07 — Import réel par ORM** (10) : via `load`, importer un nouveau confirmé à zéro et mettre à jour un confirmé existant vers zéro produit des erreurs, sans donnée invalide persistante ; un import de brouillon à zéro et un import de confirmé positif réussissent. Préserver l'identité et les valeurs antérieures du confirmé après l'import refusé. Un test `create` seul ne valide pas ce critère.
- [ ] **AC08 — Négatifs préexistants** (13–14) : les créations et écritures de quantité -1 restent refusées ; après une écriture rejetée sur une ligne quantité 3/prix 10, relire quantité 3 et montant 30.
- [ ] **AC09 — Droits et écran** (16–17) : aucun changement d'ACL, règles, groupes ou vue ; un utilisateur interne non superutilisateur peut préparer et confirmer une ligne positive et rencontre le même refus pour zéro. Aucun élargissement pour public/portail n'est introduit.
- [ ] **AC10 — Mise à niveau de la copie** (18–21) : après update sur `ordered_copy`, les IDs 1/2/3 et tous leurs noms, états, quantités, prix et montants égalent l'inventaire initial ; la nouvelle règle est réellement active. Un inventaire distinct confirme `ordered_seed` inchangée et encore au module initial. Ne pas qualifier cette preuve de restauration client.
- [ ] **AC11 — Historique et effets interdits** (20) : ni script de reprise ni update ne transforme automatiquement un confirmé invalide, ni ne modifie les lignes initiales valides. Si une anomalie historique est constatée, la réception en rend compte et n'annonce pas une mise à niveau validée sans règle active.
- [ ] **AC12 — Preuves de livraison** (23–25) : archiver au moins un nouveau contre-exemple métier rouge exécuté sur le code initial, puis les mêmes attentes vertes après correction et les scénarios couvrant AC01–AC11 ; lint des fichiers touchés, update et tests ciblés réellement exécutés ; réception indépendante des preuves ; mémoire et réception du plan consolidées par l'orchestrateur. La release reste ouverte et aucun bilan ne prétend à une recette complète.

## 9. Estimation et découpage

Faible volume de code ; l'essentiel de l'effort est la preuve multicanal et la préservation de la copie. Ordre : (1) contrat et inventaire figés ; (2) contre-exemple rouge, correction du module et tests ciblés ; (3) QA indépendante, schéma et comparaison avant/après sur copie ; (4) consolidation mémoire et réception du plan. L'analyste ne réalise pas les étapes de développement/QA.

**Niveau QA : renforcé**, car la mise à niveau touche un modèle déjà peuplé et doit préserver des données existantes. Utiliser ici la copie synthétique restaurée, qui est la source de données autorisée du scénario ; aucune copie client réelle n'est nécessaire. Pas de recette complète de release, ni de tests sans rapport avec le delta.

## 10. Ce que l'utilisateur verra

Le formulaire et le bouton restent identiques. Zéro reste utilisable pendant la préparation. La confirmation ou la modification incompatible d'une ligne confirmée affiche désormais une erreur demandant une quantité strictement positive ; une confirmation groupée invalide ne confirme aucune ligne.
