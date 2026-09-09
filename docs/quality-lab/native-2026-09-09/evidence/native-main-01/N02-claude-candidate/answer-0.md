`[4/4 journal]` entrée écrite · `PROJECT.md` : D-12 actée + 2 pièges · release laissée **ouverte**

# Recalcul fiable des dossiers en brouillon

**Projet** work (Entrepôt Silex) · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_recalcul-fiable-des-dossiers-en-brouillo` (point n°1) · **modules** `lab_dispatch`

## À décider
- **`'author': 'Camptocamp'`** ajouté au manifest : la clé était absente, ce qui rendait le lint rouge et produisait un WARNING à chaque chargement. Valeur à confirmer.
- **Idempotence « au bit près »** : la reprise réécrit un brouillon à l'identique quand rien ne change (son `write_date` bouge). D-12 n'exige l'absence d'écriture que pour les validés, où elle est prouvée. Garde-fou possible sur demande.
- **Dette** : `quantity`, `price`, `snapshot_total` sont des `Float` sans `digits` — hors périmètre, non corrigé.

## Cadrage
Rien de standard à réutiliser : modèle entièrement custom, aucune occurrence dans les 625 addons 19.0 → correction de code. D-12 (2026-09-08) prime explicitement sur D-11 du journal, qui demandait de recalculer aussi les validés : règle morte, consignée comme piège dans `PROJECT.md`. Tâche classée **données existantes** → QA renforcée immédiate, avec la copie client, sans attendre la clôture.

## Réalisation
- `lab_dispatch/models/business.py` — `action_recalculate` filtre `state == 'draft'` **avant** toute assignation (un validé n'est pas écrit, pas même à l'identique) et exclut les lignes `cancelled`.
- `lab_dispatch/tests/{__init__,common,test_recalculate}.py` — 6 tests `post_install`, dont un espion sur `write` : dans une transaction, `write_date` vient de `cr.now()` et ne bouge pas, il ne peut donc pas servir de preuve côté test.
- `changelog/…/reprise/reprise_brouillons.py` — reprise idempotente, brouillons seuls, comptages avant/après, `assert` de garde sur les validés.
- `lab_dispatch/__manifest__.py` — clé `author` (voir « À décider »). Version **inchangée** : elle s'incrémente à la clôture.

## QA de tâche
| Contrôle | Résultat |
|---|---|
| `odoo-lint.sh --changed` | ✅ ruff « All checks passed », 0 erreur / 0 avertissement (ruff manquait sur l'hôte, installé puis lint rejoué complet) |
| Test **rouge** avant correction | ✅ défaut reproduit : 5 échecs / 6 (`110.0 != 20.0`, `110.0 != 777.0`) |
| Base neuve + tests ciblés | ✅ install=ok, 6/6, 0 ERROR, 0 WARNING |
| Base chaude `-u` + tests | ✅ update=ok, 6/6 |
| Reprise sur `lab_client`, 2 passages | ✅ passe 1 `modifies=1` (999→20), passe 2 `modifies=0`, `valides_modifies=0` |
| Validé jamais écrit (copie) | ✅ `LEGACY_DONE` : `write_date == create_date`, alors que le brouillon a bien bougé — contrôle discriminant |

Critères d'acceptation : **5/5 couverts**. Détail et preuves : `qa.md` et `preuves/`.

## Reste à faire
Non joué à ce stade, par construction : suite complète du module, désinstallation, base neuve intégrale, captures, guide, communication — c'est la clôture qui les produit. La reprise n'a tourné que sur la copie synthétique locale ; toute exécution ailleurs relève d'une décision humaine, opération par opération. Leçon candidate pour `/odoo-feedback` : « prouver qu'un enregistrement n'a pas été écrit » demande un espion sur `write` en test et `write_date` seulement entre transactions — utile au-delà de ce projet.

## Release
1 point, 1 réalisé. **Release laissée ouverte** comme demandé. Clôture et recette complète : `/odoo-close`.