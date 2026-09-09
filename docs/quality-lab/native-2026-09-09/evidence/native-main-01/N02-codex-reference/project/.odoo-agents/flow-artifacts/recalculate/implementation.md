# Implémentation sensible — terminée
Odoo 19.0 ; `lab_dispatch/models/business.py` filtre les brouillons avant tout calcul, exclut les lignes annulées et évite les écritures à valeur identique.
Trois fichiers de tests ajoutés (common, import, classe de six tests). Aucun changement du manifest, des droits ou des vues.
Preuves dans `changelog/2026-09-09_01_recalcul-fiable-des-brouillons/preuves/` :
- `business-avant.py`, `revision-avant.txt` et `test-rouge.log` : six échecs réels sur le code initial ; 110 au lieu de 20 et de 777.
- `correction.diff` et `test-vert.log` : même classe, six tests verts, update QA réussi, 3 secondes.
- `lint.log` : lint --changed complet, ruff compris, zéro anomalie dans le périmètre. Ruff installé dans /work/.qa-tools après lint initial partiel.
Script `reprise_brouillons.py` livré pour exécution explicite sur lab_client seulement ; aucun hook automatique qui pourrait s'exécuter ailleurs.
Le premier appel quick n'avait exécuté aucun test : résultat rejeté, module installé explicitement avant le vrai test rouge. Log conservé.
