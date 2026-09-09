<!-- release ouverte -->
# Frais de préparation des locations

Release ouverte le 09.09.2026. **Suivi vivant** tant que ce release est
ouvert : une ligne par point, son test ciblé, son état. La recette complète, les
captures et les livrables client se font à la clôture (`/odoo-close`), qui
réécrit ce fichier dans sa forme finale.

## Points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Frais de préparation 12 EUR sur les locations de 4 jours et plus (D-02) | `/lab_rental:TestPreparationFee` — 10/10 (preuves du 09.09, périmées) | **PÉRIMÉ — remplacé par le point 2 (D-03)**. Validé le 09.09 en l'état d'alors ; ce n'est plus ce que la release livre. Preuves conservées comme historique |
| 2 | Frais de préparation révisés : 15 EUR à partir de 5 jours (D-03, remplace D-02) | `/lab_rental:TestPreparationFee` — 12/12 | VALIDÉ — lint 0, 12/12 tests ciblés (install et update), reprise 19.0.1.2.0 prouvée sur lab_client y compris à la baisse, 14/14 critères |

## Notes de travail

<!-- Ce qui a été décidé ou découvert en cours de release et qui doit survivre à la
     conversation : hypothèses posées, arbitrages, pistes écartées. Une ligne par
     note, datée. -->

- 2026-09-09 — D-02 (`decisions/2026-09-08.md`) **remplace** D-01 (7 % sur toutes les locations),
  encore présente au journal du 2026-08-01. Le forfait est **fixe** : 12 EUR, jamais proportionnel.
  Q1 borne inclusive (4 inclus), Q2 prêts exclus quelle que soit la durée.
- 2026-09-09 — Version du manifest montée à **19.0.1.1.0 pendant la tâche**, contrairement à l'usage
  (une fois à la clôture) : le dossier `migrations/19.0.1.1.0/` doit porter la version cible pour que
  la reprise s'exécute. À la clôture, ne pas la remonter une seconde fois si c'est bien la version livrée.
- 2026-09-09 — Une mise à niveau seule ne recalcule pas un champ stocké : constaté sur `lab_client`,
  d'où le script de reprise. Vaut pour toute future modification de `_compute_amount_total`.
- 2026-09-09 — Écartés du périmètre, à rouvrir si le client le demande : `Monetary` + `currency_id`
  sur `amount_total`, contrainte de positivité sur `days` / `daily_rate`, paramétrage du seuil et du montant.
- 2026-09-09 — `'author': 'Camptocamp'` ajouté au manifest (dette antérieure bloquant le lint) —
  **à confirmer** par l'humain à la clôture.
- 2026-09-09 — **D-03** (`decisions/2026-09-09.md`) remplace **D-02** dans la même release : 15 EUR à
  partir de **5 jours inclus**, prêts toujours exclus, `jours × tarif` inchangé. Le point 1 devient
  historique ; la release ne livre que D-03. Le montant d'une location de 4 jours **baisse** (52 → 40).
- 2026-09-09 — Le module est installé en 19.0.1.1.0 sur `lab_client` : ce dossier de migration ne sera
  pas rejoué. D'où le manifest en **19.0.1.2.0** et `migrations/19.0.1.2.0/`. Le dossier 19.0.1.1.0 est
  conservé pour une base encore en 19.0.1.0.0 ; les deux reprises sont idempotentes.
- 2026-09-09 — La communication de clôture ne mentionne **jamais** l'étape intermédiaire 12 EUR / 4 jours :
  elle n'a existé que sur la copie de validation, aucun document client ne la porte.
- 2026-09-09 — Deux révisions du même forfait en deux jours : le paramétrage (seuil et montant en
  configuration) reste hors périmètre, mais est à reproposer au client si une troisième arrive.
- 2026-09-09 — Rien ne change à l'écran : seul le montant total des locations de 4 jours et plus
  augmente de 12 EUR, sans ligne de détail. C'est le seul point à expliquer dans la communication.
