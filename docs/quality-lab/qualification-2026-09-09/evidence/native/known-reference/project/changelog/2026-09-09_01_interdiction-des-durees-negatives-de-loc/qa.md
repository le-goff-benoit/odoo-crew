## 2026-09-09 — Point 1 : contrainte SQL `days >= 0` sur `lab.rental` (D-31) — mode tâche, QA renforcée

**Série** 19.0 (origine : `__manifest__.py`) · **module** `lab_rental` · **flow** `d31-jours-negatifs`,
jointure `module_high_gate` · **contrat QA lié** `cf836fabee21` (9 critères) →
`qa_coverage.json`

Consolidation des trois voies QA renforcées, produites indépendamment :
`module_high_static_qa.md` (statique), `module_high_runtime_qa.md` (exécution sur base QA neuve),
`module_client_copy_qa.md` (copie client `lab_client`). Aucun contrôle n'a été rejoué ici : cette
section fusionne les preuves rendues par les trois voies et les journaux qu'elles citent, relus et
recoupés un à un.

### Verdict

**REFUSÉ — reprise ciblée sur A8.** Aucun défaut de code constaté : la contrainte est conforme à la
forme 19.0, les huit critères d'exécution sont prouvés deux fois (base QA neuve *et* copie client), le
mode d'échec silencieux anticipé par la revue est reproduit et documenté. Le refus porte sur une
**preuve manquante**, pas sur une anomalie : la première condition d'A8 — « le message configuré est
bien celui remonté à l'utilisateur » — n'est traversée par aucune des trois voies. Un critère
d'acceptation partiellement prouvé interdit « VALIDÉ » ; la couverture `partial` interdit également
l'issue `pass` de la jointure.

### Résultats d'exécution (repris des trois voies)

| Contrôle | Voie | Résultat | Preuve |
|---|---|---|---|
| Lint `labctl lint lab_rental` | statique | **échec code 1, dette antérieure seule** — Ruff bloquant *All checks passed!*, conseils aucun ; unique erreur `author` manquant au manifest | `logs/r2-static/lint.log` |
| Revue du diff (forme 19.0) | statique | **conforme** — `models.Constraint`, attribut préfixé `_`, message fr non vide, placement calqué sur `account_payment.py:199-202` ; ni `_sql_constraints` ni `@api.constrains` | `module_high_static_qa.md` |
| Installation base QA neuve + tests ciblés | exécution | **6/6 tests, 0 erreur** — `RECETTE … install=ok tests="0 failed, 0 error(s) of 6 tests" errors=0 failed=0 warnings=3 total=11s` | `logs/r2-runtime/run1-fresh-tags.log` |
| Point de contrôle : suite complète du module | exécution | **6/6 tests, 0 erreur** (le module n'a qu'une classe de tests : la suite recouvre exactement la commande ciblée) | `logs/r2-runtime/run2-suite-complete.log` |
| Mise à niveau `labctl update` sur `lab_client` | copie client | **ok, sans `WARNING odoo.schema`** | `logs/r2-client/01_update.log` |
| Contrainte réellement posée après `-u` | copie client | **présente** : `('lab_rental_check_days_positive', 'CHECK ((days >= 0))')` | `logs/r2-client/02_a6_after_update.log`, `09_final_state.log` |
| Scénario données violantes (A7) | copie client | **risque n°1 reproduit** : update « vert » sans contrainte posée ; nettoyage puis réapplication propre | `logs/r2-client/04…09` |
| Message d'erreur remonté en RPC/UI | *aucune* | **non joué** | — |

### Anomalies bloquantes

Aucune anomalie de code. Un seul défaut de couverture bloque la jointure :

#### B1 — A8 partiellement prouvé : le message remonté à l'utilisateur n'est vérifié nulle part
**Constat** — Les trois voies convergent et le disent chacune explicitement : le message est présent,
non vide et conforme sur l'objet `models.Constraint` (`lab_rental/models/business.py:16` ;
`logs/r2-client/10_a8_message.log` : `message == attendu = True`), mais aucun contrôle ne traverse
`_sql_error_to_message` (`~/odoo-sources/19.0/odoo/orm/models.py:3270-3284`) puis
`~/odoo-sources/19.0/odoo/service/model.py:207-214`. Un `TransactionCase` et `labctl shell` s'exécutent
en contexte serveur direct, sans couche de service ; ils voient `psycopg2.errors.CheckViolation`, pas
la `ValidationError` que reçoit l'utilisateur.
**Conséquence** — Le seul effet perceptible de D-31 pour l'utilisateur (revue §10) est ce message. Une
erreur d'appariement entre la contrainte et son message sortirait un texte technique PostgreSQL à
l'écran sans qu'aucun contrôle actuel ne le détecte. Le risque est faible — le message est porté par le
même objet que la définition — mais il n'est pas prouvé, et un critère écrit exprès après l'analyse de
ce chemin (revue §4 risque 4) ne se solde pas par déduction.
**Correctif proposé** — Ajouter au module un contrôle qui traverse la couche de service : un
`HttpCase` appelant `/web/dataset/call_kw` sur `lab.rental` en création à `days = -1` et asserant que
le message rendu est bien « Le nombre de jours d'une location ne peut pas être négatif. » ; à défaut,
un test qui appelle directement `_sql_error_to_message` sur l'exception capturée. Une seule voie
d'exécution suffit ensuite à reprouver A8 ; les huit autres critères restent acquis.

### Remarques et réserves (n'interdisent pas la reprise, à porter à la clôture)

