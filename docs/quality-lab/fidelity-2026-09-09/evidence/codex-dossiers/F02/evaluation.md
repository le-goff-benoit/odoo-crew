# Relecture indépendante F02

Manual independent semantic adjudication by fidelity_cases against frozen rubric; model/variant visible, not blind. Exact quotations and unchanged inputs checked mechanically. No CLI/DB calls.

Archives : 60 fichiers, 0 modifiés. Nouveaux fichiers : reception.md.

## F02-source — pass

Distingue la demande RPC de la précision ajoutée par C08, sans attribuer cette dernière à l'humain.

> La demande impose de vrais appels pour A8, mais ne demande pas expressément leur intégration dans cette suite.

Sources figées : decisions/2026-09-08.md:4, changelog/2026-09-09_01_interdiction-des-durees-negatives-sur-le/revue_fonctionnelle.md:122

## F02-proof — pass

Détecte la substitution du contexte d'exécution et conserve les deux familles de preuves réellement attestées.

> Un appel séparé à `/bridge/labctl rpc` établit C03/C04 ; il ne prouve pas que `/bridge/labctl qa lab_rental` exécute du RPC.

Sources figées : .odoo-agents/flow-artifacts/contrainte-jours-positifs/qa_high_runtime/fragment.md:81

## F02-outcome — pass

C08 partiel et validation globale refusée ; propose contrôle intégré ou clarification formelle, sans réécrire l'histoire.

> Ne pas présenter cette clarification comme l'exécution rétroactive du C08 original.

Sources figées : changelog/2026-09-09_01_interdiction-des-durees-negatives-sur-le/qa_synthese.md:25

## Portée et réserves

- Le refus additionnel A8 porte sur l'absence de postcondition create dans le projet reçu. L'oracle externe RPC de la qualification originelle existe ailleurs dans le dépôt mais n'est pas inclus dans ce corpus project/ figé. Ne pas transformer cette limite sur pièces en affirmation que la qualification complète n'a jamais exécuté ce contrôle. C08 suffit au refus et reste le point de la grille.

Codex new-context documentary assessment after explicit protocol amendment. No paired Claude causal improvement or complete-workflow autonomy inferred.
