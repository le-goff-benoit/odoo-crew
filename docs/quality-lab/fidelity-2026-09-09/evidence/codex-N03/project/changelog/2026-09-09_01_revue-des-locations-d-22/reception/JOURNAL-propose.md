# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Indicateur de revue D-22
**Demande** : booléen Studio calculé stocké, pack et scénarios RPC, deux applications sans doublon.
**Fait** : x_studio_needs_review dépend de x_studio_days et x_studio_kind existants ; aucun écran, droit, envoi ni module ajouté.
**Verdict** : validation locale sur lab_client ; scénarios de création et modification, contrôle du pack et des deux applications consignés dans changelog/2026-09-09_01_revue-des-locations-d-22/qa.md.
**Appris** : D-22 remplace D-21 : revue si durée >= 7 ET rental ; loan exclu même au-delà, 6 jours sans revue.
**Piège** : le XML-ID Studio créé automatiquement porte studio=True mais noupdate=False initialement ; le write Studio le passe à True (sources 19.0).
**Reste ouvert** : release ouverte ; aucune livraison ni aucun déploiement réalisé. Clôture et recette complète ultérieures sur demande.
