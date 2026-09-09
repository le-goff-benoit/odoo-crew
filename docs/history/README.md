# Correspondance des commits historiques

[Documentation](../README.md)

Le 9 septembre 2026, les lignes de co-auteur Claude ont été retirées de
19 commits à la demande du propriétaire. Cela a changé les identifiants des
42 commits de l’historique de `main`, sans modifier leurs fichiers, auteurs
humains, dates ou autres lignes de message.

[`commit-map.json`](commit-map.json) associe chaque ancien identifiant à son
équivalent. Les rapports de campagne conservent leurs références d’origine :
utilisez cette correspondance pour retrouver la version concernée dans un
nouveau clone. Les arbres Git de chaque paire sont identiques.

Si vous utilisez encore un clone antérieur à cette réécriture, sauvegardez
vos changements locaux et repartez d’un nouveau clone. Ne fusionnez pas
l’ancien historique dans `main`, ce qui réintroduirait les attributions retirées.
Une sauvegarde complète de l’ancien historique est conservée localement
par le propriétaire ; elle n’est pas publiée dans ce dépôt.
