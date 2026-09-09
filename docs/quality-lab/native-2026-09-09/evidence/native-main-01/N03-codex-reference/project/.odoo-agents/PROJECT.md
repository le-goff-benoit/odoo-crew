# Association Aster — indicateur Studio de revue
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.

D-22 réalisée le 2026-09-09 : `x_lab_request.x_studio_needs_review` est vrai si `x_studio_days >= 7` et `x_studio_kind == 'rental'`. Champ booléen stocké dépendant des deux champs existants, prêts exclus ; aucun écran ni droit permanent ajouté.
Pack et scénarios : `changelog/2026-09-09_01_indicateur-de-revue-d-22/studio/`. QA verte sur la copie 19.0, première application depuis indicateur absent puis seconde inchangée. Release ouverte.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.

Le modèle du banc est initialement vide et sans ACL ; les scénarios créent un accès administrateur temporaire nettoyé dans `finally`. Ils utilisent le pont pour invalider les caches d'accès après création/suppression de la fixture. Ne pas inclure cette ACL dans le pack.
Le contexte Studio génère l'XML-ID natif ; sur cette révision 19.0, `noupdate` devient vrai via `write` de cet XML-ID en contexte Studio (sans le renommer).
