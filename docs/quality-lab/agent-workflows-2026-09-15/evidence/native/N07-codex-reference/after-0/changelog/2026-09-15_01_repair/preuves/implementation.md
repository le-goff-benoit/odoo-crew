# Implémentation N-17

Modèle 19.0 : copy_data réinitialise les quantités et l'état par défaut ; zéro manuel explicite ; reliquat positif et source done ; cron filtre draft automatique et évite les écritures sans différence.
Tests : 9 méthodes, dont deux sous-cas sans reliquat, précision 0.003, sélection mixte et vrai ir.cron temporaire avec enter_registry_test_mode (précédent base/tests/test_ir_cron.py:110).
Rouge confirmé : red-confirmed.log, 9 échecs d'assertion comptés (sous-tests inclus), 0 erreur technique, 9 méthodes. Le premier red.log contient une erreur de montage du test cron corrigée AVANT le rouge confirmé et le code métier.
Vert : green.json/green.log, 0 failed, 0 errors of 9 tests ; installation et update OK, aucun skip, 7 s au total.
Lint complet via pont : Ruff bloquant et conseils verts ; un seul défaut préexistant, author absent du manifest inchangé (business-before.txt et manifest-before.txt sont les références initiales). Ce défaut n'est pas une régression du diff.
Aucun changement de schéma/droits/dépendances. Version 19.0.1.0.0, incrément reporté à la clôture.
