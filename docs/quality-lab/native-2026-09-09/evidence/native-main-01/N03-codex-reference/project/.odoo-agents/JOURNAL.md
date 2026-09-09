# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.
## 2026-09-09 — D-22 réalisé en Studio, QA validée
**Demande** : seul booléen stocké `x_studio_needs_review`, champs existants, copie locale, sans écran ni déploiement.
**Fait** : calcul `days >= 7` ET `kind = rental`, dépendances des deux champs ; pack Studio limité à un champ et scénarios RPC rejouables.
**Verdict** : VALIDÉ ; rouge avant ajout, 33/33 contrôles après construction puis après chacune des deux applications.
**Idempotence** : première application depuis champ absent = 1 création ; seconde = aucun changement, mêmes identifiants ; diff nul.
**Nettoyage** : zéro donnée métier finale ; ACL temporaire supprimée ; modèle, champs initiaux, vues et droits conservés.
**Appris** : D-22 remplace D-21 ; XML-ID Studio natif à protéger en noupdate via write ; cache ACL du banc à invalider complètement pour les fixtures RPC.
**Preuves** : `changelog/2026-09-09_01_indicateur-de-revue-d-22/qa.md` et `studio/proofs/` ; flow `d22-studio`.
**Reste ouvert** : release (1/1 point réalisé) ; clôture seulement sur demande. Candidats `/odoo-feedback` : noupdate et invalidation des caches.
