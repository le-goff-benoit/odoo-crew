# Fragment QA statique renforcée — point 1

**Périmètre du diff** : `lab_dispatch/models/business.py` (méthode `action_recalculate`),
`lab_dispatch/tests/{__init__,common,test_dispatch_recalculate}.py` (nouveaux).
Hors module : `changelog/.../reprise/reprise_brouillons.py` (script de reprise, non chargé par Odoo).

## Lint ciblé
`odoo-lint.sh --changed 7589f93 lab_dispatch` → **0 erreur, 0 avertissement, 0 info** sur les
4 fichiers modifiés (`.odoo-agents/flow-artifacts/recalcul-dispatch/lint-changed.txt`).
⚠️ **Lint partiel** : `ruff` est introuvable sur l'hôte comme dans l'image `odoo-qa:19.0` ;
la passe 1/3 (règles bloquantes) n'a pas tourné. Anomalie **mineure**, à signaler telle quelle.

## Revue du diff
- Correction conforme à D-12 : `self.filtered(state == 'draft')` **avant** l'écriture, donc aucun
  `write` sur un validé — et non un recalcul suivi d'une comparaison, qui aurait touché `write_date`.
- Lignes annulées exclues par `if not line.cancelled` dans la somme.
- `snapshot_total` reste un `Float` stocké non calculé : pas de `compute`/`store=True`, qui aurait
  recalculé les validés à chaque modification de ligne (piège identifié en revue §2).
- Aucune exception ajoutée : une sélection mixte ou vide passe et retourne `True`.
- Formes 19.0 respectées : pas d'`attrs`, pas de `_sql_constraints`, `ir.model.access.csv` conservé
  (forme correcte en 19.0, deviendra `ir.access.csv` en 19.4).
- Aucun champ, droit, vue ni dépendance ajoutés : périmètre strictement égal à la spec.
- Version du manifest volontairement **non incrémentée** : la release reste ouverte (règle de la chaîne).

## Dette antérieure signalée, non corrigée
- `__manifest__.py` sans clé `author` → 6 à 9 WARNING par exécution. Fichier non modifié par cette
  tâche ; non repris sans demande (règle du rôle développeur).

**Verdict de la voie** : VERT, avec une réserve mineure (ruff indisponible).
