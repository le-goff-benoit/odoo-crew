# Implémentation D-12 — Odoo 19.0

Reproduction réelle sur QA : `changelog/2026-09-09_01_recalcul-des-brouillons-d12/red-final.json` et `.log`, six échecs / zéro erreur, code initial. Brouillon 110 ≠ 20 ; validé 110 ≠ 777 ; lecture des lignes validées détectée.
Correction : filtrage des brouillons avant lecture des lignes, exclusion des annulées, absence d'écriture pour un total déjà exact. Six tests et leur jeu de données commun. Reprise bornée à lab_client dans `reprise.py`, commits explicites, rapport avant/après.
Première exécution corrigée : six tests verts (`green-dev.log`, 7 s). Manifest complété ensuite avec l'auteur synthétique, absence préexistante bloquant le lint ; version 19.0.1.0.0 inchangée. QA finale à rejouer sur cet état.
Lint final : `lint-final.json` et `.log` : cinq fichiers, Ruff officiel et contrôles Odoo verts, zéro avertissement. Ruff installé dans l'environnement isolé ignoré `.tools/venv` ; aucun outil ni source Odoo modifié.
