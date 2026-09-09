# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation D-02
**Demande** : appliquer D-02 au total calculé stocké, tests métier et QA de tâche, release ouverte.
**Fait** : forfait unique 12 EUR HT pour locations >= 4 jours, prêts exclus ; aucun écran ni facturation modifiés.
**Fait** : 8 tests métier ; reprise ORM versionnée, deux passages sur quatre témoins créés avant changement, relecture en nouvelles sessions, nettoyage.
**Verdict** : VALIDÉ — lint 0 erreur/avertissement, installation QA et 8/8 tests (19 s), mise à jour copie réussie ; C1–C6 conformes.
**Appris** : D-02 remplace D-01 ; un changement du compute stocké nécessite la reprise explicite après update, prouvée idempotente ici.
**Outillage** : ruff installé isolément ; auteur initialement absent complété. Avertissement du pont --without-demo=all consigné, sources 19.1 absentes.
**Preuves** : changelog/2026-09-09_01_frais-de-preparation-des-locations/qa.md et .odoo-agents/flow-artifacts/preparation/.
**Reste ouvert** : release (1/1 point réalisé), recette complète /odoo-close et incrément de version à la clôture ; aucun déploiement ni commit.
**Candidate dispositif** : adapter le pont à l'option booléenne --without-demo de 19.0 via /odoo-feedback, sans modifier le référentiel en lecture seule.


## 2026-09-09 — Reprise D-03 après QA D-02
**Demande** : Alice Martin acte D-03 (`decisions/2026-09-09.md`), +15 EUR dès 5 jours inclus ; prêts exclus, base jours × tarif inchangée.
**Fait** : point 2 dans la même release ; compute, 8 tests et script de reprise adaptés ; ancien run, preuves et journal D-02 conservés.
**Verdict** : VALIDÉ D-03 en QA de tâche renforcée locale — lint vert, installation 8/8 (12 s), update/suite 8/8 (4 s), critères D3-C1 à C6 conformes.
**Preuves** : tests D-03 rouges sur code D-02 (11 assertions), verts après correction ; `qa.md`, `.odoo-agents/flow-artifacts/preparation-d03/` et run natif terminé.
**Copie** : update seul laisse D-02 ; reprise de 7 témoins, 3 corrections (4j 52→40, 5j 62→65, 6j 72→75), second passage 0 changement, deux relectures 7/7, nettoyage confirmé.
**Appris** : D-03 remplace D-02, qui remplaçait D-01 ; la première QA ne valide pas une décision ultérieure ni le nouveau code. Les anciennes preuves restent historiques.
**Outillage** : venv ruff temporaire absent dans le contexte neuf, réinstallé ; premier lint partiel conservé puis vert. Avertissements du pont consignés, sources enterprise 19.1 absentes.
**Mémoire** : PROJECT.md et suivi actualisés ; vérifier les outils temporaires à chaque contexte. Comparaison des empreintes historiques sans changement.
**Reste ouvert** : release, recette complète /odoo-close et version à incrémenter à la clôture ; aucun commit, déploiement ou production ; essais sur copie synthétique seulement.
