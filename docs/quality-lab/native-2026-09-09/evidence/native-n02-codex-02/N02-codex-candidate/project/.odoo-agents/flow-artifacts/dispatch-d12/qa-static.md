# QA statique renforcée — VALIDÉ

Module lab_dispatch, série 19.0 depuis le manifest, mode tâche sensible.
`lint-final.json` vérifié : cinq fichiers, Ruff officiel et contrôles Odoo, zéro erreur/avertissement. Script de reprise : `lint-reprise.log`, Ruff officiel avec `builtins = ["env"]` et `--ignore T201` : le shell fournit env et le rapport de preuve est émis sur stdout. Sans ces adaptations de script shell, Ruff signalait ces deux usages attendus.
Diff relu : filtrage avant accès aux lignes, pas de sudo, SQL, compute automatique, changement de droits ou d'état. Écriture ORM seulement quand le montant diffère. Manifest : seule métadonnée author ajoutée ; dépendance base et sécurité existantes conservées.
Tests importés, six comportements incluant lecture/écriture interdite des validés, cas limites, sélection mixte et absence d'écriture au rejeu. Le scénario de reprise ne s'exécute que sur lab_client, ne sélectionne que les brouillons pour l'action et compare les validés et les lignes.
C1–C4/C6 couverts par les tests ; C5/C6 restent à constater sur la copie dans la voie dédiée.
