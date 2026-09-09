# Preuve d'interruption et libération des revendications abandonnées

**Date de reprise** : 2026-09-09 · **flow** : `contrainte-jours-positifs` · **projet** `/work`

## Fait constaté
Le superviseur a arrêté le CLI et ses descendants au passage QA, une seule fois
(source : `/work/.odoo-agents/recovery-interruption.json`).

| Élément | Valeur |
|---|---|
| `reason` | Superviseur a arrêté le CLI et ses descendants au passage QA, une seule fois. |
| `old_processes_absent` | true |
| `bridge_drained` | true |
| `same_environment` | true |
| `evidence_sha256` | f46668512fcf4b5f7477bf250b6f2b14bcf0d670537acc7d50eae4c2a964d16e |
| `database` | lab_client et lab_qa conservées, aucune restauration ni recréation |
| `git_head` | 28fbbd694077444cfa427b4e5c9923ae64abed3e |

## Vérifications faites par le nouvel orchestrateur avant libération
- État du flow relu : 3 étapes franchies (`briefing`, `functional_review`,
  `module_implementation_high_risk` → done), 3 nœuds QA revendiqués, 0 prêt.
- Aucune étape valide n'est rejouée : la revue fonctionnelle et
  l'implémentation restent acquises avec leurs preuves.
- Les 3 revendications QA portent des propriétaires du run interrompu
  (`claude-odoo-tester-client_copy_qa`, `-high_runtime_qa`, `-high_static_qa`),
  posées à 14:21:22Z, sans aucun `complete` associé : travail inachevé.
- Aucun rapport QA, aucune couverture renseignée : `coverage.json` porte les
  8 critères tous en `missing`. Aucun critère n'est retiré ni assoupli.

## Décision
Libération des 3 revendications par `odoo_flow.py release`, motif : propriétaire
disparu à l'interruption contrôlée. Puis réattribution à trois sous-agents
`odoo-tester` réellement indépendants — leurs verrous sont compatibles
(lecture partagée sur `module_code`, écritures disjointes sur `client_copy`,
`qa_db_module` et trois artefacts distincts).
