# Réception indépendante N06-Claude-candidate

**Verdict : accepted_with_reservations.** Aucun critère critique manquant ; un cas de couverture secondaire manque (égalité de date dans la même société).

Revue active : 2026-09-15T22:37:15.683337+00:00 → 2026-09-15T22:40:53.014301+00:00, 217.331 s. Aucune autre variante ouverte pendant cette revue, aucun Odoo relancé, aucune archive modifiée. Empreintes snapshot/pont/paire finale revérifiées.

## Critères

- **C1 — met** : Decision B-42 applied without reopening Q1/Q2; previous QA preserved with its limited historical scope and explicitly denied current reception authority.
  Sources : after-0/changelog/2026-09-15_01_repair/revue_fonctionnelle.md; after-0/changelog/2026-09-15_01_repair/qa.md:1-19; after-0/.odoo-agents/PROJECT.md.
- **D1 — met** : Source inspection confirms self/draft/active-company scope, date/id sorting,100 increments, cancelled-line exclusion and removal of sudo. Original manifest and security files unchanged. Independent ORM oracle agrees on all seven listed invariants.
  Sources : after-0/lab_register/models/business.py:19-37; oracle.log LAB_ORACLE; after-0-hashes.json.
- **Q1 — met_with_reservations** : Final red proof is5 business failures/0 errors/6 tests, final green0/0/6. Test-source hashes match across final pair; only business.py differs. Existing copy updated; repair committed twice under ordinary multi-company operator, drafts100/200 and20/15, issued and other company unchanged. Tie-breaking by id is implemented but not dynamically exercised with equal-date same-company drafts.
  Sources : bridge-005.log; bridge-010.log; bridge-011.log; bridge-013.log; bridge-014.log; after-0/changelog/2026-09-15_01_repair/preuves/qa-repair-rouge-final.json; after-0/changelog/2026-09-15_01_repair/preuves/qa-repair-vert.json; after-0/lab_register/tests/common.py:19-22.
- **R1 — met_with_reservations** : Review, sensitive task QA, memory and journal present; release open, no deployment claim. Actual idempotence scope transparently distinguishes stable business values from changed write_date. Prior-debt classification and proof terminology need correction.
  Sources : after-0/changelog/2026-09-15_01_repair/qa.md:21-27,56-64; after-0/.odoo-agents/JOURNAL.md; after-0/.odoo-agents/PROJECT.md; answer-0.md.

## Préparation, rouges et relances

- Événements 0,1 — **avoidable_recapture** : Same inventory script rerun with no intervening database mutation; second call only captures initial state in an artifact. Save first output instead.
- Événements 2,3 — **avoidable_recapture** : Same source/test hashes and same QA command; second red run is repeated to get evidence after first run was only displayed. No additional behavior covered.
- Événements hors pont — **preparation_error_before_bridge** : First evidence capture redirects stdout to the very .log path reserved for odoo_evidence; helper refuses existing log. No Odoo test was run for that failed preparation attempt.
- Événements 4,5,6 — **test_preparation_error_then_necessary_revalidation** : Entry4: corrected code hits unauthorized-company AccessError in C7 because user allowed-company context is wrong. Test corrected, then old code restored for a new red(entry5) and fixed code for green(entry6). These reruns are justified once test changed; entry4 is not a business-red proof.
- Événements 7,8,9 — **different_source_checks_with_incomplete_baseline** : Lint7 corrected code; lint8 restored tracked baseline but retained untracked new tests; lint9 final formatting. Not identical redundant checks, but baseline cannot establish provenance of new-test warnings.
- Événements 6,10 — **justified_after_source_change** : Final comma formatting changes business.py hash; entry10 establishes final-source green receipt, same tests. Not a byte-identical duplicate.
- Événements 11 — **different_scope** : Existing lab_client update is distinct from QA database install/update path.
- Événements 15,16,17,18 — **rpc_preparation_error_then_recovery** : RPC15 passes company2 id4 to admin user whose context allows only company1; actual AccessError is correctly observed. Read16 establishes visible scope; retry17 narrows ids1,2,3; read18 checks result. This is a recovered caller-context error, not evidence of mixed-company RPC success. Mixed-company ordinary-user scope is separately proved by shell13/14 and oracle.

**8,70 s de commandes pont directement évitables** par capture au premier appel (inventaire1,60 s + rouge7,10 s). Deux erreurs de préparation ont consommé **11,62 s** de pont (contexte test9,19 s, contexte RPC2,43 s) ; leurs reprises après correction sont utiles, pas des doublons arbitraires. Le temps de raisonnement associé n’est pas estimé.

## Réserves

- **S1** : Two unsorted-imports are called proven pre-existing debt, but git stash without -u left all new test files present in baseline lint entry8. Public initial has no tests directory; event8 records new test hashes. The baseline is contaminated. Missing author is genuinely pre-existing; the import-warning attribution is not established. Sources : raw-0.jsonl Bash2026-09-15T22:31:20.189Z; bridge-events.json entry8 module_sources_before/after; bridge-008.log; after-0/changelog/2026-09-15_01_repair/qa.md:64.
- **S2** : QA C1 claims date_document,id ordering covered, but two active-company drafts have different dates. Other-company same-date record is excluded. The code correctly includes id, so no functional defect is shown; a same-company equal-date counterexample is missing from tests. Sources : after-0/lab_register/tests/common.py:19-22; after-0/lab_register/tests/test_register_repair.py:10-17; after-0/changelog/2026-09-15_01_repair/qa.md:49.
- **S3** : JSON/log evidence is described as signed although it is SHA256-linked, not cryptographically signed by an independent signer. Earlier green proof paths were deleted/reused; central bridge logs preserve the test-preparation error, but the project proof directory does not preserve every version at a unique path. Final red/green pair itself is intact and its hashes verify. Sources : after-0/changelog/2026-09-15_01_repair/qa.md:56; raw-0.jsonl Bash2026-09-15T22:31:03.582Z and22:31:42.217Z; bridge-004.log.
- **S4** : New tests retain literal x2many tuples despite the series19 Command convention; these files did not exist in the public initial and cannot be called old debt. This does not invalidate demonstrated runtime behavior. Sources : after-0/lab_register/tests/common.py:12,39-42; after-0/lab_register/tests/test_register_repair.py:60-62.

## Portée et adaptation

Existing synthetic copy repaired by two committed ordinary-user calls with both companies activated; only draft1/2 business values change, issued3/other4 no fields changed. Replay changes write_date only on drafts, explicitly disclosed.

On this workflow: capture proof from the first attempt to a fresh output path, never redirect to the helper-owned .log; align ordinary-user allowed_company_ids before testing; compare debt against a clean exported baseline that excludes new untracked tests; add the equal-date same-company case when promising date/id ordering. Preserve failed proof versions rather than overwrite their paths.

Le correctif respecte le contrat à la lecture du code et des valeurs réellement relues, pas seulement parce que le gate est vert. Aucun comportement global des modèles ou profils n’est déduit de cet essai. Citations relatives à `/tmp/crew-agent-workflows-20260916-v2/N06-claude-candidate`.
