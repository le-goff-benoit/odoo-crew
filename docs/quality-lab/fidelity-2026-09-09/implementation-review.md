# Revue indépendante de la réception de tâche

09/09/2026. Lecture seule des fichiers canoniques ; reproductions déterministes dans des projets temporaires ne contenant aucune donnée client. Aucun appel LLM payant ni Odoo/DB. Révision en cours de modification par l'orchestrateur et ses agents : ce rapport distingue l'état initial et les correctifs vus ensuite.

Fichiers relus : scripts/odoo_reception.py, diff scripts/odoo_flow.py, tests/test_odoo_reception.py, docs/TASK_RECEPTION.md et les trois rôles modifiés. Les résultats des sondes sont dans `review-probe-initial-results.json` (transcription de la première sortie outil conservée) et `review-probe-after-owner-fix.json`. Scripts scratch : `review_probe.py`, `review_probe_v2.py`.

## Verdict

La structure choisie reste limitée et compréhensible : activation par flow, préparation en fichiers neufs, trois axes, citations exactes, vérification des groupes/document/code, mémoire proposée conservée jusqu'au pass, revalidation à publication et sorties rouges qui restent ouvertes avant pass. Les flows historiques sans garde conservent leur fonctionnement. Les limites sémantiques sont correctement annoncées.

Trois problèmes opérationnels sont reproduits. Le premier a été corrigé pendant cette revue et son refus confirmé. Le deuxième est confié au développeur par l'orchestrateur. Le troisième peut devenir une limitation assumée pour les tâches directes, mais empêche le contournement documenté dans un plan de release.

## R1 — reviewer égal au nouveau propriétaire de complétion : corrigé, refus reproduit

État initial : prepare sous owner A ; libération normale du claim ; revendication par B ; fragment signé reviewer B ; complete sous owner B. Toutes les opérations utilisent les API publiques normales, sans édition du state. Résultat : pass, parce que `verify` compare uniquement au propriétaire préparateur stocké dans le bundle.

Correctif vu : `verify_task_reception(..., owner)` refuse désormais le reviewer identique au propriétaire courant de complétion. La deuxième sonde reçoit bien « reviewer identique au propriétaire actuel de complétion ». Maintenir un test de ce transfert A→B et un positif où B complète une réception signée C. L'identité demeure déclarative ; le correctif contrôle la règle annoncée sans prétendre identifier un vrai contexte indépendant.

## R2 — réception indépendante de la mauvaise spec : correction nécessaire

Reproduction : `bind-criteria` épingle `bound-spec.md`, qui contient une obligation ; la couverture de ce contrat est formellement complète. `prepare-reception` reçoit `spec.md`, distinct, et produit son bundle. La réception indépendante cite cette autre spec ; complete reçoit les deux documents et donne pass. Aucune modification du state ni des bundles épinglés.

Conséquence : la couverture et la nouvelle réception peuvent chacune valider des contrats différents. Cette disjonction est mécanique, différente de la limite sémantique assumée d'une source manquante ou d'un jugement faux.

Traitement : lorsque `qa_contract` existe, vérifier que le groupe spec du bundle désigne exactement sa source canonique et son `source_sha256`. Vérifier à la préparation pour donner l'erreur tôt **et à la complétion**, car bind-criteria peut survenir après prepare-reception. Ne pas exiger la présence de qa_contract sur les flows historiques qui ne l'utilisent pas. Tests : spec différente refusée dans les deux ordres de liaison ; même source acceptée ; mutation de source toujours refusée ; refus sans changement claims/registry/tokens.

## R3 — invalidation après pass : limite opérationnelle, pas récupération livrée

Reproduction : la jointure passe ; une autre tâche ajoute une entrée au JOURNAL avant la prise du verrou mémoire ; claim journal_task ; conserver cette entrée au lieu de l'écraser. La copie PROJECT conforme est faite pour isoler le conflit JOURNAL. Résultats :

- prepare-reception : « préparation impossible après réception QA » ;
- journal_task done : « publication différente du draft approuvé : .odoo-agents/JOURNAL.md » ;
- journal_task blocked : « issue invalide (...) attendue parmi done ».

L'ancien flow reste actif ; `release` libère son claim, ne consomme pas le jeton et ne le termine pas. Il n'existe aucune commande terminale générique cancel/abort/abandon dans odoo_flow.py. Les instructions initiales « reprends préparation et réception avant le pass » étaient impossibles dans cet état ; leur remplacement vu par « nouveau flow, premier non terminé » décrit maintenant une limite réelle.

