<!-- release ouverte -->
# Correction locale synthétique

## Suivi des points

| # | Point | Test ciblé | État |
|---|---|---|---|
| 1 | Préparation périodique, duplication et reliquat (N-17) | /bridge/labctl qa lab_preparation --quick --tags /lab_preparation | QA renforcée verte 12/12 ; reprise appliquée sur lab_client |

## Points de la release

### Point 1 — Préparation périodique, duplication et reliquat (décision N-17) — 2026-09-16
- **Demande** : `demande.md` · **contrat** : `decisions/current.md` (N-17)
- **Revue** : `revue_fonctionnelle.md` · **QA** : `qa.md`, `qa_tache_preparation_n17.md`, `qa_coverage.json`
- **Code** : `lab_preparation/models/business.py`, `lab_preparation/tests/`,
  `lab_preparation/migrations/19.0.1.1.0/post-migrate.py`, manifest 19.0.1.0.0 → 19.0.1.1.0
- **État** : tâche reçue, QA renforcée verte (12/12). **Release laissée ouverte.**

### Notes de travail
- 2026-09-16 — La version du manifest est incrémentée **maintenant**, contrairement à l'usage
  (incrément unique à la clôture) : sans elle, le `post-migrate` de reprise ne s'exécute pas.
  À la clôture, vérifier qu'on ne l'incrémente pas une seconde fois pour rien.
- 2026-09-16 — Reset à la duplication porté par `copy=False` sur les champs plutôt que par une
  surcharge de `copy_data()` : forme la plus simple, vérifiée dans `odoo/orm/models.py` l.5434.
- 2026-09-16 — Piste écartée : ajouter un garde « ne pas réécrire si la valeur est identique »
  dans le cron. Cela rendrait l'idempotence littérale jusque dans la `write_date`, mais N-17
  interdit d'inventer un comportement ; la limite est documentée dans `qa.md` à la place.
- 2026-09-16 — Dette antérieure non reprise : clé `author` absente du manifest (lint rouge).
- 2026-09-16 — Le premier run de flow (`preparation-n17`) a été ouvert sur la transition `module`
  alors que la reprise de données existantes impose `module_high_risk` ; il a été abandonné après
  `release` de son verrou et rejoué sous `preparation-n17-hr`, sur la voie renforcée.
