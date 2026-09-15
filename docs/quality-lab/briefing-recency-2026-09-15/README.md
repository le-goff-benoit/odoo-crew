# Dates du briefing — 15 septembre 2026

Référence : Crew `4c6738c`. Correction locale du lecteur de journal, sans modification des journaux clients ni des instructions de rôle.

## Défaut reproduit

Le briefing choisissait les N dernières positions du fichier. Un journal alimenté en tête ou dans un ordre mixte pouvait présenter un ancien plan comme dernière activité, même en présence d’un incident plus récent.

Trois contrôles synthétiques ajoutés à `tests/pilotage/test_odoo_briefing.py` : journal avec ajout en tête, journal mixte avec conservation des apprentissages anciens, vue complète et entrées de même date. Avant correction : deux échecs et une erreur ; après correction : neuf tests ciblés verts, dont les six contrôles préexistants.

## Correction et limites

La vue limitée sélectionne par date, avec tri stable. La vue complète conserve l’ordre source. Les apprentissages de tout l’historique restent présents. À date identique, le lecteur ne suppose aucune priorité : il conserve l’ordre du fichier et indique les autres titres du jour exclus par la limite, pour permettre leur consultation.

Cette correction ne détermine pas quelle décision remplace une autre et ne réduit pas arbitrairement la mémoire métier. Les journaux sans heure ne prouvent pas l’ordre des décisions dans une même journée. La diminution du contexte et la réécriture des profils restent des propositions à comparer sur un banc comportemental distinct.

## Validation

Neuf tests ciblés verts ; suite récursive de **308 tests, dont 1 ignoré**, graphe valide, génération isolée et parité de **35 fichiers**, y compris vérification des profils actifs. Aucun appel modèle requis pour ce défaut déterministe. Les preuves rouge/vert sont conservées dans ce dossier ; la suite ne lit que des fixtures synthétiques.
