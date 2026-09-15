# Registre Boréal — brouillons et références émises
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.

## Décision B-42 et résultat local — 2026-09-16
`action_repair` cible uniquement self en draft dans env.company, même si plusieurs sociétés sont autorisées. Tri date_document puis id, séquences 100/200/…, somme quantity*price des seules lignes non annulées. Issued et autres sociétés strictement préservés ; sélection mixte autorisée dans les droits de lecture existants.
Correction et reprise lab_client : société initiale 1, ids 1/2 = 100/20 et 200/15 ; issued id 3 = 17/555/ISSUED/005 et société 2 id 4 = 80/666/OTHER/DRAFT inchangés, toutes lignes et métadonnées exclues conservées. Rejeu : zéro write, valeurs et write_date/write_uid stables.
Six tests rouges puis verts ; succès/refus sous utilisateur ordinaire sans sudo prouvés sur QA et copie. Fichiers ACL/règles inchangés. Compte du pont RPC autorisé en société 1 uniquement, ne pas élargir ses droits pour une recette multi-société.
Ancienne QA limitée à une création vide : elle ne réceptionne pas B-42. Dossier courant : changelog/2026-09-15_01_repair/qa.md. Lint complet rouge uniquement sur dette author du manifest ; diff/Ruff bloquant conformes. Relecture non indépendante (LAB.md). Release ouverte, pas de déploiement distant, version 19.0.1.0.0.
