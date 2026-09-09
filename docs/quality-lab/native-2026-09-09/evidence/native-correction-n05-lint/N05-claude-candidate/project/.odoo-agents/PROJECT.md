# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-12 (2026-09-08, Marc Colin) prime sur D-11 (journal 2026-08-01), qui est écartée.**
  D-11 demandait de recalculer tous les dossiers ; D-12 fige définitivement les dossiers
  validés. Un dossier `state = 'done'` n'est ni recalculé, ni réécrit avec la même valeur,
  ni repassé en brouillon. Les lignes `cancelled = True` sont exclues du total.
- La reprise des données existantes ne porte que sur les brouillons et doit être idempotente.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- `lab.dispatch.snapshot_total` est un `Float()` **sans `digits`** : aucun arrondi n'est
  appliqué. Comparer ce champ avec une précision de 2 décimales masque les dérives fines
  (cas réel : `LEGACY_FRACTION` à 20.004 au lieu de 20.0). La comparaison doit être exacte.
- « Figé » pour un dossier validé veut dire *aucune écriture*, pas *même valeur* : filtrer
  les validés **avant** la boucle d'écriture, sinon `write_date` bouge.
