# Qualification droits multi-sociétés — 2026-09-09

Témoin accepté, mutant règle absente détecté, ORM et vrai XML-RPC sous utilisateur ordinaire uid=5, sociétés autorisées=[2], société interdite=3. Odoo 19.0-20260817.

- run-1 : 15,29 s ; défaut oracle RPC (attente nom Python au lieu du code4), infrastructure nettoyée. Aucun mutant exécuté après témoin déclaré invalide.
- oracle-reevaluation.json : mêmes réponses originales, mapping XML-RPC vérifié en sources ; témoin conforme sans nouvel appel Odoo.
- run-2 : 32,09 s ; témoin13,98 s, mutant16,29 s ; 9 contrôles ORM,7 RPC,3 postconditions privilégiées par variante.
- Témoin :19/19 vérifications satisfaites.
- Mutant :6 défauts ORM,4 RPC,2 postconditions en échec ; lecture B révélée, valeur B devenue888, imports étrangers persistants. L'utilisateur reste limité et les opérations autorisées sur A fonctionnent.
- Total3 variantes réellement exécutées, zéro appel LLM, moins de15 minutes. Nettoyage Docker vérifié sur les deux runs, empreintes contrôlées.

Adoption : banc/oracle réutilisable et calibration démontrée. Aucune amélioration d'instruction agent déduite de cette calibration. Limites : modèle synthétique19.0 uniquement, méthode import serveur sans assistant navigateur, aucun contrôle comptable.
