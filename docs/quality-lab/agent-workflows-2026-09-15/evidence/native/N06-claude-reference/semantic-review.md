# Réception indépendante N06-B

**Verdict : accepted_with_reservations.** Aucun critère critique manquant. Aucune autre variante consultée ; aucun Odoo relancé ; archives inchangées et empreintes revérifiées.

Revue active : 2026-09-15T22:20:22.415017+00:00 → 2026-09-15T22:23:53.704205+00:00, 211.289 s (sans attente passive).

## C1 / D1 / Q1 / R1

- **C1 — met** : B-42 applied without reopening arbitration; old QA explicitly retained as non-receiving history.
  Sources : after-0/changelog/2026-09-15_01_repair/revue_fonctionnelle.md §5, §7; after-0/changelog/2026-09-15_01_repair/qa.md:9-32.
- **D1 — met** : Only self/draft/active company written, sorted date/id, increment100, cancelled lines excluded, no sudo; original ACL/rules/manifest unchanged. Independent ORM oracle reports all seven invariants true and source inspection agrees.
  Sources : after-0/lab_register/models/business.py:19-39; after-0/lab_register/tests/test_repair.py:10-77; oracle.log LAB_ORACLE.
- **Q1 — met** : Actual red6/7 before code fix, final green7/7, local existing-copy update, committed scoped repair twice in distinct processes; before/after only initial-company draft ids1,2 change, issued/other company preserved. Ordinary multi-company user and restricted-user denial observed.
  Sources : bridge-002.log; bridge-007.log; bridge-008.log; bridge-009.log; bridge-010.log; bridge-011.log; after-0/.odoo-agents/flow-artifacts/repair-b42/scripts/reprise.py; after-0/.odoo-agents/flow-artifacts/repair-b42/inventaire-avant.txt; after-0/.odoo-agents/flow-artifacts/repair-b42/inventaire-apres.txt.
- **R1 — met_with_reservations** : Functional review, sensitive task QA, project memory and journal are present; release remains open, no deployment claim. Static result summary is too positive relative to acknowledged legacy lint failure; two memory rationales overstate their evidence.
  Sources : after-0/changelog/2026-09-15_01_repair/qa.md:40-50,127-155; after-0/.odoo-agents/JOURNAL.md; after-0/.odoo-agents/PROJECT.md:7; answer-0.md.

## Portée réellement reçue

Le code ne modifie que la méthode de réparation ; ACL, règles et manifest sont identiques au dossier initial. Sept tests couvrent tri et égalités, lignes annulées, émis, société active, self, idempotence et utilisateur ordinaire. Le rouge est métier (6 échecs, 0 erreur), pas un incident d’environnement. Le test d’idempotence seul passait déjà avant : la QA le dit honnêtement.

La reprise est effectivement committée sur la copie locale, puis rejouée dans un autre processus. Les valeurs finales 100/200 et20/15 sont relues, les enregistrements exclus restent inchangés. L’utilisateur restreint reçoit bien AccessError. L’oracle ORM indépendant est concordant ; mon verdict se fonde aussi sur le code, les scripts et les inventaires.

Release ouverte, revue/QA/journal/mémoire présents ; aucune livraison distante prétendue. Recette de clôture et vue navigateur ne sont pas revendiquées.

## Relances : ce qui est prouvé

- Événements 7,15 — **avoidable_duplicate** : Same final module hashes, same seven test names and fresh install path; only tag filter omitted. Source contains only this tagged class. Runtime fragment itself admits no other tests; no additional coverage or source change shown.
- Événements 0,1 — **avoidable_recapture** : Identical inventory script rerun, no intervening database mutation in bridge events; second invocation persists the previously only displayed result. Useful durable artifact, avoidable execution by saving first result.
- Événements 3,7 — **justified_after_changes** : Module/tests changed after first green: tuple x2many -> Command, action section/comment and trailing comma. Event7 establishes final-source evidence; not an unchanged-code duplicate.
- Événements 4,5,6 — **justified_checks_of_changed_files** : Each lint follows changed source hashes. First flags tuple command and trailing comma; second tuple warning removed; third trailing comma removed. All retain existing unchanged-manifest author error. Could batch style changes, but no strictly identical redundant lint is proved.
- Événements 8,14 — **different_scope** : Event8 upgrades existing lab_client data copy; event14 tests module upgrade path on separate QA DB. Different environment/path, not duplicate coverage.

**Gain directement étayé : 23,45 s de commandes pont évitables** (22,14 s de QA fraîche identique +1,31 s de recapture d’inventaire), sans extrapoler le temps de raisonnement. Les lints004/005/006 portent sur des empreintes différentes ; la QA007 fixe le vert final après modifications ; la QA014 couvre un chemin de mise à jour différent.

## Réserves localisées

- **S1** : QA verdict/table says static conforme while full lint exit1 remains. Debt is explicitly demonstrated as pre-existing and out of diff, so not a critical failure, but headline should carry the exception. Sources : after-0/changelog/2026-09-15_01_repair/qa.md:49,127-138; bridge-006.log.
- **S2** : Memory claims a post-migrate necessarily affects all companies. The scoped-repair choice is appropriate here, but a migration script can also have a bounded domain. Keep a local authorization rationale rather than a categorical technical rule. Sources : after-0/.odoo-agents/PROJECT.md:7; after-0/changelog/2026-09-15_01_repair/revue_fonctionnelle.md §6 H3.
- **S3** : README justifies tie-break with ids1,4 from different companies, although id4 is filtered out. Correct code and test use SAME1/SAME2 in the same company. Correct the memory example; no functional defect shown. Sources : after-0/changelog/2026-09-15_01_repair/README.md:21; after-0/lab_register/tests/common.py:35-37; after-0/lab_register/tests/test_repair.py:10-17.
- **S4** : Restricted-user probe prints an anomaly instead of failing if denial disappears; currently log does show real AccessError, and independent oracle confirms enforcement. Make future probe assertions fail closed. Sources : after-0/.odoo-agents/flow-artifacts/repair-b42/scripts/droits_restreint.py:29-33; bridge-011.log; oracle.log.

## Adaptation limitée proposée

For this workflow, reuse the final fresh green proof across receipt lanes when source/environment/test names match; save initial observation output immediately. Retain update-path QA and reruns after actual source changes. Put known lint exception in the verdict, and phrase memory as bounded decisions supported by the demonstrated example.

Aucune règle générale sur tous les projets ou tous les modèles n’est déduite de cet essai. Les citations ci-dessus sont relatives à `/tmp/crew-agent-workflows-20260916-v2/N06-claude-reference`.
