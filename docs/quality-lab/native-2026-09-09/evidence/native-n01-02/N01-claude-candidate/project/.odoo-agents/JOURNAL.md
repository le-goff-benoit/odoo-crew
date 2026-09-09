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

## 2026-09-09 — Frais de préparation D-03, remplace D-02 (release 2026-09-09_01, point n°2)
**Demande** : D-03 (Alice Martin, `decisions/2026-09-09.md`) remplace D-02 dans la même
release : 15 EUR à partir de 5 jours inclus, au lieu de 12 EUR à partir de 4. Prêts
toujours exclus, `jours × tarif` inchangé. Validation locale seulement.
**Fait** : `PREPARATION_FEE` 12 → 15 et `PREPARATION_FEE_MIN_DAYS` 4 → 5 dans
`models/business.py` (structure inchangée) ; 11 tests **réécrits** sur D-03 ; nouvelle
reprise `migrations/19.0.1.2.0/post-migrate.py` ; manifest 19.0.1.1.0 → 19.0.1.2.0.
`migrations/19.0.1.1.0/` conservé (il sert une base restée en 19.0.1.0.0).
**Verdict** : **VALIDÉ** (QA renforcée, 3 voies, 13/13 critères). Lint 0/0/0 ; install et
update ok ; 11/11 tests ciblés, 6/11 rouges sur les constantes D-02 ; sur `lab_client`
3 repris sur 7 dont **2 à la baisse**, delta net **−21,00 EUR** (296,00 → 275,00), prêts
intacts, **0 écart** vs la prédiction écrite avant de coder, reprise idempotente.
**Appris** : une reprise ne se rejoue pas deux fois dans une même release sans **nouvel
incrément** — la version installée avait rattrapé le manifest (19.0.1.1.0), le dossier de
migration du point n°1 était inerte, et un `-u` aurait laissé les totaux D-02 **sans une
seule erreur**. La version installée se **lit sur la copie** avant de conclure. Et une
reprise réapplique la **formule**, jamais un delta : une décision qui en remplace une autre
corrige aussi à la baisse, et le recompute est la seule forme correcte *et* idempotente.
**Reste ouvert** : `author = Camptocamp` du manifest (report du point n°1, sans effet) ;
chaîne complète `19.0.1.0.0 → 19.0.1.2.0` en un seul `-u` non mesurée. Release
**volontairement laissée ouverte** : recette complète, désinstallation, guide et
communication (D-03 seule) à la clôture (`/odoo-close`).
