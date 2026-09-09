`[4/4 journal]` entrée écrite · `PROJECT.md` : D-12 actée + 3 pièges ajoutés · release **laissée ouverte**

---

# Recalcul juste des dossiers en brouillon

**Projet** Entrepôt Silex · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_recalcul-juste-des-dossiers-en-brouillon` (point n°1) · **module** `lab_dispatch`

## À décider
- **Faux vert de l'outillage** (majeure, hors module) : `labctl qa … --quick` a rendu « installation, tests et logs propres » avec **0 test collecté**. Cause prouvée : sur une base clonée du gabarit, `odoo-test.sh` choisit `-u`, or le module n'y est pas installé — `-u` est alors un no-op, `registry.updated_modules` est vide et `make_suite` ne collecte rien. Contourné par le chemin complet. Leçon candidate pour `/odoo-feedback`.
- `ruff` introuvable (hôte et image `odoo-qa:19.0`) : le lint est **partiel**, la passe « règles bloquantes » n'a pas tourné.

## Cadrage
Aucun équivalent standard en 19.0 (`lab.dispatch` est entièrement custom) : correctif de logique métier. Contradiction tranchée : D-11 du journal (« recalculer tous les dossiers ») est caduque, D-12 fait foi — validés figés, lignes annulées exclues. Hors périmètre : reconstruire les validés, droits, déploiement, tout livrable documentaire.

## Réalisation
- `lab_dispatch/models/business.py` : `filtered(state == 'draft')` **avant** l'écriture (et non un recalcul suivi d'une comparaison, qui toucherait `write_date`), somme restreinte aux lignes `cancelled = False`. `snapshot_total` reste stocké **non calculé** — un `compute … store=True` recalculerait les validés.
- `lab_dispatch/tests/` : `common.py` + 7 tests couvrant C1–C6 et le recordset vide.
- `changelog/…/reprise/reprise_brouillons.py` : reprise rejouable, n'écrit que les brouillons divergents, refuse de committer si un validé bouge.
- Version du manifest volontairement non incrémentée (release ouverte).

## QA de tâche — niveau **renforcé** (données existantes), 3 voies
| Contrôle | Résultat |
|---|---|
| Test rouge avant correction | **6 échecs / 7** — défaut prouvé |
| Lint `--changed` | 0 erreur, 0 avertissement · ⚠️ partiel (ruff absent) |
| Install `-i` / update `-u` sur `lab_qa` neuve | ok / ok |
| Tests ciblés | **7/7 verts**, 0 ERROR |
| Reprise sur `lab_client` — passe 1 | 1 écriture (999,00 → 20,00) |
| Reprise — passe 2 rejouée | **0 écriture** → idempotence prouvée |
| Validé id=2 | 777,00 et `write_date` inchangés |

Les 7 critères d'acceptation sont couverts et vérifiés un par un dans `qa.md`.

## Reste à faire
- Anomalies mineures non corrigées : `author` absent du manifest (dette antérieure, fichier non touché) ; `action_recalculate` réécrit un brouillon même à valeur inchangée (conforme au contrat, à arbitrer si un tracking apparaît).
- Le test C3 n'est discriminant que parce qu'il repousse `write_date` dans le passé : dans une même transaction elle vaut déjà l'horodatage de la transaction — ma première version passait à tort sur le code buggé.

## Release
1 point, 1 réalisé. **Release laissée ouverte** comme demandé ; recette complète, captures, guide et incrément de version à la clôture : `/odoo-close`. Rien n'a été commité.