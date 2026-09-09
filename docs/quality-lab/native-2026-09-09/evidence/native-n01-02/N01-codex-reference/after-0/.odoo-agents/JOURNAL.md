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
