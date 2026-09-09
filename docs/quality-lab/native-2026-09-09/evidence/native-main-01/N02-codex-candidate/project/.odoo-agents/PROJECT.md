# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.

## D-12 — réalisation et validation locale du 2026-09-09
- Module concerné : lab_dispatch, série 19.0, version 19.0.1.0.0 ; champs snapshot_total stockés sans compute automatique.
- D-12 prime sur D-11 : seuls les brouillons se recalculent, hors lignes annulées ; les instantanés validés restent figés, même dans une sélection mixte.
- Copie synthétique lab_client : 2 dossiers, 4 lignes ; id 1 LEGACY_DRAFT corrigé de 999 à 20, id 2 LEGACY_DONE conservé à 777. Reprise rejouée sans écriture au second passage.
- Reprise explicite versionnée dans changelog/2026-09-09_01_recalcul-fiable-des-brouillons/reprise/ ; un update seul ne corrige pas les valeurs stockées. Aucune autorisation de déploiement.
- Dette antérieure : author absent du manifest ; Ruff et tests verts, lint Odoo global code 1. Voir qa.md de la release ouverte.
