# Atelier Boréal — frais de préparation des locations
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
Le module `lab_rental` porte un modèle propre au projet (`lab.rental`, dépend de `base`
seul) : ce n'est pas du `sale_renting` (standard enterprise). Deux natures d'engagement
cohabitent sur le même modèle, distinguées par `kind` : la **location** (facturée) et le
**prêt** (jamais de frais). Le total `amount_total` est un champ calculé **stocké**.
## Décisions actées
Lire decisions/2026-09-09.md : **c'est la seule en vigueur**. Les décisions plus anciennes
(2026-09-08, journal du 2026-08-01) sont mortes et ne doivent pas être réimplémentées.
- **D-03 (09/09/2026, Alice Martin) — en vigueur** : `amount_total = jours × tarif_jour`,
  plus un forfait de préparation de **15 EUR** si `kind = 'rental'` **et** `days >= 5`.
  Borne inclusive : 5 jours comptent, **4 jours ne paie plus rien**. Prêts exclus quelle
  que soit la durée. Hors taxes, EUR unique, aucun arrondi supplémentaire.
- **D-02 (12 EUR dès 4 jours) est morte** : implémentée et validée le 09/09 au point n°1 de
  la release `2026-09-09_01`, puis remplacée le même jour par D-03 avant toute livraison.
  Elle n'a jamais quitté le laboratoire — la communication client ne la mentionne pas.
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
  2026-09-09 : 0 enregistrement, recompté en SQL après la bascule D-03, donc sans objet ce
  jour-là. La réserve vaut pour D-03 comme elle valait pour D-02.)
- Le seuil de **5 jours** est **inclusif** ; le piège classique est d'écrire `> 5`. Montant et
  seuil sont deux constantes distinctes (`PREPARATION_FEE`, `PREPARATION_FEE_MIN_DAYS`) : un
  test garde-fou vérifie qu'elles portent ensemble les valeurs de la décision en vigueur.
- **Une règle tarifaire peut être remplacée au milieu d'une release ouverte.** Une QA verte ne
  vaut que pour la règle qu'elle a mesurée : quand la décision change, le point déjà validé
  est requalifié « REMPLACÉ » dans le suivi et la nouvelle suite de tests doit être prouvée
  rouge sur l'ancienne formule. Ne jamais laisser deux règles se disputer le README à la
  clôture.
