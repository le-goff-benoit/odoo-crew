# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-12 (2026-09-08, Marc Colin)** prime sur D-11 (2026-08-01) : `action_recalculate`
  ne traite **que** les brouillons, somme les lignes `cancelled=False`, et laisse un
  dossier validé strictement intact (aucune écriture, pas même identique). Une
  sélection mixte ignore les validés sans erreur. Aucun changement de droits ; un
  validé ne redevient jamais brouillon.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- Le journal contient encore D-11 (recalculer tous les dossiers) : règle **morte**,
  ne pas la ressortir. Toute reprise de données ne concerne que les brouillons.
- « Inchangé » pour un dossier validé se garantit en filtrant **avant** l'écriture
  (`filtered(state == 'draft')`), pas en réécrivant la même valeur.
