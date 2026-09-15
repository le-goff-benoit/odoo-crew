# Journal

## 2026-09-14 — Ancienne QA
**Fait** : tests de création simples verts ; ni données historiques, ni sélection mixte.
**Reste ouvert** : demande actuelle et reprise.

## 2026-09-16 — Préparation périodique, duplication et reliquat (décision N-17)
**Demande** : corriger `_cron_prepare`, `copy()` et `action_remainder()` de `lab_preparation`
selon `decisions/current.md`, reprendre les drafts automatiques de la copie, tests rouge/vert.
**Fait** : cron borné aux drafts `manual=False` avec `max(ordered-delivered, 0)` ;
`action_set_manual` marque `manual=True` même à zéro ; `copy=False` sur `delivered_qty`,
`prepared_qty`, `manual`, `state` ; `action_remainder` crée le reste uniquement s'il est positif
et clôt la source sans écraser sa `prepared_qty`. Reprise par `migrations/19.0.1.1.0/post-migrate.py`
(manifest 19.0.1.0.0 → 19.0.1.1.0, incrément nécessaire pour déclencher la migration).
**Verdict** : QA renforcée VERTE, 12/12 critères (`changelog/2026-09-15_01_repair/qa.md`).
Rouge d'abord prouvé : 9 échecs sur 11 avant correction. Sur `lab_client`, id 1 : 999 → 7 ;
ids 2, 3, 4 sans aucun `write` (`write_date` d'origine conservée).
**Appris** : sur ce modèle, `manual` est un drapeau de saisie, pas un « prepared_qty non nul » —
c'est la confusion qui écrasait les zéros volontaires.
**Reste** : release **ouverte** ; lint du module rouge sur une dette antérieure (clé `author`
absente du manifest) ; hypothèse H1 (source close même sans reste) à confirmer par le métier ;
aucun `ir.cron` livré ; aucun déploiement.
