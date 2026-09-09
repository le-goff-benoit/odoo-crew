```
[4/4 journal]   entrée écrite · PROJECT.md : 1 décision actée + 2 pièges · release 2026-09-09_01 laissée ouverte
```

# Frais de préparation des locations (D-02)

**Projet** Atelier Boréal (`/work`) · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_frais-de-preparation-des-locations` (point n°1) · **module** `lab_rental`

## À décider
- **Recalcul des enregistrements préexistants.** Changer la *formule* d'un champ **stocké** ne recalcule rien : Odoo ne recalcule que sur variation des dépendances. Sans objet aujourd'hui — la copie `lab_client` contient **0 enregistrement** (compte SQL). Si la base cible en a à la livraison, il faut un `migrations/<version>/post-recompute.py`, écrit avec le numéro de version réel : à trancher à la clôture.
- **Dette antérieure** : `__manifest__.py` n'a pas de clé `author` (1 erreur de lint sur fichier non modifié, 9 WARNING au chargement). Non corrigée, hors périmètre — à traiter avec l'incrément de version à la clôture.

## Cadrage
À développer : le standard de location d'Odoo est `sale_renting`, **enterprise**, et le projet ne l'utilise pas (`lab.rental` dépend de `base` seul) — y basculer serait une refonte. Le delta réel est une addition conditionnelle dans un compute existant. **Aucune question bloquante** : Q1 (borne inclusive) et Q2 (prêts exclus) sont tranchées dans la décision. Hors périmètre assumé : facturation, compta, devise, arrondi, contraintes de saisie, écrans.

## Réalisation
- `lab_rental/models/business.py` — forfait isolé dans `_preparation_fee()`, constantes nommées `PREPARATION_FEE = 12.0` / `PREPARATION_FEE_MIN_DAYS = 4`, seuil écrit `>=`. Le compute garde ses trois dépendances (`days`, `daily_rate`, `kind`) et reste stocké.
- `lab_rental/tests/common.py`, `lab_rental/tests/test_preparation_fee.py` (créés) — 9 tests.
- Aucun champ, aucune vue, aucune ligne de sécurité : **rien de visible ne change** pour l'utilisateur, seul le total des locations de 4 jours et plus augmente de 12 EUR.
- Version du manifest **non incrémentée** : elle bouge une fois, à la clôture.

## QA de tâche
| Contrôle | Résultat |
|---|---|
| `odoo-lint.sh --changed` (fichiers touchés) | ✅ ruff : 0 · contrôles Odoo : 0 erreur / 0 avertissement |
| Installation base neuve + mise à niveau `-u` | ✅ `install=ok update=ok` |
| Tests ciblés `/lab_rental:TestPreparationFee` | ✅ **9/9** |
| Rouge avant correctif (ancienne formule rejouée) | ✅ **4/9 échouent**, code restauré |
| Copie `lab_client` (ORM + SQL, témoins supprimés) | ✅ 4/4 cas conformes, copie laissée intacte |

**8 critères d'acceptation sur 8 couverts** (détail nominatif dans `qa.md`). Preuves dans `changelog/.../preuves/`.

## Reste à faire
- **Contrôle incomplet corrigé en cours de route, à ne pas perdre** : le premier passage `--quick` a rendu `✅ tests OK` avec `of 0 tests`. La base QA existait sans le module, et `--quick` fait `-u` dès que la base existe — `--fresh` n'y change rien puisqu'il la recrée. Faux vert écarté en passant par le chemin complet (`-i`). **Leçon candidate pour `/odoo-feedback`** : un `-u` sur un module non installé doit être un échec, pas un vert.
- Le lint a d'abord tourné sans `ruff` (« lint partiel ») ; ruff 0.16.6 a été installé et le lint rejoué entièrement — le verdict partiel n'a pas été retenu.
- Les deux points « À décider » ci-dessus.

## Release
1 point, 1 réalisé. **La release reste ouverte**, comme demandé. Clôture, recette complète, captures et livrables client : `/odoo-close`. Rien n'a été commité.