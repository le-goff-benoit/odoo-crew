# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — D-22, indicateur Studio
**Demande** : ajouter uniquement x_studio_needs_review stocké, voie Studio, copie locale, release ouverte.
**Fait** : champ calculé selon days >= 7 ET kind = rental, dépend des deux champs existants ; pack et scénarios RPC dans changelog/2026-09-09_01_indicateur-de-revue-d-22/studio/.
**Verdict** : VALIDÉ, rouge avant/vert après ; deux apply (1 création puis 0 changement), diff nul, aucun doublon ; seuils, prêts, transitions, lots et initialisation 3/3.
**Nettoyage** : données/actions temporaires supprimées ; seuls le champ et son XML-ID sont ajoutés ; droits, champs sources et vues conservés.
**Appris** : D-22 remplace D-21 (pas de seuil 5 ni nouveau champ durée). Le modèle du banc sans ACL nécessite un support de recette temporaire avec sudo ; cela ne prouve pas l'accès métier.
**Appris** : Studio 19.0 marque studio à la création du XML-ID, mais ne force noupdate qu'au write ; candidate de correction du référentiel.
**Reste ouvert** : release ouverte, aucune livraison/déploiement ; recette complète à sa clôture. Détail et limites dans qa.md.
