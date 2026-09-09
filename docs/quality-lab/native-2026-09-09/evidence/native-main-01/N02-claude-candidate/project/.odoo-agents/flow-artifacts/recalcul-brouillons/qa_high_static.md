# Fragment QA statique renforcée — lab_dispatch

**Périmètre** diff depuis `7589f933cb838a3d5a7691c5253ad3e47f1bad77`, série 19.0.

## Lint des fichiers touchés
`odoo-lint.sh --changed <base> /work/lab_dispatch` → **✅ lint OK**, 5 fichiers,
ruff bloquant « All checks passed », conseils : aucun, contrôles Odoo 0/0/0.
Preuve : `preuves/lint_changed.log`.
Réserve levée en cours de tâche : ruff était absent de l'hôte au premier passage
(lint « partiel ») ; installé (`ruff-0.16.6`), le lint a été rejoué complet.

## Revue du diff
| Point | Constat |
|---|---|
| `action_recalculate` | filtre `state == 'draft'` **avant** toute assignation → aucune écriture sur un validé (conforme au risque n°2 de la revue) ; somme restreinte à `not line.cancelled` |
| Forme 19.0 | pas d'`attrs`/`states`, pas de `_sql_constraints`, pas de `self._cr` ; aucun XML ni sécurité modifiés — rien qui touche les formes de série |
| Docstring | présente, en anglais comme le reste du code, explique le *pourquoi* du filtre préalable |
| Périmètre | aucun champ, modèle, droit ni vue ajouté ; `snapshot_total` reste un `Float` simple (dette `digits` signalée en revue, non traitée) |
| Hors périmètre assumé | `'author': 'Camptocamp'` ajouté au manifest : clé obligatoire manquante qui rendait le lint rouge et produisait un WARNING à chaque chargement. Valeur à confirmer par l'humain. |
| Version du manifest | inchangée (19.0.1.0.0) — correct, la release reste ouverte, l'incrément se fait à la clôture |
| Tests | `tests/__init__.py`, `tests/common.py` (`LabDispatchCommon`), `tests/test_recalculate.py` `@tagged('post_install', '-at_install')` ; aucun attribut de classe nommé `run` |
| Reprise | script versionné dans la release, aucune écriture sur les validés, `assert` de garde + `commit()` explicite |

## Verdict de voie
**VERT** — rien à reprendre côté statique.
