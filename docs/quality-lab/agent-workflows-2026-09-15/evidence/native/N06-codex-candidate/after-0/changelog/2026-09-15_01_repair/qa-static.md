# QA statique — Odoo 19.0 — B-42
Diff relu : action_repair seulement et trois fichiers de tests nouveaux. Lecture contrôlée, filtre self/state/company active, tri date/id, précontrôle collectif write, valeurs distinctes par record ; aucune recherche globale ni sudo. Comparaison exacte des Float, sans arrondi inventé ; idempotence sans écriture inutile.
Sources : orm/models.py::check_access (4100), sorted (6261) ; sale/models/sale_order.py (1563) pour contrôle write.
Ruff bloquant : All checks passed dans proofs/lint.log. Conseil COM812 non bloquant (virgule de lambda). Contrôle structurel Odoo : échec sur author manquant uniquement, y compris --only-files car ce contrôle conserve toute anomalie structurelle. Ne pas annoncer un lint global vert.
proofs/static-comparison.txt prouve que manifest et les deux fichiers de sécurité sont identiques à HEAD ; author absent avant la tâche. Dette antérieure, sans effet sur action_repair ni l’update. Syntaxe des quatre fichiers Python contrôlée. Tests importés par tests/__init__.py et la classe est réellement exécutée par Odoo.
Aucun changement de dépendances, schéma, ACL/règles, version (19.0.1.0.0 conservée jusqu’à clôture). Aucun écran modifié.
Verdict de voie : diff conforme, dette structurelle préexistante explicitement conservée. Relecture non indépendante.
