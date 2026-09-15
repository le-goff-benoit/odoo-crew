# Calibration des parcours — 15 septembre 2026

Le [corpus W01–W06](../../../benchmarks/workflow_regressions/README.md) ajoute
livraison, stock/reliquat/cron, facture historique/PDF, formulaire réactif,
mini-release interrompue et diagnostic de série trompeuse. Les oracles sont
séparés des dossiers publics. Aucun appel modèle dans cette calibration.

Les résultats définitifs et les incidents d’amorçage sont conservés ici. Le
succès du témoin puis le rejet d’une mutation qualifient uniquement les défauts
visés ; une campagne native indépendante mesure le comportement des agents.

## Verdict

**Banc adopté comme contrôle supplémentaire.** Cette qualification ne promeut
aucun modèle et n’atteste pas un gain de vitesse des agents.

| Parcours | Témoin | Mutation rejetée | Preuve |
|---|---|---|---|
| Odoo 19 : stock, PDF, formulaire | 3 réussites, 0 erreur ; magasinier et utilisateur facturation ordinaires ; Chrome réel | 3 échecs métier attendus, 0 erreur d’infrastructure | [Résultat](odoo19/result.json), [log témoin](odoo19/witness/odoo.log), [log mutant](odoo19/mutants/odoo.log) |
| Odoo 18 : PDF uniquement | Facture comptabilisée datée de 2020, langue destinataire française, utilisateur anglais, trois lignes et total 49 | Suppression de la ligne explicative à zéro détectée | [Résultat](odoo18/result.json), [log témoin](odoo18/witness/odoo.log), [log mutant](odoo18/mutants/odoo.log) |
| Mini-release W05 | 3 commandes réellement exécutées ; T01 conservée, I03 ajoutée, T02 interrompue/reprise, conflit PDF refusé | Remplacement de la preuve T01 détecté comme périmé | [Résultat](mini-release/result.json) |
| Contrats du banc et diagnostic W06 | 9 tests sans Docker | Perte de couverture, preuve changée, mauvais diagnostic, faux succès navigateur et incident transport refusés | [Tests](unit-tests.log) |

Les deux campagnes Odoo ont nettoyé leurs conteneurs et réseaux, avec vérification.
Durées de campagne sur ce poste : **177,672 s** pour Odoo 19 et **173,171 s**
pour Odoo 18 ; elles incluent l’installation de bases neuves et les assets et
ne sont pas une mesure de vitesse des modèles. La mini-release utilise les APIs
réelles avec un graphe minimal à deux nœuds explicitement synthétique ; elle ne
remplace pas la recette complète d’un module Odoo.

W01 réutilise les calibrations de la [garde de livraison](../../DELIVERY_GUARD.md).
W06 utilise le lecteur de série réel sur config et manifest 18 malgré un journal
importé trompeur 19, plus une grille structurée distincte. Les dossiers W05/W06
restent disponibles pour des campagnes natives futures ; aucune réussite native
sur ces dossiers n’est annoncée ici.

## Rendus vérifiés

Les PDF ont été rendus en PNG et inspectés : les trois lignes, le total et les
libellés français sont lisibles, sans rognage.

- Odoo 19 : [PDF](odoo19/witness/rendered/historical-invoice.pdf) · [PNG](invoice19.png).
- Odoo 18 : [PDF](odoo18/witness/rendered/historical-invoice.pdf) · [PNG](invoice18.png).

## Incidents conservés

Les premiers essais ont identifié des défauts du **banc**, conservés dans
[incidents.json](incidents.json) et leurs journaux : nom du fichier CSV,
`stock.move.name` absent en 19, contexte HTTP nécessaire au PDF, puis contexte
de registre de test pour le curseur séparé du cron. Ils ont été corrigés avant
les témoins définitifs. Le format initial `ODOO_SERIES=18.0` du fichier config
était ignoré : le runtime et le manifest restaient bien 18, mais son briefing
était trompeur. Le témoin 18 final a été rejoué avec `series = 18.0` et porte le
[briefing exact](odoo18/witness/briefing.md).

Les sources et résultats propres à chaque essai sont archivés sans correction
rétroactive des logs. Les chemins absolus dans certaines preuves désignent les
bacs à sable originaux ; leur copie documentaire n’est pas une relocation
certifiée de l’environnement. Les valeurs et identités sont toutes fictives.
