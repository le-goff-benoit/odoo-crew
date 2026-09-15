# Journal

## 2026-09-14 — Ancienne QA
**Fait** : tests de création simples verts ; ni données historiques, ni sélection mixte.
**Reste ouvert** : demande actuelle et reprise.

## 2026-09-16 — Correctif `action_repair` (B-42), release 2026-09-15_01_repair
**Demande** : réparer `action_repair` de `lab.register` et reprendre les brouillons existants de la société initiale de la copie synthétique ; autorisation locale seulement.
**Fait** : méthode limitée à `self`, brouillons de `env.company`, tri `date_document, id`, séquences 100/200, `snapshot_total` hors lignes annulées ; `search([])` et `sudo()` supprimés. Tests neufs `lab_register/tests/`. Reprise jouée sur `lab_client` sous `n06_operator` (utilisateur ordinaire, multi-société) : id1 20→100 / 999.0→20.0, id2 10→200 / 123.0→15.0 ; émis et société 2 « champs modifiés: AUCUN ».
**Verdict** : QA de tâche **VALIDÉ SOUS RÉSERVE** — 8 critères sur 8 prouvés ; réserve documentaire sur la portée de l'idempotence. Rouge 5/6 puis vert 6/6, même suite (`preuves/qa-repair-rouge-final.*`, `qa-repair-vert.*`). Ruff bloquant propre.
**Appris** : un `qa.md` marqué « PASS » sans portée écrite se lit comme une réception de release ; celui du 14/09 ne couvrait qu'une création vide et masquait C1-C8. Un test d'idempotence peut être vert sur du code faux : il l'était déjà sur la méthode d'origine. Le rejeu conserve les valeurs mais écrit quand même (`write_date` bouge) — l'idempotence prouvée est celle du résultat.
**Reste** : release **ouverte** — recette complète, incrément du manifest et livrables documentaires reviennent à `/odoo-close`. Dette antérieure non reprise : clé `author` absente du manifest, 2 `unsorted-imports`. Leçon candidate pour `/odoo-feedback` : une QA antérieure « PASS » doit porter sa portée, sinon elle est réputée ne rien réceptionner.
