`[3/4 tester]` VALIDÉ — install/update OK, 7/7 tests, critères 7/7 · une dette antérieure signalée → journal
`[4/4 journal]` entrée écrite · PROJECT.md : D-31 actée + 2 pièges ajoutés

---

# Durées de location négatives interdites (D-31)

**Projet** work (Éole) · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_durees-de-location-negatives-interdites` (point n°1) · **module** `lab_rental`

## À décider
- `lab_rental/__manifest__.py` n'a pas de clé `author`. C'est la seule erreur de lint restante et elle est **antérieure** (présente sur le commit de base, Odoo la relaie en WARNING à chaque chargement). Je ne l'ai pas corrigée : hors de D-31 et hors de « aucun écran ni droit à modifier ». Un mot suffit à la lever — dites-moi si je la prends à la clôture.

## Cadrage
D-31 tranche tout : borne à zéro incluse, contrainte SQL explicitement demandée, `daily_rate` et `amount_total` inchangés. Le standard 19.0 n'offre pas de borne déclarative sur `fields.Integer` → développement, voie module. Hors périmètre : vues, droits, données, facturation.

J'ai levé un risque avant d'écrire : le journal notait que les durées négatives avaient été tolérées pour des essais, ce qui aurait fait échouer l'`ADD CONSTRAINT`. Relevé sur `lab_client` : 0 ligne, donc 0 fautive.

## Réalisation
- `lab_rental/models/business.py` — `_days_positive = models.Constraint('CHECK (days >= 0)', "…")`, forme 19.0 (`_sql_constraints` n'existe plus). +5 lignes, compute non touché.
- `lab_rental/tests/test_days_constraint.py` + `tests/__init__.py` — 7 tests.

Deux points ont demandé de la précision : chaque rejet est encadré d'un `env.cr.savepoint()`, sans quoi l'`IntegrityError` laisse la transaction avortée et « la location valide subsiste » est intestable ; et le test de modification appelle `flush_all()` explicitement, sans quoi il passerait au vert sans rien prouver.

## QA de tâche
| Contrôle | Résultat |
|---|---|
| `odoo-lint.sh --changed` | ⚠️ 1 erreur antérieure (`author`), 0 sur les 3 fichiers touchés ; `ruff` absent de l'environnement, voie non jouée |
| Installation base neuve `lab_qa` | ✅ 0 ERROR / 0 CRITICAL |
| Tests ciblés `/lab_rental:TestDaysConstraint` | ✅ **7/7**, 0 échec (⏱ 13 s) |
| Mise à niveau de la copie `lab_client` | ✅ contrainte posée, 2 locations légitimes conservées |
| Rejeu manuel sur la copie | ✅ create et write négatifs refusés, données intactes après |

| Critère | Couvert par | État |
|---|---|---|
| C1 création refusée | `test_create_negatif_refuse` + copie | ✅ |
| C2 modification refusée | `test_write_negatif_refuse` + copie | ✅ |
| C3 zéro valide | `test_zero_reste_valide` | ✅ |
| C4 total inchangé | `test_total_inchange` | ✅ |
| C5 location valide conservée après rejet | `test_location_valide_conservee_apres_rejet` + copie | ✅ |
| C6 contrainte bien SQL | `test_contrainte_bien_sql` (`pg_constraint`) | ✅ |
| C7 rien d'autre modifié | relecture du diff | ✅ |

Détail et preuves : `changelog/2026-09-09_01_.../qa.md`, `revue_fonctionnelle.md`, `preuves/lint.txt`.

## Reste à faire
- La dette `author` ci-dessus, seul contrôle non vert.
- `ruff` n'est pas installé ici : la voie « règles bloquantes » du lint n'a pas tourné. Je ne la déclare pas verte.
- Deux locations de QA (`QA — …`) subsistent dans `lab_client` ; elles servaient à prouver la migration, à supprimer si vous les jugez parasites.
- Leçon candidate pour `LESSONS.md` : une contrainte SQL testée sans savepoint ni flush explicite donne un test faussement vert.

## Release
1 point, 1 réalisé. La release reste ouverte ; recette complète, guide et communication à `/odoo-close`.