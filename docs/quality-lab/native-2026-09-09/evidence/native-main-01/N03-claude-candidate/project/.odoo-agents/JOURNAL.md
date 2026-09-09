# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Indicateur de revue requise (D-22), voie Studio
**Demande** : ajouter le seul booléen calculé stocké `x_studio_needs_review` sur
`x_lab_request`, sans module, sans écran, sans déploiement.
**Fait** : champ manuel calculé stocké créé en contexte `studio=True`
(`studio_customization.revue_requise_demand_924627ca…`), dépendances
`x_studio_days,x_studio_kind` ; pack versionné, build idempotent, deux
scénarios rejouables. Release `2026-09-09_01`, point 1.
**Verdict** : VALIDÉ — RPC 12/12, ORM 16/16, 13/13 critères après une reprise.
**Appris** :
- Un `ir.model.data` créé en contexte `studio` sort en `noupdate=False` : Studio
  ne pose `noupdate` qu'au `write` suivant (`web_studio/models/ir_model_data.py:19-25`,
  appelé par `ir_model.py:62`). Ce que la doc de rôle résume en « marqué studio et
  noupdate » n'est vrai qu'après une écriture. **Leçon candidate pour LESSONS.md.**
- `x_lab_request` n'a aucun `ir.model.access` : sans ACL, tout accès hors
  superutilisateur est refusé (`ir_model.py:2134-2167`), donc aucun scénario XML-RPC
  au niveau enregistrement n'est possible. La table de vérité se joue en ORM
  superutilisateur.
**Reste ouvert** : trancher les droits d'accès du modèle (préalable à toute mise en
service) ; poser le champ sur un écran ; déployer le pack (staging puis production).
Clôture de la release et recette complète : `/odoo-close`.
