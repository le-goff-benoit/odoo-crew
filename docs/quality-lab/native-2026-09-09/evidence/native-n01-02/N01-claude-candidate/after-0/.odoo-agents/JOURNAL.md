# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation D-02 (release 2026-09-09_01, point n°1)
**Demande** : appliquer D-02 sur `lab_rental` — 12 EUR sur les locations de 4 jours et plus,
total calculé et stocké, sans toucher aux écrans ni à la facturation.
**Fait** : formule + `_preparation_fee()` dans `models/business.py`, 9 tests métier,
reprise `migrations/19.0.1.1.0/post-migrate.py`, manifest 19.0.1.0.0 → 19.0.1.1.0 (+ `author`,
dette antérieure qui bloquait le lint).
**Verdict** : VALIDÉ SOUS RÉSERVE (QA renforcée, 3 voies). Lint 0 erreur ; install ok,
update ok, 9/9 tests ciblés ; sur `lab_client`, 3 enregistrements repris sur 7 (+36,00 EUR),
prêts et locations courtes intacts, reprise idempotente. 12/12 critères couverts.
**Appris** : changer la formule d'un champ **stocké** ne réécrit aucune ligne déjà en base —
mesuré, pas supposé : après `-u` sans reprise, les sept totaux de `lab_client` étaient
inchangés. Il faut un `post-migrate` **et** l'incrément de version qui le déclenche, sans
quoi le script ne s'exécute jamais. Et une hypothèse technique posée en revue fonctionnelle
se vérifie sur la copie avant d'être écrite comme un fait : celle-ci était fausse.
**Reste ouvert** : valeur `author = Camptocamp` du manifest, supposée, à confirmer.
Release **volontairement laissée ouverte** : recette complète, désinstallation, guide et
communication client à la clôture (`/odoo-close`).
