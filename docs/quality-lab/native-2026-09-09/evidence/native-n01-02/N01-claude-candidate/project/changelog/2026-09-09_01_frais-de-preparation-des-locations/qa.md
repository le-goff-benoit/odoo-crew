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

---

## 2026-09-09 — Point n°2 : frais de préparation D-03 (remplace D-02) — mode tâche, **niveau renforcé**

**Série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental` · fusion des trois
voies QA (statique, exécution, copie client) — fragments dans
`.odoo-agents/flow-artifacts/frais-d03/`.

### Verdict

**VALIDÉ** — D-03 est implémentée, testée, et la reprise des données déjà écrites par le
point n°1 de cette release est prouvée sur `lab_client`, y compris dans son sens
descendant. Aucune réserve nouvelle. La réserve R1 du point n°1 (`author` du manifest)
reste ouverte, inchangée, sans effet fonctionnel.

**Portée exacte de ce verdict** : validation **locale**, sur base de QA neuve et sur copie
synthétique. Ni recette complète, ni désinstallation, ni production, ni déploiement —
conformément à D-03 (« validation locale seulement »).

### Pourquoi la QA du point n°1 ne suffisait pas

Ce n'est pas une formalité de procédure, c'est une cause technique mesurée :

1. **Les tests du point n°1 attestaient l'inverse de D-03.** Six d'entre eux (12 EUR,
   borne à 4 jours) sont devenus faux le 09/09. Les conserver aurait rendu la suite rouge ;
   les ignorer aurait laissé D-02 sans filet.
2. **La reprise du point n°1 ne pouvait pas se rejouer.** Version installée sur
   `lab_client` mesurée avant travaux : `19.0.1.1.0`, **égale** à celle du manifest. Un
   script de `migrations/` ne s'exécute que si la version installée est strictement
   inférieure. Sans nouveau dossier `19.0.1.2.0` **et** nouvel incrément du manifest, le
   `-u` de D-03 aurait laissé les sept totaux à leurs valeurs D-02, **sans une seule
   erreur dans les logs**.
3. **La correction va dans les deux sens.** Les locations de 4 jours perdent les 12 EUR
   que le point n°1 leur avait ajoutés. Une reprise conçue comme « ajouter les frais »
   aurait produit des montants faux. Seule la réapplication de la formule est correcte —
   et c'est aussi ce qui la rend idempotente.

Autrement dit : la première QA prouvait D-02 sur une base déjà modifiée. Rejouer les mêmes
contrôles sans toucher à la version aurait donné un vert **mensonger**.

### Résultats d'exécution

| Contrôle | Résultat | Détail |
|---|---|---|
| Lint `--changed` (ruff bloquant + conseils + contrôles Odoo) | ✅ | 7 fichiers, 0 erreur, 0 conseil, 0 info |
| Installation sur base neuve `lab_qa` | ✅ ok | 11 s |
| Mise à jour `-u lab_rental` sur base existante | ✅ ok | 4 s |
| Tests ciblés `/lab_rental:TestPreparationFee` | ✅ **11/11** | 0 failed, 0 error, 0 skipped |
| Suite du module sans filtre de tag | ✅ **11/11** | la classe testée est toute la suite |
| Les tests échouent-ils sur les constantes D-02 ? | ✅ **6/11 rouges** | discrimination prouvée dans les deux sens |
| ERROR / CRITICAL, WARNING `lab_rental` dans les logs | ✅ 0 / 0 | |
| **La reprise `19.0.1.2.0` s'exécute-t-elle vraiment ?** | ✅ | `Running upgrade [19.0.1.2.0>] post-migrate` dans le log ; version installée → `19.0.1.2.0` |
| **Copie client `lab_client` — reprise des données** | ✅ | 3 sur 7 repris (dont **2 à la baisse**), delta net **−21,00 EUR**, total 296,00 → **275,00**, prêts intacts, **0 écart** vs prédiction |
| Idempotence de la reprise | ✅ | `migrate()` rejouée 2 fois : totaux identiques |
| Aucun résidu D-02 actif | ✅ | 5 occurrences de « 12 », toutes en commentaire historique |
| Désinstallation | ⏳ n.a. | revient à la clôture (`/odoo-close`) |
| Parcours navigateur, captures | ⏳ n.a. | le module n'a aucune vue ; rien à jouer |

Preuves : `preuves/d03_lint.txt`, `d03_tests_cibles.txt`,
`d03_tests_cibles_update.txt`, `d03_tests_rouges_sur_d02.txt`,
`d03_copie_client_avant.txt`, `d03_copie_client_update.txt`,
`d03_copie_client_apres.txt`, `d03_copie_client_idempotence.txt`, `d03_diff_stat.txt`.

### Anomalies bloquantes

Aucune.

### Anomalies majeures

Aucune subsistante. Une **anomalie majeure a été anticipée puis désamorcée avant d'écrire
du code** : la reprise inopérante par égalité de version (voir ci-dessus). Contrairement au
point n°1, où la mesure avait démenti la revue, ici la revue a **prédit** le piège — la
version installée a été lue sur `lab_client` avant toute modification — et les sept valeurs
attendues ont été écrites dans la spec puis retrouvées à l'identique.

### Remarques mineures / réserves

- **R1 (report du point n°1, toujours ouverte)** — clé `author = Camptocamp` du manifest,
  valeur supposée. À confirmer par l'humain. Aucun effet fonctionnel.
- **R4** — le module porte désormais **deux** dossiers de migration, dont
  `19.0.1.1.0/` qui applique une décision **qui n'a plus cours**. C'est correct : il sert
  une base restée en `19.0.1.0.0`, laquelle passera par D-02 puis immédiatement par D-03.
  **Ne pas le supprimer à la clôture.** Noté dans les notes de la release.
- **R5** — manifest incrémenté **deux fois pendant la release** (`.1.1.0` puis `.1.2.0`),
  contrairement à la règle « une fois, à la clôture ». Obligatoire dans les deux cas :
  chaque reprise exige son incrément. À la clôture, incrémenter au-delà est sans danger ;
  redescendre tuerait les deux reprises.
- **R6** — la positivité de `days` / `daily_rate` reste une hypothèse de la décision, non
  contrainte par le code. Volontaire, hors périmètre, inchangé depuis le point n°1.
- **R7** — le point n°1 est marqué « VALIDÉ SOUS RÉSERVE » dans le suivi et son verdict
  reste vrai *pour D-02*. Le comportement effectivement livré par la release est **D-03**.
  La clôture ne doit communiquer que D-03 ; annoncer 12 EUR à 4 jours serait faux.

### Couverture des critères d'acceptation (point n°2)

| Critère | Couvert par | État |
|---|---|---|
| CA1 — location 5 j × 10 → 65,00 (borne inclusive) | `test_rental_above_threshold_carries_the_fee` + `lab_client` id 1 | ✅ |
| CA2 — location 4 j → 40,00, **plus de frais** | `test_rental_at_former_threshold_is_free_of_fee`, `test_rental_below_threshold_is_free_of_fee` + `lab_client` id 2 et 4 | ✅ |
| CA3 — location 6 j × 10 → 75,00 | `test_rental_well_above_threshold_carries_the_fee` | ✅ |
| CA4 — prêt 10 j → 100,00 ; prêt 5 j → 50,00 | `test_loan_never_carries_the_fee`, `test_loan_at_threshold_never_carries_the_fee` + `lab_client` id 5 et 6 | ✅ |
| CA5 — forfait dû à tarif nul ; 0 j → 0,00 | `test_fee_does_not_depend_on_the_daily_rate` + `lab_client` id 7 | ✅ |
| CA6 — le stocké suit `days` et `kind` | `test_fee_follows_days_and_kind_changes` | ✅ |
| CA7 — forfait plat, non proportionnel | `test_fee_is_flat_not_proportional` | ✅ |
| CA8 — valeur écrite en base | `test_stored_value_is_written_in_database` + lecture SQL sur `lab_client` | ✅ |
| CA9 — reprise sur `lab_client` : 3/7, −21,00, total 275,00, prêts intacts | mesure avant/après, 0 écart vs prédiction | ✅ |
| CA10 — reprise idempotente | `migrate()` rejouée 2 fois | ✅ |
| CA11 — la reprise **s'exécute** (version → 19.0.1.2.0) | ligne `Running upgrade [19.0.1.2.0>] post-migrate` du log | ✅ |
| CA12 — aucun résidu D-02 actif | `grep` + `test_fee_amount_and_threshold_are_the_ones_of_d03` | ✅ |
| CA13 — ni vue, ni droit, ni champ ajouté | revue du diff, `security/` non touché | ✅ |

**13/13.** Aucun critère non satisfait.

### Non testé / angles morts

- **Désinstallation**, **suite complète du stack**, **mise à niveau depuis la sauvegarde
  d'origine** : hors QA de tâche, à la clôture.
- **Chaîne complète `19.0.1.0.0 → 19.0.1.2.0` en un seul `-u`** : non jouée. `lab_client`
  était déjà en `19.0.1.1.0` ; la séquence des deux reprises d'affilée sur une base neuve
  encore en `19.0.1.0.0` reste à vérifier à la clôture. Elle devrait converger (chaque
  reprise réapplique la formule courante), mais **ce n'est pas mesuré** — c'est le seul
  angle mort réel de ce point.
- **Aucun écran vérifié**, faute d'écran : le module ne déclare aucune vue.
- **Volume** : la reprise fait `search([])` puis recompute en mémoire — instantané sur
  sept enregistrements, à traiter par lots sur un parc réel.
- **Multi-société, archivage, portail, mobile** : sans objet.
- `lab_client` est **synthétique** et peuplée par la QA du point n°1 : elle prouve le
  mécanisme, pas le comportement sur un vrai parc client.

### Appris (pour le journal)

- **Une reprise ne se rejoue pas deux fois dans la même release sans un nouvel incrément.**
  Quand une décision est remplacée en cours de release, le dossier `migrations/` déjà
  consommé est inerte : la version installée a rattrapé le manifest. Il faut un nouveau
  dossier **et** un nouvel incrément, et la version installée se **lit sur la copie** avant
  de conclure.
- **Une reprise doit réappliquer la formule, jamais un delta.** Une décision qui en
  remplace une autre corrige aussi **à la baisse**. Le recompute est la seule forme à la
  fois correcte dans les deux sens et idempotente.
- **Remplacer une décision, c'est réécrire les tests, pas en ajouter.** Les tests qui
  attestaient D-02 étaient devenus des assertions fausses ; les cas de la borne à 4 jours
  sont conservés mais avec l'attente inverse, ce qui documente le changement dans le code.
- La méthode du point n°1 (mesurer avant de conclure) a payé : ici le piège a été
  **prédit**, chiffré dans la spec, puis retrouvé à l'identique — 0 écart sur 7 valeurs.
