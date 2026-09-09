# QA — release 2026-09-09_01 Frais de préparation des locations

## 2026-09-09 — Point n°1 : frais de préparation D-02 — mode tâche, **niveau renforcé**

**Série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental` · fusion des trois
voies QA (statique, exécution, copie client) — fragments dans
`.odoo-agents/flow-artifacts/frais-preparation/`.

### Verdict

**VALIDÉ SOUS RÉSERVE** — la règle D-02 est implémentée, testée et prouvée sur les données
existantes de la copie ; la seule réserve est une valeur inventée faute d'information
(`author` du manifest), sans effet fonctionnel.

### Résultats d'exécution

| Contrôle | Résultat | Détail |
|---|---|---|
| Lint `--changed` (ruff bloquant + conseils + contrôles Odoo) | ✅ | 6 fichiers, 0 erreur, 0 avertissement, 0 info |
| Installation sur base neuve `lab_qa` | ✅ ok | 2 s |
| Mise à jour `-u lab_rental` | ✅ ok | 4 s |
| Tests ciblés `/lab_rental:TestPreparationFee` | ✅ **9/9** | 0 failed, 0 error, 0 skipped |
| Suite du module sans filtre de tag | ✅ **9/9** | la classe testée est toute la suite |
| Les tests échouent-ils sur l'ancienne formule ? | ✅ **6/9 rouges** | discrimination prouvée |
| ERROR / CRITICAL, WARNING `lab_rental` dans les logs | ✅ 0 / 0 | |
| **Copie client `lab_client` — reprise des données** | ✅ | 3 enregistrements repris sur 7, +36,00 EUR, aucun prêt touché |
| **Idempotence de la reprise** | ✅ | reprise rejouée : totaux identiques |
| Désinstallation | ⏳ n.a. | revient à la clôture (`/odoo-close`) |
| Parcours navigateur, captures | ⏳ n.a. | le module n'a aucune vue ; rien à jouer |

Preuves : `preuves/` de cette release (`tests_cibles.txt`,
`tests_rouges_avant_correctif.txt`, `qa_install_update.txt`, `copie_client_avant.txt`,
`copie_client_apres.txt`, `copie_client_idempotence.txt`, `diff_stat.txt`).

### Anomalies bloquantes

Aucune.

### Anomalies majeures

Aucune. Une **anomalie majeure a été détectée puis corrigée pendant la tâche** : la revue
fonctionnelle tablait sur un recalcul automatique du champ stocké au `-u`. La mesure sur
`lab_client` a montré que les sept totaux existants restaient inchangés. Livré tel quel,
le module aurait appliqué les frais aux **nouvelles** locations seulement, en laissant les
anciennes silencieusement fausses — le pire des cas : pas d'erreur, juste des montants faux.
Corrigé par `migrations/19.0.1.1.0/post-migrate.py` et l'incrément de version qui le rend
exécutable, tous deux vérifiés sur la copie.

### Remarques mineures / réserves

- **R1 (réserve)** — clé `author` ajoutée au manifest, valeur `Camptocamp` **supposée**.
  C'était de la dette antérieure bloquant le lint sur un fichier que la tâche modifiait déjà.
  À confirmer par l'humain, sans urgence : aucun effet fonctionnel.
- **R2** — version incrémentée à 19.0.1.1.0 **pendant** la release, contrairement à la règle
  habituelle (incrément à la clôture). Obligatoire ici : un script de `migrations/` ne
  s'exécute que si la version installée est inférieure à celle du manifest. À la clôture,
  incrémenter davantage est sans danger ; revenir à 19.0.1.0.0 tuerait la reprise.
- **R3** — la positivité de `days` / `daily_rate` reste une hypothèse de D-02, non contrainte
  par le code. Volontaire (hors périmètre). Une location à `days` négatif reste définie :
  elle ne franchit pas la borne, donc pas de frais.

### Couverture des critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| CA1 — location 5 j × 10 → 62,00 | `test_rental_above_threshold_carries_the_fee` + `lab_client` id 1 | ✅ |
| CA2 — location 4 j × 10 → 52,00 (borne inclusive, Q1) | `test_rental_at_threshold_carries_the_fee` + `lab_client` id 2 | ✅ |
| CA3 — location 3 j × 10 → 30,00 | `test_rental_below_threshold_is_free_of_fee` + `lab_client` id 3 | ✅ |
| CA4 — prêt 10 j × 10 → 100,00 (Q2) | `test_loan_never_carries_the_fee` + `lab_client` id 5 | ✅ |
| CA5 — prêt 4 j → sans frais | `test_loan_at_threshold_never_carries_the_fee` + `lab_client` id 6 | ✅ |
| CA6 — le stocké suit `days` et `kind` | `test_fee_follows_days_and_kind_changes` | ✅ |
| CA7 — 0 jour → 0,00 ; location 4 j à tarif nul → 12,00 | `test_fee_does_not_depend_on_the_daily_rate` + `lab_client` id 4 et 7 | ✅ |
| CA8 — données **existantes** reprises sur `lab_client` | mesure SQL avant/après, 3 repris sur 7, +36,00 | ✅ |
| CA9 — ni vue, ni droit, ni champ ajouté | relecture du diff, `git diff` vide sur `security/` | ✅ |
| CA10 — reprise idempotente | `migrate()` rejouée, totaux identiques | ✅ |
| Hors CA — le forfait est bien forfaitaire (D-02 ≠ D-01) | `test_fee_is_flat_not_proportional` | ✅ |
| Hors CA — la valeur est bien écrite en base | `test_stored_value_is_written_in_database` (lecture SQL) | ✅ |

**12/12.** Aucun critère non satisfait.

### Non testé / angles morts

- **Désinstallation** et **suite complète du stack** : hors QA de tâche, à la clôture.
- **Aucun écran vérifié**, faute d'écran à vérifier : le module ne déclare aucune vue. Si un
  écran est ajouté plus tard, le total affiché devra être revérifié.
- **Volume** : la reprise fait un `search([])` puis un recompute en mémoire. Sur sept
  enregistrements c'est instantané ; sur une base de plusieurs centaines de milliers de
  locations, elle mériterait un traitement par lots. Non applicable au périmètre actuel,
  signalé pour la prochaine intervention.
- **Multi-société, archivage, portail, mobile** : sans objet, le modèle ne porte ni
  `company_id`, ni `active`, ni exposition portail.
- La copie client est **synthétique** et a été peuplée par la QA elle-même : elle prouve le
  mécanisme de reprise, pas le comportement sur un vrai parc de données client.

### Appris (pour le journal)

- Changer la formule d'un champ **stocké** ne touche pas une seule ligne déjà en base. Le
  `-u` ne suffit pas, et l'absence d'erreur rend l'oubli invisible : il faut une reprise
  `post-migrate` **et** l'incrément de version qui la déclenche.
- Une hypothèse technique posée en revue fonctionnelle se vérifie sur la copie avant d'être
  écrite comme un fait : ici, elle était fausse.
