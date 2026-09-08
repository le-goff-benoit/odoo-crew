# S-01 — contrat synthétique de développement

Série 19.0, module `quality_case`, objet `quality_case.delivery`. Ce contrat est
une décision de conception du **banc fictif**, pas un arbitrage pris pour un client.
Il complète volontairement les inconnues des exercices d’analyse.

- Une demande concerne un seul article. `ordered_qty` strictement positif,
  `available_qty` positif ou nul. Comparaison des quantités à six décimales.
- Quantité disponible complète : expédition permise ; disponibilité nulle : refus.
- Partiel accepté : expédition sans accord à partir de 60 % inclus ; en dessous,
  un accord du responsable est obligatoire. Si partiel refusé, attendre le complet,
  même avec un accord. Le blocage intervient dans `action_ship`.
- `action_approve` requiert le groupe `quality_case.group_approver` et une personne
  distincte de `create_uid`. L’approbation ne doit pas être forgeable via create/write.
- Une baisse par rapport à la proposition **immédiatement précédente** invalide
  l’accord ; une hausse le conserve. Changer `ordered_qty`, `accepts_partial` ou
  `company_id` invalide aussi l’accord. Pas de maximum historique implicite.
- Les accès suivent les règles de société, y compris en appel direct aux méthodes.
  Le champ `state` passe de `draft` à `done` seulement par `action_ship` autorisée.
- Les groupes, ACL et règle de société sont fournis dans le squelette et figés.
  Le fichier candidat implémente seulement `models/delivery.py`.

L’oracle est un **autre addon**, `quality_oracle`, que le générateur ne voit pas.
Il est installé dans une base jetable, avec de vrais utilisateurs limités.
Le gabarit ne contient que `base`, est créé pour la campagne puis détruit ; chaque
variante démarre de son propre clone. Aucun cache de client ou de campagne antérieure.
La référence et les trois mutations vérifient que le banc distingue succès et défaut.
Cela ne constitue pas une couverture exhaustive du métier de stock Odoo.

Le transport de packs est aussi testé par de vrais appels ORM : identité stable,
réapplication, prévalidation et création de modèle/champs/données. Avec `--studio`,
le gabarit inclut `web_studio` et vérifie le marquage des identifiants externes.
Un import de modèle n'invente aucun champ : `x_name` doit être explicite.

Avant les générations B12, une revue de l'oracle a ajouté deux contrôles du même
contrat : les valeurs par défaut RPC ne doivent pas forger une approbation ou
une expédition ; réécrire une politique inchangée ne doit pas invalider un accord.
Ces contrôles ont trouvé trois échecs dans la première référence du banc. La
référence a été corrigée ; les sorties LLM restent intactes et recevront toutes
la même version de l'oracle. La suite contient désormais huit méthodes de test
métier et quatre de transport (les sous-cas ne sont pas douze tests indépendants).
