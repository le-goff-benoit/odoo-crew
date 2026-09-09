# Atelier Boréal — frais de préparation des locations
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire `decisions/2026-09-09.md` : **D-03 fait foi** et remplace toutes les règles
antérieures sur les frais de préparation.
- **D-03 (09/09/2026, Alice Martin) fait foi sur les frais de préparation** : forfait de
  **15 EUR** ajouté au total quand `kind = 'rental'` **et** `days >= 5` (borne
  **inclusive**). Les prêts en sont exclus sans exception, quelle que soit la durée.
  `jours × tarif_jour` inchangé. Hors taxes, EUR unique, aucun arrondi supplémentaire
  (clauses de D-02 non modifiées, donc maintenues). Validation locale seulement.
- **Historique — ne pas réimplémenter** : D-02 (12 EUR dès 4 jours, `decisions/2026-09-08.md`)
  et D-01 (7 % proportionnel) sont **remplacées**. Un forfait de 12 EUR, un seuil de
  4 jours ou un frais en pourcentage sont désormais des **régressions**. Le test
  `test_fee_amount_and_threshold_are_the_ones_of_d03` verrouille les deux paramètres.
- Le total (`lab.rental.amount_total`) est un champ **calculé et stocké**, hors facturation
  et hors comptabilité : il ne déclenche aucune écriture comptable.
- **Rythme des décisions** : ce client a changé la règle trois fois en cinq semaines. Écrire
  le montant et le seuil comme **constantes nommées** (et non comme littéraux dans le
  compute) est ce qui a réduit D-03 à deux lignes. À conserver.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- `amount_total` étant **stocké**, tout changement de sa formule **ne réécrit rien** au
  `-u` du module : Odoo ne recalcule pas un champ stocké dont seul le corps du compute a
  changé. Mesuré le 09/09, pas supposé. Il faut un `post-migrate` **et** l'incrément de
  version qui le déclenche. Ce n'est jamais un changement de code inoffensif : il se
  valide sur la copie `lab_client` avec un comptage avant/après.
- **Une reprise déjà consommée est inerte.** Un script de `migrations/<version>/` ne
  s'exécute que si la version **installée** est strictement inférieure à celle du manifest
  (`~/odoo-sources/19.0/odoo/modules/migration.py:192-208`). Deux changements de règle dans
  la même release exigent **deux dossiers et deux incréments**. Toujours **lire la version
  installée sur la copie** (`ir.module.module.latest_version`) avant de conclure qu'une
  reprise va s'exécuter — l'oubli ne produit aucune erreur, juste des montants faux.
- **Une reprise réapplique la formule, jamais un delta.** Quand une décision en remplace
  une autre, la correction va **dans les deux sens** (D-03 a retiré 12 EUR aux locations de
  4 jours). Le recompute est la seule forme à la fois correcte dans les deux sens et
  idempotente.
- **Le module porte deux dossiers de `migrations/` à conserver** : `19.0.1.1.0/` (D-02, pour
  une base restée en 19.0.1.0.0) et `19.0.1.2.0/` (D-03). Ne pas les supprimer, ne pas
  redescendre la version du manifest — cela les rendrait inertes.
- Le module n'a **aucune vue**. « Ne pas changer les écrans » y est donc gratuit — mais la
  valeur affichée change pour l'utilisateur : c'est cela que la communication doit dire.
