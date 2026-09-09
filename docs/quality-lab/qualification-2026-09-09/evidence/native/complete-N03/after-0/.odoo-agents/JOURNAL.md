# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Indicateur de revue Studio (D-22)
**Demande** : ajouter le seul booléen stocké `x_studio_needs_review` sur `x_lab_request`,
calculé selon D-22, sans module et sans déploiement.
**Fait** : champ manuel calculé stocké créé en contexte `studio=True`
(`studio_customization.revue_requise_demand_0772…`), `depends` sur les deux champs existants
réutilisés tels quels. Pack versionné `studio/pack.json`, trois scénarios rejouables.
Release `2026-09-09_01`, point 1.
**Verdict** : VALIDÉ — RPC 25/25, ORM 12/12, `diff` 0, deux applications sans doublon,
13/13 critères. Aucun droit, vue, automatisation ni cron créé.
**Appris** :
- Un modèle manuel peut exister **sans aucun `ir.model.access`** : personne, pas même `admin`,
  n'y accède en XML-RPC. La recette du comportement passe alors par l'ORM superuser, et cette
  limite doit être *prouvée* dans le scénario plutôt que supposée.
- D-22 (7 jours inclus, location seule) remplace D-21 (5 jours pour tous) : la table de vérité
  du scénario se lit dans la décision, jamais dans le calcul à tester.
**Reste ouvert** : le champ n'est visible par personne faute d'ACL et faute de vue — arbitrage
humain à demander, hors périmètre de D-22. Clôture et recette complète : `/odoo-close`.
