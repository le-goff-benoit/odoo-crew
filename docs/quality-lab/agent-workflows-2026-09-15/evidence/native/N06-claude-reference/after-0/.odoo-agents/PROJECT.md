# Registre Boréal — brouillons et références émises
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Décisions actées
- **B-42 (2026-09-16, appliquée)** — `action_repair` de `lab.register` agit sur `self` × `draft` × `env.company` seulement ; tri `date_document` puis `id` ; `sequence` 100, 200, … ; `snapshot_total` hors lignes `cancelled`. Les `issued` et les autres sociétés sont strictement préservés. Source : `decisions/current.md`, mise en oeuvre et preuves dans `changelog/2026-09-15_01_repair/`.
- **Pas de script de migration pour cette reprise** — un `post-migrate` s'appliquerait à toutes les sociétés de toute base mise à jour, ce que B-42 interdit. Une reprise reste une opération ciblée, jouée et tracée sur la copie.

## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.
- **Un `qa.md` titré `PASS` avec sa portée en petits caractères en dessous vaut un `INCOMPLET`.** C'était le cas de la recette du 14.09.2026, reclassée en historique non réceptionnant. Lire la portée avant le titre.
- **L'idempotence ne prouve pas un contrat de périmètre.** La `action_repair` fautive, globale, était déterministe donc idempotente : le test d'idempotence passait déjà sur le code cassé. Un test d'idempotence n'a de valeur qu'accompagné de tests de périmètre.
- **`company_ids` dans une `ir.rule` vaut `env.companies` (sociétés activées), pas `env.company`.** Voir `~/odoo-sources/19.0/odoo/addons/base/models/ir_rule.py:41-49`. La règle multi-société laisse donc voir toutes les sociétés activées : borner un traitement à la société active demande un filtre explicite sur `env.company`, la visibilité ne suffit pas.
- **Dette antérieure** : `lab_register/__manifest__.py` n'a pas de clé `author` ; le lint est en erreur de ce seul fait, indépendamment du diff en cours.
- Utilisateurs de la copie `lab_client` : `n06_operator` (ordinaire, sociétés 1 et 2) et `n06_restricted` (ordinaire, société 1) — de quoi tester les droits sans toucher à `admin`.
