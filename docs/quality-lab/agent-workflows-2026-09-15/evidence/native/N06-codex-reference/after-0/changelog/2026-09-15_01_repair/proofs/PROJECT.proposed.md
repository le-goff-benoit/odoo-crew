# Registre Boréal — brouillons et références émises
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.

## Décisions actées — B-42
- Source : decisions/current.md. Réparer seulement les draft de self dans env.company, même avec plusieurs sociétés autorisées ; ordre date_document/id, séquences 100,200… ; total des seules lignes non annulées.
- Issued : préserver state, sequence, snapshot_total et reference ; autres sociétés et brouillons non sélectionnés intacts. Sélection mixte accessible admise, sans élévation de droits.
- Reprise locale historique société initiale 1 effectuée : IDs 1/2 = 100/20 et 200/15. Émis 3 et autre société 4 préservés. Deuxième transaction sans changement et rejeu sans write.
- ACL/règles inchangées ; droits vérifiés sous utilisateurs ordinaires, y compris refus de société interdite et refus write.
- La QA initiale de création vide ne couvre pas B-42. Preuves actuelles dans changelog/2026-09-15_01_repair/qa.md ; relecture non indépendante imposée par LAB.md.
- Lint Python passe ; lint Odoo global rouge sur dette antérieure author manquant (manifest inchangé). Release ouverte, aucune livraison distante ni recette complète.