Pour une **tâche directe**, compromis acceptable dans cette campagne étroite : vérifier les bases sous verrou avant toute copie, laisser les fichiers concurrents intacts, déposer l'incident dans un fragment neuf, libérer le claim avec raison, ouvrir un nouveau flow explicitement relié à l'ancien. Ne jamais appeler le premier terminé, ne jamais réécrire ses événements ou supprimer le garde. Risques : accumulation de flows actifs et alerte d'intervention encore en cours ; travail de réception répété après une modification sans rapport.

Pour une **tâche de plan**, le même contournement ne fonctionne pas. `odoo_plan.task_status` retourne running pour tout flow actif, même sans claim ; `mutate(...reopen/defer...)` refuse running ; `available` refuse un start si non-pending et réserve le périmètre des tâches running. Ouvrir un flow direct supplémentaire ne le rattache pas à la tentative du plan et ne libère pas ses dépendances. Il faut donc :

1. soit borner l'adoption actuelle aux tâches directes (mode documentaire toujours possible sur plan, garde expérimental/non activé), et écrire explicitement la limite de plan ;
2. soit traiter un arrêt officiel dans une évolution séparée. Une transition journal_task→journal_task_blocked pour les nouveaux snapshots est une option cohérente avec l'autorité du graphe ; un abort spécifique doit lui aussi produire un état terminal, une preuve et la libération atomique des claims. Ne pas modifier silencieusement les snapshots historiques pour simuler cet arrêt.

Le helper `check-bases` ajouté pendant la revue rend l'interdiction de copie concrète ; il doit être appelé sous le verrou mémoire, dont la vérification reste coopérative. Le lien à l'empreinte du flow est recontrôlé à complete : le helper seul ne vaut pas réception.

## Points non retenus comme défauts supplémentaires

- Un axe source_memory peut citer un seul draft : minimum mécanique explicitement documenté ; l'exhaustivité de la relecture est une responsabilité sémantique. Ne pas transformer cette limite assumée en faux bug.
- Les scopes code facultatifs et les logs libres n'offrent pas les mêmes garanties que les preuves structurées : limitation annoncée, pas une prétention à une preuve d'environnement.
- Les codes d'échec dans un dossier peuvent être des preuves valables d'un scénario négatif. Ne pas imposer arbitrairement require_success=True à toute pièce imbriquée sans distinguer le contrôle de sa postcondition.
- Les checks de cibles canoniques, fichiers neufs, drafts distincts, sous-chemins dans le projet et mutations de contenu sont raisonnables pour ce dispositif coopératif. Aucune faille de chemin supplémentaire reproduite.

Ce rapport ne réexécute pas la campagne comportementale ni toute la suite unitaire ; l'orchestrateur assure ces contrôles après stabilisation des corrections. Les constats R1/R2 viennent d'exécutions déterministes publiques, et R3 des mêmes API avec comparaison des transitions/plan.

## Contre-vérification finale sur candidat stabilisé

Rejeu indépendant effectué après le message de stabilité du développeur, sans modifier les constats initiaux ci-dessus. `review_probe_final.py` et `review-probe-final-results.json` conservent les appels et les empreintes des trois fichiers contrôlés.

- **R1 fermé** : prepare A, claim transféré à B, reviewer B → refus ; state et registre restent identiques. Contrôle positif prepare A, claim B, reviewer C → pass.
- **R2 fermé** : spec différente refusée à prepare-reception lorsque bind-criteria précède ; également refusée à complete lorsque prepare-reception précède la liaison du contrat. Chaque refus conserve state et registre.
- **R3 borné, non réparé** : prepare-reception refuse désormais explicitement les flows portant plan_task, sans modifier state ni registre. Le mode documentaire sans garde reste possible. Le contournement par nouveau flow demeure limité aux tâches directes ; l'ancien flow reste non terminé et la limite de concurrence après pass reste assumée.

Verdict final de cette revue technique : **les défauts mécaniques R1/R2 sont corrigés et contre-vérifiés ; le garde peut poursuivre sa qualification dans son périmètre expérimental de tâches directes**. Aucune récupération complète après pass ni compatibilité du garde avec les plans n'est affirmée. La décision d'adoption sémantique reste conditionnée aux essais natifs séparés.
