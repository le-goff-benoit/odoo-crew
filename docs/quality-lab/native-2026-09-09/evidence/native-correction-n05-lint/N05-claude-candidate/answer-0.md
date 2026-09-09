```
[4/4 journal]   entrée écrite · PROJECT.md : D-11 écartée + 2 pièges ajoutés · release laissée ouverte
```

# Recalcul fiable des dossiers de dispatch

**Projet** work (Entrepôt Silex, synthétique) · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_recalcul-fiable-des-dossiers-de-dispatch` (point n°1) · **modules** `lab_dispatch`

## À décider
- **Clé `author` absente de `__manifest__.py`** — dette antérieure (présente depuis `HEAD`), elle fait échouer le bloc « contrôles Odoo » du lint et produit un `WARNING` à chaque chargement. Je ne l'ai pas corrigée : la valeur est une donnée d'identité du projet, pas un choix technique. À trancher avant `/odoo-close`.
- **Version du manifest déjà portée à `19.0.1.0.1`**, contrairement à l'usage (incrément à la clôture) : c'est elle qui déclenche la migration, sans quoi la reprise ne s'exécute jamais. `/odoo-close` ne doit pas la réincrémenter. Noté dans `qa.md` et dans les notes de la release.

## Cadrage
À développer : modèles entièrement custom, aucun standard 19.0 en jeu (`snapshot_total` absent des sources). D-11 (journal 2026-08-01, « recalculer tous les dossiers ») est **écartée** par D-12, tracé dans `PROJECT.md`. Hors périmètre : champ calculé, dé-validation, vues, droits.

## Réalisation
- `lab_dispatch/models/business.py` — `_snapshot_amount()` isole le montant hors lignes annulées ; `action_recalculate` filtre les brouillons **avant** la boucle (un validé n'est donc pas écrit du tout, pas seulement « écrit à la même valeur ») ; `_reprise_snapshot_brouillons()` n'écrit que si la valeur diffère et rend les dossiers repris.
- `lab_dispatch/migrations/19.0.1.0.1/post-migrate.py` (nouveau) — porte la reprise, arborescence et déclenchement vérifiés dans `~/odoo-sources/19.0/odoo/modules/migration.py`.
- `lab_dispatch/tests/test_recalculate.py` (nouveau) — 7 tests ; `TestRecalculate` fige `write_date` par SQL pour détecter une écriture même à valeur égale.
- Comparaison **exacte** dans la reprise : `snapshot_total` est un `Float()` sans `digits`, une comparaison arrondie à 2 décimales aurait laissé la dérive `20.004` en base.

## QA de tâche — niveau renforcé (données existantes)
| Contrôle | Résultat |
|---|---|
| Lint ruff (bloquant + conseils) | 0 |
| Lint contrôles Odoo | 1 erreur, dette antérieure (`author`) |
| Test rouge avant correction | `110.0 != 20.0`, `110.0 != 777.0`, reprise absente — 3 failed + 3 errors / 7 |
| Install + update + tests ciblés | 0 failed / 7 |
| Suite complète, base neuve | 0 failed / 7, ERROR/CRITICAL = 0 |
| Reprise sur `lab_client` | 999.0→20.0, 20.004→20.0, validé 777.0 avec `write_date` inchangée |
| Rejeu de la reprise | 0 dossier corrigé, état identique `write_date` comprises |

| Critère | Couvert par | État |
|---|---|---|
| C1 annulées exclues | `test_brouillon_exclut_les_lignes_annulees` | ✅ |
| C2 validé non écrit | `test_valide_reste_strictement_inchange` + `write_date` sur copie | ✅ |
| C3 sélection mixte | `test_selection_mixte` + `search([]).action_recalculate()` sur copie | ✅ |
| C4 pas d'écriture inutile | `test_reprise_idempotente` + rejeu | ✅ |
| C5 idempotence | `test_reprise_idempotente` + `preuves/02_reprise_copie.md` §4 | ✅ |
| C6 état final de la copie | `preuves/02_…` §3, `preuves/06_controle_final_copie.txt` | ✅ |

Aucun test n'a été réécrit entre la passe rouge et la passe verte.

## Reste à faire
- La clé `author` (ci-dessus).
- **Non vérifié** : la conformité en 19.1 / 19.4 — seules `19.0` et `19.0-enterprise` sont présentes dans `~/odoo-sources/`. Signalé dans la revue, risque faible (modèle custom sans équivalent standard).
- Leçon candidate pour `/odoo-feedback` : « figé » signifie *aucune écriture*, pas *même valeur* — filtrer avant la boucle ; et une reprise portée par une migration impose d'incrémenter la version pendant la tâche, ce que la règle « version incrémentée à la clôture » ne prévoit pas.

## Release
1 point dans la release, 1 réalisé. **Release laissée ouverte** comme demandé. Clôture et recette complète : `/odoo-close`.