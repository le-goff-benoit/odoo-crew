# Implémentation — Codex développeur, Odoo 19.0

Compute D-02 dans `lab_rental/models/business.py`, dépendances existantes complètes, stockage conservé.
Trois fichiers de tests ajoutés : common TransactionCase (seule dépendance base), import et 7 tests métier post_install.
Reprise idempotente : `changelog/2026-09-09_01_frais-de-preparation-d-02/scripts/recompute_lab_totals.py`, garde stricte lab_client et ORM Odoo 19.0.
Jeu pré-update réellement créé sur l'ancienne formule : trois lignes, totaux 30/40/40 (before-update.log).
Lint ciblé : 4 fichiers, Ruff 0.16.6 installé dans un venv local ignoré, contrôles Odoo 19.0 verts ; aucune erreur ni avertissement (lint.log). Une anomalie antérieure hors fichiers modifiés masquée.
Aucun changement de droits, vues, dépendances ou version 19.0.1.0.0. Tests Odoo à exécuter dans les nœuds QA suivants.