- **R1 — `author` absent de `__manifest__.py`** (`lab_rental/__manifest__.py`). Dette antérieure,
  confirmée par le développeur (test en dé-modifiant le diff) et par les deux voies. Hors périmètre de
  D-31, mais elle met le lint en code 1 : elle devra être traitée avant la clôture, où le lint est
  bloquant.
- **R2 — le risque n°1 est confirmé, pas neutralisé.** A7 prouve qu'un `-u` sur une base portant une
  ligne `days < 0` se termine sans erreur *sans poser la contrainte* (séquence `post_constraint` →
  report → `finalize_constraints`, `~/odoo-sources/19.0/odoo/orm/registry.py:682-717`). La procédure de
  reprise de la revue §7 est donc **obligatoire** avant toute mise à niveau sur une base peuplée :
  compter `days < 0`, faire arbitrer les lignes par Luc Roy (mise à 0 ou suppression — non tranché par
  D-31), puis mettre à niveau et **vérifier `pg_constraint`**. À reprendre dans le README et la
  communication de clôture.
- **R3 — `days` reste `NULL`-able** (`is_nullable = YES`) : `CHECK (days >= 0)` laisse passer `NULL`.
  Accepté en connaissance de cause (revue risque 5, hypothèse H3), non traité, à ne pas oublier.
- **R4 — la copie `lab_client` a été reconstituée entre la revue et la QA.** La revue §5 la décrivait
  vide *et sans* la contrainte ; la voie copie client la trouve vide *avec* la contrainte déjà posée à
  l'installation du snapshot. Sans conséquence sur le verdict : la voie a joué un `update` explicite
  pour A6, et A7 a recréé de bout en bout le cas « base héritée sans contrainte ». À savoir pour la
  prochaine intervention : cette copie est synthétique et volatile, elle ne prouve rien sur les volumes
  ni sur l'historique réel du client.
- **R5 — inexactitude documentaire dans la voie exécution.** Son préambule annonce les deux journaux du
  run précédent (`logs/runtime/`) à 0 octet ; en réalité seul `run2-suite-complete.log` est vide,
  `run1-fresh-tags.log` fait 27 125 octets. Sans effet sur le verdict — la voie a tout rejoué dans
  `logs/r2-runtime/` — mais les journaux de `logs/runtime/` sont périmés et ne doivent pas être cités.
- **R6 — `kind` dans `@api.depends` de `_compute_amount_total`** (`business.py:19`) sans être utilisé :
  dette antérieure signalée par la revue (risque 6), volontairement non touchée.

### Couverture des critères d'acceptation

Contrat lié `cf836fabee21`, détail et empreintes dans `qa_coverage.json`.

| Critère | Couvert par | État |
|---|---|---|
| A1 — création `days = -1` refusée | `test_create_negative_days_is_rejected` (base QA) + scénario ORM sur `lab_client` | **covered** |
| A2 — écriture `days = -3` refusée, valeur restée 5 | idem, valeur relue par l'ORM **et** par `SELECT` direct | **covered** |
| A3 — `days = 0` accepté, `amount_total == 0.0` | `test_zero_days_is_accepted` + `03_a1_a5.log` | **covered** |
| A4 — `4 × 12,5 = 50,0` (non-régression) | `test_positive_days_amount_total` + `03_a1_a5.log` | **covered** |
| A5 — la location valide survit au rejet, curseur utilisable | `test_valid_rental_survives_rejection` + `03_a1_a5.log` | **covered** |
| A6 — contrainte réellement en base après `-u` | `02_a6_after_update.log`, `09_final_state.log` (+ à l'installation neuve) | **covered** |
| A7 — comportement sur données violantes, joué et documenté | `04…09` sur `lab_client` | **covered** |
| A8 — message remonté à l'utilisateur ; plus de `_sql_constraints` | 2ᵉ condition prouvée (grep vide) ; 1ʳᵉ condition non jouée → **B1** | **partial** |
| A9 — lint sans écart nouveau imputable au diff | `logs/r2-static/lint.log` | **covered** |

### Non testé / angles morts

- Le chemin RPC/HTTP `CheckViolation` → `ValidationError` (B1) : aucun écran, aucun tour, aucun
  `HttpCase` n'a été joué — conforme à l'interdiction de livrable documentaire avant la clôture, mais
  A8 en dépend.
- Le diff de la tâche n'a pas pu être délimité par `git diff` : l'objet de base de la release
  (`.base` = `9cf40f33b0…`) n'existe pas dans cette copie, qui n'a qu'un commit. La voie statique l'a
  contourné en croisant trois sources documentaires ; la délimitation est cohérente mais non
  vérifiable mécaniquement.
- Comportement sur volumes réels et sur les modèles liés d'une vraie base client : hors laboratoire.
- Droits, comptabilité, facturation : hors périmètre de D-31, non touchés (aucun changement dans
  `security/ir.model.access.csv`, aucune vue).

### Appris (à verser au journal à l'étape de capitalisation)

- En 19.0, une contrainte de table posée sur une table déjà violante **échoue en silence** à l'`-u` :
  le module reste `installed`, l'appelant ne reçoit rien, la règle n'est pas appliquée. Vérifier
  `pg_constraint` est le seul contrôle qui conclut. Reproduit ici de bout en bout.
- Ni un `TransactionCase` ni `labctl shell` ne traversent la couche de service : tout critère portant
  sur le message vu par l'utilisateur exige un contrôle HTTP, à prévoir dès l'écriture des tests.
