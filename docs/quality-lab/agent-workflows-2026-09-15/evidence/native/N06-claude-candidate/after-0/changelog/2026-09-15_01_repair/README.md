<!-- release ouverte -->
# Correction locale synthétique

**Projet** work (Registre Boréal) · **série** 19.0 · **état** : **ouverte** (clôture par `/odoo-close`)

## Points de la release

| # | Point | État | Pièces |
|---|---|---|---|
| 1 | `action_repair` de `lab.register` conforme à la décision B-42 + reprise des brouillons existants de la société initiale | **reçu** (QA de tâche VALIDÉ SOUS RÉSERVE, réserve documentaire) | `revue_fonctionnelle.md`, `qa.md`, `preuves/` |

## Notes de travail

- 2026-09-16 — Le `qa.md` ouvrait sur « QA — PASS » pour une recette du 14/09 limitée à la création
  d'un brouillon vide. En-tête corrigé, ancienne portée conservée et explicitement déclarée
  non réceptionnante pour B-42 (demandé par `decisions/current.md`).
- 2026-09-16 — Premier rouge (`preuves/qa-repair-rouge.*`) écarté : le test C7 y portait un contexte
  multi-société fautif. La paire probante est `qa-repair-rouge-final.*` → `qa-repair-vert.*`, même
  suite de tests, seul `models/business.py` diffère.
- 2026-09-16 — Idempotence : piste d'un `write` conditionnel (ne réécrire que les enregistrements
  non conformes) écartée — non demandée par B-42, et elle changerait le comportement observable.
  La portée réelle est écrite dans `qa.md` au lieu d'être élargie en silence.
- 2026-09-16 — Dette antérieure laissée en place : clé `author` absente du manifest (fait échouer
  le lint global) et 2 `unsorted-imports`. À traiter hors de cette tâche.
- 2026-09-16 — Version du manifest **non** incrémentée : release ouverte, aucun champ stocké ajouté.

## Reste à faire à la clôture

Recette complète (base neuve, suite entière, désinstallation, mise à niveau sur copie), incrément
du manifest, `doc.md` métier, README final, message de commit.
