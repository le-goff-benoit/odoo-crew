# Fragment QA d'exécution — contrainte days >= 0

## Base de QA neuve (`lab_qa`) — `labctl qa lab_rental --quick --tags /lab_rental:TestDaysConstraint`
- Installation `-i lab_rental` : OK · 21 modules chargés.
- Tests : **7 exécutés, 0 échec, 0 erreur** (⏱ 13 s).
- Logs : 0 ERROR / 0 CRITICAL ; 3 WARNING, tous « Missing `author` key » (dette antérieure).
- Ligne de recette : `install=ok tests="0 failed, 0 error(s) of 7 tests" errors=0 failed=0`.

## Copie existante (`lab_client`) — mise à niveau
- État avant : table `lab_rental` vide, aucune contrainte CHECK. Deux locations légitimes
  créées pour la QA (3 jours / 60.0 et 0 jour / 0.0) afin d'éprouver la migration sur des données.
- `labctl update` : module rechargé, `creating or updating database tables` sans erreur —
  l'`ADD CONSTRAINT` passe, **les deux lignes existantes sont conservées**.
- Contrainte réellement posée en base : `lab_rental_days_positive` → `CHECK ((days >= 0))`.
- Rejeu manuel sur la copie :
  - `create({'days': -1})` → `IntegrityError: violates check constraint "lab_rental_days_positive"` ✅
  - `write({'days': -4})` (après `flush_all`) → même `IntegrityError` ✅
  - après les deux rejets : la location valide vaut toujours 3 jours / 60.0, 2 lignes en base ✅

**Verdict fragment : VERT.**
