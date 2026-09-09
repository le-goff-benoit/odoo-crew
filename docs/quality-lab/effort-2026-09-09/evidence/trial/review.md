# Essai indépendant de /odoo-estimate

Verdict : PASS. Sept commandes réelles, toutes terminées sans erreur.

Deux lots fictifs Odoo 19 : référence livraison et filtre de recherche. Analyse déjà reçue ; copie prête supposée. Trois rôles par lot et deux rôles communs à la release, soit huit lignes.

La révision partielle change uniquement la prévision développeur de T01. La version initiale et les sept autres lignes restent identiques. Le bilan indique les mesures réelles et les jetons comme indisponibles.

## Contrôles

- initial_revision_unchanged : PASS
- two_revisions : PASS
- eight_lines_preserved : PASS
- seven_untouched_lines_identical : PASS
- revision_reason_preserved : PASS
- only_agent_minutes_no_rates : PASS
- missing_actual_unknown : PASS
- all_initial_low_confidence : PASS
- qa_release_once : PASS
- no_analysis_reestimated : PASS
- four_reports_exist : PASS

## Limites

- Aucune précision prédictive démontrée : jugement initial et confiance faible
- Disponibilité de copie et analyse reçue sont des hypothèses du scénario, non une vérification Odoo
- Aucune mesure native importée dans cet essai de préparation
- CLI verbeuse en JSON ; Markdown affiche encore low au lieu de faible
- Briefing offline ne reconnaît pas la release synthétique sans état du gestionnaire ; chemin explicite accepté et aucune commande de développement lancée
