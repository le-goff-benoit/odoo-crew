# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation D-02
**Demande** : appliquer D-02 au total stocké de lab_rental, sans écran ni facture ; laisser la release ouverte.
**Fait** : forfait 12 EUR dès 4 jours pour les locations, prêts exclus ; contraintes non négatives, 8 tests métier et migration idempotente 19.0.1.0.1.
**Verdict** : VALIDÉ — lint complet vert, installation/mise à jour QA, 8/8 tests sans skip ; update, double reprise et relecture SQL/ORM sur copie synthétique réussis, essais nettoyés.
**Appris** : D-02 remplace D-01 (7 %) ; un compute stocké modifié seul ne recalcule pas l'existant.
**Candidate dispositif** : --quick choisit -u sur une base existante sans vérifier que le module est installé ; un résumé vert avec 0 test doit être refusé. Installation explicite nécessaire ici.
**Preuves** : changelog/2026-09-09_01_frais-de-preparation-des-locations/qa.md et preuves/.
**Reste ouvert** : release (1/1 point réalisé), incrément du manifest et déclenchement automatique de migration à vérifier à /odoo-close ; auteur absent du manifest, dette préexistante.

## 2026-09-09 — Reprise de la release, décision D-03
**Demande** : Alice Martin acte D-03 (decisions/2026-09-09.md), remplaçant D-02 dans la même release.
**Fait** : forfait 15 EUR dès 5 jours inclus pour les locations ; prêts exclus, jours × tarif inchangé ; tests et migration non livrée alignés.
**Mémoire** : revue et suivi du point 1 repris, PROJECT.md à jour ; preuves et flow D-02 conservés, nouveau flow preparation-d03.
**Verdict** : VALIDÉ EN LOCAL — lint vert, mise à jour QA et 8/8 tests (7 s), update copie, double migration et relecture SQL/ORM après commit réussis ; 8 essais nettoyés.
**Reprise 1** : QA copie initialement rouge sur write_date ; critère trop strict ajouté par l'agent rectifié avec preuve du comportement standard ; échec conservé.
**Appris** : D-03 est actuelle, D-02 et D-01 historiques ; une ancienne QA verte ne valide pas une nouvelle décision. Un compute stocké exige une nouvelle reprise.
**Candidate dispositif** : les entrées métier restent intactes, mais le recalcul peut actualiser write_date ; un test dans une transaction unique masque ce changement.
**Preuves** : changelog/2026-09-09_01_frais-de-preparation-des-locations/qa.md et preuves/d03/.
**Reste ouvert** : release 1/1 réalisé localement ; manifest 19.0.1.0.0, incrément et déclenchement automatique de migration 19.0.1.0.1 à tester à /odoo-close ; dette author préexistante. Aucun déploiement.
