# QA d'exécution renforcée — VALIDÉ
Transport LAB.md, seule base QA lab_qa. Logs complets dans les preuves de la release.
- Premier `qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate` : zéro test ; rejeté, ne constitue pas une preuve verte.
- `qa lab_dispatch --tags /lab_dispatch:TestRecalculate` : installation réelle réussie ; 6/6 tests rouges sur code original (`test-rouge.log`, 7 s).
- Après correction, `qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate` : update réussi ; 6/6 tests verts, zéro skip, erreur ou échec (`test-vert.log`, 3 s).
La classe ciblée est l'intégralité de la suite actuellement présente dans le module. Critères 1–4 et idempotence de l'action couverts ; absence de write vérifiée par interception, y compris validé déjà à 20.
Pas de parcours navigateur ni désinstallation en QA de tâche ; aucune interface modifiée. La copie est contrôlée séparément.
