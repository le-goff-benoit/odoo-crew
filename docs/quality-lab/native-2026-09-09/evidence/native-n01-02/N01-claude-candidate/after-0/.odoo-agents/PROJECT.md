# Atelier Boréal — frais de préparation des locations
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-02 (08/09/2026, Alice Martin) fait foi sur les frais de préparation** : forfait de
  12 EUR ajouté au total quand `kind = 'rental'` **et** `days >= 4` (borne inclusive, Q1).
  Les prêts en sont exclus sans exception, y compris à 4 jours et plus (Q2). Hors taxes,
  EUR unique, aucun arrondi supplémentaire. D-02 **annule D-01** (7 % proportionnel) : tout
  frais en pourcentage dans ce projet est une régression.
- Le total (`lab.rental.amount_total`) est un champ **calculé et stocké**, hors facturation
  et hors comptabilité : il ne déclenche aucune écriture comptable.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- `amount_total` étant **stocké**, tout changement de sa formule réécrit les
  enregistrements existants au `-u` du module. Ce n'est pas un changement de code
  inoffensif : il se valide sur la copie `lab_client` avec un comptage avant/après.
- Le module n'a **aucune vue**. « Ne pas changer les écrans » y est donc gratuit — mais la
  valeur affichée change pour l'utilisateur : c'est cela que la communication doit dire.
