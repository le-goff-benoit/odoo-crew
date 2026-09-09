# QA de la release

## 2026-09-09 — Tâche 1 : interdiction des durées de location négatives (D-31) — mode tâche

**Série** 19.0 (origine : `.odoo-agents/config`, confirmée par `__manifest__.py`) · **module** `lab_rental` · **niveau** renforcé (données existantes)

### Verdict
**VALIDÉ** — la contrainte SQL est réellement posée sur la base de test **et** sur la copie client, les cinq critères d'acceptation sont couverts par des tests exécutés, et la non-vacuité de ces tests est prouvée. Une seule anomalie subsiste : la clé `author` absente du manifest, **dette antérieure hors du diff**, non introduite par cette tâche.

### Résultats d'exécution
| Contrôle | Résultat | Détail |
|---|---|---|
| Lint `--changed` (3 fichiers touchés) | ⚠️ 1 erreur | erreur unique sur `__manifest__.py` (clé `author`), fichier non modifié → dette antérieure. 0 erreur sur le code livré. Preuve : `preuve_lint.json` |
| Lint — étape ruff | ⛔ **non exécutée** | `ruff` introuvable sur l'hôte comme dans l'image `odoo-qa:19.0` ; le style Python n'a été vérifié que par revue humaine du diff |
| Installation base neuve (`lab_qa`) | ✅ `install=ok` | `preuve_tests.json`, `qa_tache1_tests.log` |
| Mise à niveau (`lab_qa`, base chaude) | ✅ `update=ok` | `qa_tache1_update.log` |
| Tests ciblés `TestRentalDaysConstraint` | ✅ **6/6** — 0 failed, 0 error | 15 s en base neuve, 6 s en mise à niveau |
| Non-vacuité des tests | ✅ prouvée | contrainte retirée → **4/6 rouges** (`qa_tache1_sans_contrainte.log`) ; remise → 6/6 verts |
| Mise à niveau sur la copie client (`lab_client`) | ✅ ok | `qa_tache1_copie_update.log`, aucun échec d'ajout de contrainte |
| Contrainte présente dans `pg_constraint` (copie) | ✅ `lab_rental_check_days_positive` = `CHECK ((days >= 0))` | absente avant la tâche → réellement posée |
| Comportement vérifié sur la copie | ✅ refus création et écriture, location valide intacte, zéro accepté | `qa_tache1_copie_verification.log` |
| Message métier rendu à l'utilisateur | ✅ « Le nombre de jours d'une location ne peut pas être négatif. » | `qa_tache1_copie_message.log` |
| Reprise de données | ✅ sans objet | 0 ligne `lab_rental` avant comme après ; 0 ligne négative |
| Copie rendue propre | ✅ | enregistrements de vérification supprimés, copie à 0 ligne |
| Logs | ✅ `ERROR/CRITICAL : 0`, 0 test ignoré | 3 WARNING, tous « Missing `author` key » |
| Écrans / droits | ✅ inchangés | aucune vue dans le module ; `security/ir.model.access.csv` non touché |
| Désinstallation, suite complète, navigateur | ⏭ non joués | relèvent de la recette de clôture (`/odoo-close`) |

### Anomalies bloquantes
Aucune.

### Anomalies majeures
Aucune introduite par cette tâche.

### Remarques mineures et dette antérieure
- **D1 (antérieure)** — `lab_rental/__manifest__.py:1` : clé `author` absente. Fait échouer `odoo-lint.sh` (sortie 1) et produit 3 WARNING à chaque chargement. Hors périmètre de D-31 : signalée, **non corrigée** (règle « on ne reprend pas la dette antérieure sans qu'on le demande »). Un mot du responsable suffit à la traiter à la clôture.
- **R1** — `days` reste un `Integer` non `required` : la colonne accepte `NULL`, que `CHECK(days >= 0)` laisse passer. Sans effet en pratique (l'ORM écrit `0` pour un `Integer` à `False`, et le zéro est autorisé par D-31). Non traité : hors périmètre.
- **R2** — `daily_rate` négatif reste possible et produirait un `amount_total` négatif par une autre voie. Non arbitré par D-31, donc hors périmètre — à porter au responsable si la règle métier visait le total et non la durée.

### Couverture des critères d'acceptation
| Critère | Couvert par | État |
|---|---|---|
| CA1 — contrainte `CHECK (days >= 0)` présente dans `pg_constraint` | `test_constraint_is_in_database` + lecture directe de `pg_constraint` sur `lab_client` | ✅ |
| CA2 — création `days = -1` refusée, rien en base | `test_create_negative_days_refused` (+ création `-2` refusée sur la copie) | ✅ |
| CA3 — écriture `days = -3` refusée, enregistrement inchangé | `test_write_negative_days_refused` et `test_valid_rental_survives_refusal` (+ écriture `-5` refusée sur la copie, `days`/`amount_total` intacts) | ✅ |
| CA4 — `days = 0` accepté, `amount_total = 0` | `test_zero_days_allowed` (+ vérifié sur la copie) | ✅ |
| CA5 — calcul du total inchangé (`days × daily_rate`) | `test_total_still_computed` (7 × 12 = 84) | ✅ |

### Non testé / angles morts
- `ruff` indisponible : la conformité de style Python n'est pas prouvée par outil, seulement par revue du diff.
- Aucun parcours navigateur, aucune capture : le module n'a pas de vue, et c'est de toute façon la clôture qui les produit.
- Désinstallation et suite complète du module non jouées (recette de clôture).
- Le comportement sur une base **contenant déjà** des durées négatives n'a pas pu être observé : ni la copie ni la base QA n'en contiennent. Le risque reste théorique ici, mais il est réel sur une autre base.

### Appris (pour le journal)
- Sur cette copie, la tolérance historique aux durées négatives (journal 2026-08-01) n'a laissé **aucune ligne** : `lab_rental` est vide. La contrainte a donc pu être posée sans reprise.
- Une contrainte SQL écrite dans le code n'est pas une contrainte posée : vérifier `pg_constraint` après mise à niveau est le seul contrôle qui le prouve.
