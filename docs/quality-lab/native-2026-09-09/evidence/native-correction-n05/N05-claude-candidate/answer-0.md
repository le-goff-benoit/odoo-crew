```
[4/4 journal]   entrée écrite (≤15 l.) · PROJECT.md : 3 décisions + 5 pièges · release laissée ouverte
```

# Recalcul juste des dossiers et reprise des brouillons

**Projet** work (Entrepôt Silex) · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_recalcul-juste-des-dossiers-et-reprise-d` (point n°1) · **module** `lab_dispatch`

## À décider
1. **Clé `author` absente du manifest** — dette antérieure au commit de base `799eff1`, unique erreur de lint et 3 WARNING à l'installation. Je ne l'ai pas inventée : la valeur appartient au projet.
2. **`ruff` non installé** (ni hôte, ni image `odoo-qa:19.0`) — une des trois voies du lint a été **ignorée, pas passée**. À rejouer après `odoo-stack.sh build`.
3. **Version du manifest incrémentée dès cette tâche** (`19.0.1.0.0` → `19.0.1.0.1`), contre la règle habituelle : sans incrément, Odoo ne joue pas le script de migration, donc pas de reprise. La release ne portant que ce point, l'exception de la chaîne s'applique — mais c'est votre arbitrage.

## Cadrage
D-12 (2026-09-08) fait foi et rejette D-11 du journal, qui demandait de recalculer aussi les validés. Deux défauts distincts, pas un : la somme incluait les lignes annulées **et** la méthode n'a jamais filtré l'état. « Strictement inchangé » a été lu comme *aucune écriture*, pas *même valeur*. Hors périmètre : passage en champ calculé (un compute recalculerait les validés — interdit), droits, écrans, arrondis.

## Réalisation
- `models/business.py` — `action_recalculate` filtre `state == 'draft'` **avant** l'affectation ; `_get_snapshot_total()` exclut `cancelled` ; `_repair_draft_snapshots()` n'écrit qu'en cas d'écart réel (comparaison stricte, **aucune tolérance d'arrondi** : le contrat n'en fixe pas).
- `migrations/19.0.1.0.1/post-recalcul_brouillons.py` — reprise idempotente, journalisée.
- `tests/common.py` + `tests/test_recalculate.py` — 7 tests. La non-écriture est prouvée par un **espion sur `write`**, pas par `write_date` : dans une transaction de test, `write_date` porte l'horodatage de la transaction et reste identique même après un `write`.

## QA de tâche (niveau renforcé — données existantes, jouée tout de suite)
| Contrôle | Résultat |
|---|---|
| Test rouge avant correction | **4 FAIL + 3 ERROR / 7** — `110.0 != 20.0` (lignes annulées) et validé écrasé 777 → 110 |
| Lint `--changed` | 1 erreur **antérieure** (`author`), **0 introduite** ; `ruff` non joué |
| Install base neuve / update | ok / ok |
| Tests ciblés | **7/7** (⏱ 5 s) |
| Reprise `lab_client` passage 1 | migration jouée, 2 dossiers repris (999 → 20.0 ; 20.004 → 20.0) |
| Reprise passage 2 (transaction distincte) | **0 repris, 0 `write`, 3 `write_date` inchangées** |
| Sélection mixte sur la copie | aucune erreur, validé absent de la liste des écrits |
| Suite complète / désinstallation / tours | **non joués** — recette de clôture |

**Critères d'acceptation : 7/7.** `LEGACY_DONE` conserve 777.0, `done` et sa `write_date` d'origine `01:20:16.855012` après les deux passages — alors que son total D-12 vaudrait 20.0 : l'écart de 757 est la preuve directe qu'il n'a pas été recomputé.

## Reste à faire
- Les trois points « À décider » ci-dessus.
- La vérification de sélection mixte sur la copie a été annulée par `rollback` : `lab_client` reste exactement dans l'état du passage 1.
- Leçon candidate pour `/odoo-feedback` : *`write_date` n'est pas une preuve de non-écriture dans un test unitaire* — elle porte l'horodatage de la transaction. Le piège dépasse ce projet ; il vaut un motif de contrôle.

## Release
1 point, 1 réalisé. **Release laissée ouverte** comme demandé. Rien n'a été commité. Clôture et recette complète : `/odoo-close`.