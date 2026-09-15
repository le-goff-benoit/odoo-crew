# Journal

## 2026-09-14 — Ancienne QA
**Fait** : tests de création simples verts ; ni données historiques, ni sélection mixte.
**Reste ouvert** : demande actuelle et reprise.

## 2026-09-16 — action_repair (décision B-42) et reprise de la société initiale
**Demande** : réparer `action_repair` de `lab.register` et les brouillons existants de la société initiale de la copie.
**Fait** : périmètre ramené à `self` × `draft` × `env.company`, tri `date_document, id`, pas de 100, `snapshot_total` hors lignes annulées, `sudo()` retiré ; sécurité et manifest inchangés. Reprise jouée sur `lab_client` sous `n06_operator` (ordinaire, 2 sociétés activées), sélection mixte.
**Verdict** : QA de tâche **renforcée VALIDÉE** (C1→C9). Rouge 6/7 sur le code d'origine puis vert 7/7 ; `update=ok` ; reprise rejouée dans un second processus, `diff` vide ; `n06_restricted` (ordinaire) répare sans `sudo()` et se voit refuser la société 2.
**Appris** : (1) un `qa.md` titré `PASS` dont la portée est écrite en dessous vaut un `INCOMPLET` — l'ancienne recette du 14.09 est reclassée en historique non réceptionnant ; (2) `test_repair_is_idempotent` passait **déjà** sur le code fautif : l'idempotence seule ne prouve pas un contrat de périmètre ; (3) un `post-migrate` a été écarté, il aurait touché toutes les sociétés de toute base, ce que B-42 interdit.
**Reste ouvert** : release `2026-09-15_01_repair` **ouverte** — recette complète, incrément de version et livrables à `/odoo-close` ; dette antérieure `__manifest__.py` sans clé `author` à arbitrer. Rien n'est commité ni poussé.
