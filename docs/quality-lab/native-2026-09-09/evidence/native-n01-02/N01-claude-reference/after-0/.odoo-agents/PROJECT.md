# Atelier Boréal — frais de préparation des locations
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
Le module `lab_rental` porte un modèle propre au projet (`lab.rental`, dépend de `base`
seul) : ce n'est pas du `sale_renting` (standard enterprise). Deux natures d'engagement
cohabitent sur le même modèle, distinguées par `kind` : la **location** (facturée) et le
**prêt** (jamais de frais). Le total `amount_total` est un champ calculé **stocké**.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-02 (08/09/2026, Alice Martin) — en vigueur** : `amount_total = jours × tarif_jour`,
  plus un forfait de préparation de **12 EUR** si `kind = 'rental'` **et** `days >= 4`.
  Borne inclusive (Q1 : 4 compte). Prêts exclus quelle que soit la durée (Q2).
  Hors taxes, EUR unique, aucun arrondi supplémentaire.
- **D-01 (7 % de frais) est morte** : elle ne subsiste que dans l'entrée de journal du
  2026-08-01. Ne pas la réimplémenter en relisant le journal.
- Périmètre volontairement fermé : pas de facturation, pas de comptabilité, pas de devise,
  pas de contrainte de saisie, aucun écran modifié.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- **`amount_total` est stocké** : changer la *formule* ne recalcule pas les enregistrements
  existants. Odoo ne recalcule que sur variation des dépendances (`days`, `daily_rate`,
  `kind`). Toute évolution de la règle tarifaire doit se demander si une base cible contient
  des lignes, et prévoir un script de migration le cas échéant. (Copie `lab_client` au
  2026-09-09 : 0 enregistrement, donc sans objet ce jour-là.)
- Le seuil de 4 jours est **inclusif** ; le piège classique est d'écrire `> 4`.
