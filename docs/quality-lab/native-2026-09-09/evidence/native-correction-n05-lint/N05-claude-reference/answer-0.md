**[4/4 journal]** entrée écrite · PROJECT.md : 2 pièges ajoutés · release laissée ouverte

---

# Recalcul fiable des dossiers en brouillon (`lab.dispatch`)

**Projet** Entrepôt Silex · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_recalcul-fiable-des-dossiers-en-brouillo` (point n°1) · **module** `lab_dispatch`

## À décider (à la clôture)
- `__manifest__.py` n'a pas de clé `author` — **dette antérieure** au commit de base `d6b5c10`, seul point rouge du lint complet. Non corrigée pour ne pas inventer une valeur d'éditeur.
- La reprise est un script rejouable dans la release, pas un script de migration : son emballage dans `migrations/` dépend de l'incrément de version, qui se fait à la clôture.

## Cadrage
Deux défauts distincts vivaient dans la même ligne : les lignes annulées étaient comptées, **et** les dossiers validés étaient écrasés. Développement justifié (aucun standard ne couvre ce modèle propre au projet). Le total figé reste volontairement un champ simple : un champ calculé stocké recalculerait les validés et violerait D-12. Hors périmètre : vues, droits, correction des totaux validés, changement d'état.

## Réalisation
- `lab_dispatch/models/business.py` — `action_recalculate` filtre sur `state == 'draft'` ; le total passe par `_get_lines_total()`, qui exclut `cancelled`.
- `lab_dispatch/tests/test_dispatch_recalculate.py` — 5 tests (nouveau).
- `changelog/…/reprise/reprise_brouillons.py` — reprise idempotente, comparaison **exacte** des totaux.

## QA de tâche (niveau sensible : données existantes → trois voies, immédiate)
| Contrôle | Résultat |
|---|---|
| Test rouge du défaut | **4 échecs / 5** avant correction (110.0 ≠ 20.0 ; 110.0 ≠ 777.0) |
| Tests ciblés, base neuve | 5/5 verts |
| Install / update | `install=ok update=ok` |
| Lint ruff (config 19.0) | vert sur le diff ; 1 erreur de dette antérieure |
| Reprise sur `lab_client` | passe 1 : 2 modifiés (999.0 → 20.0 ; 20.004 → 20.0) · passe 2 : **0 modifié** |

Les 6 critères d'acceptation sont couverts. `LEGACY_DONE` reste à 777.0, `write_date` comprise, y compris après une action jouée sur une sélection mixte des trois dossiers.

Le piège de la reprise était `LEGACY_FRACTION` à 20.004 : une comparaison avec tolérance à deux décimales l'aurait déclaré conforme et laissé faux. La comparaison exacte le corrige, et la seconde passe prouve qu'elle ne réécrit rien.

## Reste à faire
Les deux points « À décider ». Observation sans effet sur le contrat : recalculer un brouillon déjà conforme met tout de même à jour sa `write_date`.

## Release
1 point, 1 réalisé. **Release laissée ouverte**, comme demandé — clôture et recette complète : `/odoo-close`. Rien n'a été commité ; toutes les écritures sont restées sur `/work` et la copie synthétique `lab_client`.