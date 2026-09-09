`[4/4 journal]` entrée écrite · `PROJECT.md` : D-03 fait foi, D-02/D-01 historisées, 4 pièges ajoutés sur les reprises. Les preuves du point n°1 sont intactes (préfixe `d03_` pour les nouvelles), le run de flow précédent n'a pas été touché.

---

# Frais de préparation D-03 — remplace D-02

**Projet** Atelier Boréal · **série** 19.0 (origine `__manifest__.py`) · **release** `changelog/2026-09-09_01_frais-de-preparation-des-locations` (point n°2, **ouverte**) · **module** `lab_rental`

## À décider
- **R1 (report du point n°1)** — `author = 'Camptocamp'` dans le manifest reste une valeur supposée. Sans effet fonctionnel.
- **Communication de clôture** : la release contient deux points contradictoires. Le comportement livré est **D-03 seule**. J'ai marqué le point n°1 « REMPLACÉ » dans le suivi et noté que la communication ne doit **pas** annoncer 12 EUR à 4 jours. À confirmer à la clôture.

## Cadrage
D-03 ne change que deux paramètres d'une règle déjà livrée (12→15 EUR, seuil 4→5 jours) ; aucune question bloquante, tout est tranché dans `decisions/2026-09-09.md`. Verdict standard inchangé depuis le point n°1 : rien en Community, `sale_renting` est Enterprise et ne porte pas ce forfait. Hors périmètre : facturation, compta, `Monetary`, écrans, droits, positivité de `days`/`daily_rate`.

## Réalisation
- `models/business.py` — `PREPARATION_FEE 12.0 → 15.0`, `PREPARATION_FEE_MIN_DAYS 4 → 5`. Structure inchangée : les constantes nommées du point n°1 ont réduit le changement à deux lignes.
- `migrations/19.0.1.2.0/post-migrate.py` — **nouveau**. `migrations/19.0.1.1.0/` conservé.
- `__manifest__.py` — `19.0.1.1.0 → 19.0.1.2.0`.
- `tests/test_preparation_fee.py` — 11 tests **réécrits** (les 9 anciens attestaient D-02, ils étaient devenus faux).

## QA de tâche (renforcée, 3 voies)
| Contrôle | Résultat |
|---|---|
| Lint `--changed` | 0 erreur, 0 conseil, 0 info |
| Install base neuve / update | ok / ok |
| Tests ciblés | **11/11** |
| Rouges sur les constantes D-02 | **6/11** (discrimination prouvée) |
| Reprise exécutée ? | `Running upgrade [19.0.1.2.0>] post-migrate`, version installée → `19.0.1.2.0` |
| Reprise sur `lab_client` | 3/7 repris dont **2 à la baisse**, delta net **−21,00 EUR** (296,00 → **275,00**), prêts intacts, **0 écart** vs prédiction |
| Idempotence | rejouée 2×, totaux identiques |

**13/13 critères d'acceptation couverts.** Verdict : **VALIDÉ**, portée **locale** (base de QA neuve + copie synthétique) — ni recette complète, ni désinstallation, ni production, ni déploiement.

**Pourquoi la première QA ne suffisait pas** — trois causes mesurées, pas une formalité : les tests du point n°1 attestaient l'inverse de D-03 ; la reprise `19.0.1.1.0` était **inerte** (version installée sur `lab_client` = version du manifest, lue avant de coder), donc un `-u` aurait laissé les totaux D-02 **sans aucune erreur** ; et la correction va **dans les deux sens**, ce qui exige une reprise qui réapplique la formule au lieu d'ajouter un delta.

## Reste à faire
- **Non mesuré** : la chaîne `19.0.1.0.0 → 19.0.1.2.0` en un seul `-u` (les deux reprises d'affilée sur une base neuve). Devrait converger, non prouvé — noté pour la clôture.
- Ne pas supprimer `migrations/19.0.1.1.0/` ni redescendre la version du manifest.
- `lab_client` est synthétique (7 enregistrements) : le mécanisme est prouvé, pas le comportement sur un parc réel ; la reprise mériterait un traitement par lots à grande échelle.
- **Leçon candidate pour `/odoo-feedback`** : « une reprise déjà consommée est inerte — deux changements de règle dans une même release exigent deux dossiers de migration et deux incréments ; la version installée se lit sur la copie ». Généralisable au-delà de ce projet, et candidate à un motif de lint (`post-migrate` ajouté sans incrément de version).

## Release
2 points, 2 réalisés — le n°1 remplacé par le n°2. Release **volontairement laissée ouverte** ; recette complète, désinstallation, captures et communication client : `/odoo-close`.