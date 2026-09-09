`[4/4 journal]` entrée écrite · `PROJECT.md` : 1 décision actée, 3 pièges ajoutés · graphe terminé sur `task_done`, release **ouverte**.

# Interdiction des durées de location négatives (D-31)

**Projet** Éole · **série** 19.0 (`.odoo-agents/config`, confirmée par le manifest) · **release** `changelog/2026-09-09_01_interdiction-des-durees-de-location-nega` (point n°1) · **module** `lab_rental`

## À décider
- **Clé `author` absente de `__manifest__.py`** — c'est la **seule** cause de l'échec du lint (`odoo-lint.sh` sort en 1) et des 3 WARNING à chaque chargement. Dette antérieure, hors du diff : signalée, non corrigée faute de mandat. Un mot de votre part et elle part à la clôture.
- **`daily_rate` négatif reste possible**, et produirait un `amount_total` négatif par une autre voie que la durée. D-31 ne tranche que `days` : je m'y suis tenu. Si la règle métier visait le total, il manque un arbitrage.

## Cadrage
Verdict standard : **à développer** — `lab.rental` est un modèle entièrement custom, aucun paramètre Odoo ne borne un entier. La forme, elle, est du standard 19.0 pur : `models.Constraint` (`odoo/orm/table_objects.py:79`), jamais `_sql_constraints`. Aucune question bloquante : D-31 tranche les deux (zéro valide, contrainte SQL). Hors périmètre : `daily_rate`, toute vue, tout droit, toute borne haute.

## Réalisation
- `lab_rental/models/business.py` — `_check_days_positive = models.Constraint('CHECK(days >= 0)', "Le nombre de jours d'une location ne peut pas être négatif.")`, placé après `_description`, avant les champs. Aucun champ ajouté, modifié ni supprimé ; `_compute_amount_total` et son `@api.depends` intacts.
- `lab_rental/tests/__init__.py` et `tests/test_rental_days.py` — 6 tests `@tagged('post_install', '-at_install')`.
- `security/ir.model.access.csv` et le manifest non touchés ; version laissée à `19.0.1.0.0` (l'incrément se fait à la clôture).

## QA de tâche (renforcée — données existantes)
| Contrôle | Résultat |
|---|---|
| Lint `--changed` (3 fichiers) | 1 erreur, **hors diff** (`__manifest__.py`, clé `author`) — 0 sur le code livré |
| Lint — étape ruff | **non exécutée** : `ruff` absent de l'hôte et de l'image `odoo-qa:19.0` |
| Install base neuve / mise à niveau (`lab_qa`) | `install=ok` · `update=ok` |
| Tests ciblés `TestRentalDaysConstraint` | **6/6**, 0 failed, 0 error, 0 ignoré |
| Non-vacuité des tests | contrainte retirée → **4/6 rouges** ; remise → 6/6 verts |
| Mise à niveau de la copie `lab_client` | ok, aucun échec d'ajout de contrainte |
| `pg_constraint` sur la copie | `lab_rental_check_days_positive` = `CHECK ((days >= 0))` — absente avant la tâche |
| Refus reproduits **sur la copie** | création `-2` et écriture `-5` refusées ; location valide intacte (`days=4`, `amount_total=40.0`) ; `days=0` accepté |
| Message rendu à l'utilisateur | « Le nombre de jours d'une location ne peut pas être négatif. » |
| Copie rendue propre | enregistrements de vérification supprimés, 0 ligne — état initial |

| Critère d'acceptation | Couvert par | État |
|---|---|---|
| CA1 contrainte réellement en base | `test_constraint_is_in_database` + lecture `pg_constraint` sur la copie | ✅ |
| CA2 création négative refusée | `test_create_negative_days_refused` + copie | ✅ |
| CA3 modification refusée, enregistrement conservé | `test_write_negative_days_refused`, `test_valid_rental_survives_refusal` + copie | ✅ |
| CA4 zéro valide, total nul | `test_zero_days_allowed` + copie | ✅ |
| CA5 calcul du total inchangé | `test_total_still_computed` (7 × 12 = 84) | ✅ |

Détail et preuves : `changelog/2026-09-09_01_interdiction-des-durees-de-location-nega/qa.md`.

## Reste à faire
- Les deux points « À décider » ci-dessus.
- **Contrôles incomplets, dits sans les masquer** : ruff indisponible (style Python vérifié par revue du diff seulement) ; désinstallation, suite complète et navigateur non joués — ils relèvent de `/odoo-close` ; le comportement sur une base **contenant déjà** des durées négatives n'a pas pu être observé, la copie étant vide.
- Leçon candidate pour `LESSONS.md` : « une contrainte SQL écrite n'est pas une contrainte posée » — `pg_constraint` après update est le seul contrôle qui le prouve. À promouvoir par `/odoo-feedback` si elle se répète ailleurs.

## Release
1 point dans la release, 1 réalisé. Rien n'est commité. Clôture et recette complète : `/odoo-close`.