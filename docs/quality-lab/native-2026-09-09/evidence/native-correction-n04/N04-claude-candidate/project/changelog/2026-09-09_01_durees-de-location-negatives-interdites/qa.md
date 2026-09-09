# QA de la release

## 2026-09-09 — Point 1 : contrainte SQL `lab.rental.days >= 0` (D-31)

**Verdict : VALIDÉ** — 7/7 tests verts, contrainte posée et éprouvée sur la copie,
7/7 critères d'acceptation couverts. Une dette antérieure reste à arbitrer.

### Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Lint des fichiers touchés | `odoo-lint.sh --changed <base> lab_rental` | ⚠️ 1 erreur, **antérieure** (`__manifest__.py` sans `author`) ; 0 sur les 3 fichiers touchés ; `ruff` absent de l'environnement |
| Installation base neuve | `labctl qa lab_rental --quick` | ✅ `install=ok`, 0 ERROR / 0 CRITICAL |
| Tests ciblés | `--tags /lab_rental:TestDaysConstraint` | ✅ **7 exécutés, 0 échec, 0 erreur** (⏱ 13 s) |
| Mise à niveau de la copie | `labctl update` sur `lab_client` | ✅ contrainte ajoutée, 2 locations existantes conservées |
| Contrainte réellement en base | `pg_constraint` sur `lab_client` | ✅ `lab_rental_days_positive` → `CHECK ((days >= 0))` |
| Rejeu manuel sur la copie | shell Odoo `lab_client` | ✅ create et write négatifs refusés, données valides intactes |

### Critères d'acceptation

| # | Critère | Couvert par | État |
|---|---|---|---|
| C1 | Création à jours négatifs refusée | `test_create_negatif_refuse` + rejeu sur `lab_client` | ✅ |
| C2 | Modification à jours négatifs refusée | `test_write_negatif_refuse` + rejeu sur `lab_client` | ✅ |
| C3 | `days = 0` reste valide (création et modification) | `test_zero_reste_valide` ; prêt à 0 jour conservé sur la copie | ✅ |
| C4 | Total inchangé (jours × tarif) | `test_total_inchange` (6×12.5=75, puis 8×12.5=100) | ✅ |
| C5 | Location valide conservée après rejet | `test_location_valide_conservee_apres_rejet` + rejeu sur la copie | ✅ |
| C6 | La contrainte est bien SQL, au niveau table | `test_contrainte_bien_sql` (lecture de `pg_constraint`) | ✅ |
| C7 | Aucune vue, aucun droit, aucun autre comportement modifié | relecture du diff (5 lignes, un seul fichier existant modifié) | ✅ |

### Notes techniques

- Un `write` sur ce modèle ne déclenche pas d'écriture immédiate : les tests appellent
  explicitement `env.flush_all()` dans le bloc attendu en échec, sans quoi l'`IntegrityError`
  n'arriverait jamais et le test serait faussement vert.
- Chaque rejet est encadré d'un `env.cr.savepoint()` : une `IntegrityError` laisse sinon la
  transaction avortée, et C5 (« la location valide subsiste ») serait intestable.

### À arbitrer (dette antérieure, non introduite par cette tâche)

- `lab_rental/__manifest__.py` n'a pas de clé `author` : erreur de lint et WARNING Odoo à
  chaque chargement, déjà présents sur le commit de base. Hors périmètre de D-31 et de la
  consigne « aucun écran ni droit à modifier » ; à corriger d'un mot lors d'une prochaine
  tâche ou à la clôture, sur décision.
