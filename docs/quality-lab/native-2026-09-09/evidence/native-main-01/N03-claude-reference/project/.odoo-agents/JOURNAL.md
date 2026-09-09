# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Indicateur de revue sur les demandes Aster (D-22)
**Demande** : indicateur booléen stocké `x_studio_needs_review` sur `x_lab_request`, voie Studio, sans module ni déploiement.
**Fait** : champ manuel calculé stocké créé en contexte `studio=True` (`depends` sur `x_studio_days` et `x_studio_kind`) ; pack versionné, scripts de construction et scénarios RPC dans `changelog/2026-09-09_01_…/studio/`. Champs existants intacts.
**Verdict** : VALIDÉ — 10/10 critères, scénario 17/17, pack appliqué deux fois sans doublon (y compris depuis une copie sans le champ), contre-épreuve D-21 bien rouge.
**Appris** :
- `x_lab_request` n'a **aucun** `ir.model.access` : personne, admin compris, ne peut lire ni créer une demande. Le champ est correct mais inexploitable en l'état ; D-22 interdit d'y toucher, donc c'est à arbitrer.
- Odoo ne pose `noupdate` sur un identifiant externe Studio qu'au premier *write*, pas à la création (`web_studio/models/ir_model_data.py`) : un pack exporté juste après création serait exposé à une mise à niveau.
- Un droit d'accès fraîchement créé reste invisible du processus qui sert les appels tant que `ir.model.access.call_cache_clearing_methods` n'a pas été appelé — constaté sur `create` pendant 8 requêtes, alors que `read` passait.
**Reste ouvert** : décision sur les droits d'accès du modèle ; aucun écran n'affiche l'indicateur ; release ouverte, clôture par `/odoo-close`.
