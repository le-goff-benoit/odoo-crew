# Frais de préparation des locations (D-02)

**Projet** Atelier Boréal · **série** 19.0 · **release** `2026-09-09_01_frais-de-preparation-des-locations`
(point n°1, **ouverte**) · **module** `lab_rental`

## À décider
- `'author': 'Camptocamp'` ajouté au manifest pour débloquer le lint (dette antérieure) : est-ce le
  bon auteur pour ce projet ?
- Version du manifest passée à `19.0.1.1.0` **pendant** la tâche, contre l'usage : le dossier de
  migration doit porter la version cible. Ne pas la remonter à nouveau à la clôture si c'est la
  version livrée.

## Cadrage
À développer : aucun module de location en Community 19.0, `sale_renting` est Enterprise et
travaille sur `sale.order.line`. Q1 (borne inclusive) et Q2 (prêts exclus) déjà tranchées : aucune
question bloquante. Hors périmètre assumé : `Monetary`, contrainte de positivité, paramétrage.

## Réalisation
- `models/business.py` — `_preparation_fee()` isolé, constantes `PREPARATION_FEE` (12.0) et
  `PREPARATION_FEE_MIN_DAYS` (4), docstring portant D-02 et le remplacement de D-01.
- `tests/test_preparation_fee.py` — 10 tests métier (nouveau).
- `migrations/19.0.1.1.0/post-migrate.py` — reprise idempotente via `env.add_to_compute` (nouveau).
- `__manifest__.py` — version et `author`.

## QA de tâche — niveau renforcé
| Contrôle | Résultat |
|---|---|
| lint des fichiers touchés | ✅ 0 erreur, 0 avertissement |
| installation base neuve + tests ciblés | ✅ `install=ok`, 10/10, ⏱ 15s |
| mise à jour base existante + tests ciblés | ✅ `update=ok`, 10/10, ⏱ 4s |
| mise à niveau de la copie `lab_client` | ✅ 3 lignes sur 7 recalculées, +12.0 exactement |
| idempotence de la reprise | ✅ aucun montant ne dérive |
| périmètre en base (vues, droits, champs) | ✅ inchangé |
| **critères d'acceptation** | **12/12 couverts** (`qa_rapport_tache1.md`) |

## Reste à faire
Rien de rouge. Leçon candidate au dispositif : « corriger le calcul d'un champ stocké ne corrige pas
les valeurs en base » est déjà dans le rôle développeur mais pas dans `LESSONS.md` ; elle vient
d'être payée pour de vrai ici.

## Release
1 point, 1 réalisé. **Release laissée ouverte** comme demandé. Clôture et recette complète : `/odoo-close`.
