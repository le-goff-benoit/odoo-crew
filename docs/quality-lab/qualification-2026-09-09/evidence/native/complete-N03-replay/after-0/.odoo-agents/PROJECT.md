# Association Aster — indicateur Studio de revue
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-22 réalisée en voie Studio le 2026-09-09 : `x_lab_request.x_studio_needs_review`
(booléen stocké) = `x_studio_kind == 'rental'` ET `x_studio_days >= 7`, seuil inclus,
prêts exclus. Genre vide, durée nulle ou négative ⇒ pas de revue (hypothèse actée
faute de mention dans D-22).
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
`x_lab_request` n'a **aucune vue** : les champs ne sont lisibles que par RPC, filtre ou
export. Un « ça ne se voit pas » sur ce modèle n'est pas un bug tant qu'aucune vue
n'a été demandée.
Voie Studio = pas de module, donc pas de lint Ruff ni de `odoo-test.sh` : la preuve est
le couple `odoo_pack.py diff` + scénario RPC rejouable, rouge avant et vert après.
En XML-RPC sur ce parc, `create` renvoie une liste ; normaliser avant de réutiliser l'id.
