# QA statique D-03 — VALIDÉ
Série 19.0 (manifest), mode tâche renforcée. Relecture du delta D-02→D-03 et du diff depuis .base : compute assigné sur chaque record, dépendances complètes, forfait non cumulatif, store=True inchangé. 8 méthodes testent les résultats métier indépendants et la persistance ; imports tests existants vérifiés.
Lint natif --changed ace91a8b81 : 5 fichiers, ruff exécuté, 0 erreur/avertissement/info (lint-green.json/log). Aucun code modifié depuis cette preuve.
Le script ORM utilise add_to_compute/_recompute_recordset présents dans odoo/orm/environments.py:453 et models.py:6932 en 19.0 ; lab_client synthétique seul périmètre autorisé.
D3-C6 : aucun changement des vues, droits, facturation, dépendances ou version depuis D-02. Les nouveaux fichiers de tests de la release restent non suivis à l'entrée et à la sortie : QA de l'arbre local, pas d'un commit livré ; inclure ces fichiers lors d'une future livraison.
