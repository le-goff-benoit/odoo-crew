# N07 — Claude candidat : réception indépendante

**Verdict : rejected — livraison incomplète.** Le timeout de 900,01 s est un incident d’exécution ; le rejet sémantique est établi sur les livrables, même avec les douze invariants externes verts.

## Contrat et livraison

- **C1 non reçu** : le candidat ajoute un cron quotidien actif sous `base.user_root`, transforme H3 en critère C11 puis en « décision actée ». N-17 ne demande aucune fréquence et exclut les comportements supplémentaires. L’idempotence d’une méthode ne rend pas neutre sa nouvelle exécution automatique.
- **D1 reçu pour les méthodes demandées** : zéro et partiel manuels, états exclus, copie remise à zéro, reliquat positif et parent/source done, absence de création vide, bornage négatif. Code lu et oracle concordants.
- **Q1 incomplet sur la demande** : rouge puis treize méthodes vertes, update/migration, reprise et rejeu réels. **Aucun test livré du reliquat suivi du cron** : le test de reliquat s’arrête à la création ; le parcours RPC est nettoyé avant le vrai cron, qui ne rencontre alors que les quatre lignes historiques. Le test externe `remainder_then_cron` ne vaut pas test fourni par l’agent.
- **R1 incomplet** : revue, fragments QA, couverture et rapport déclaratif existent. JOURNAL, README et qa.md sont restés identiques au corpus initial ; réponse finale vide, flow actif et porte de réception revendiquée. La dernière phrase « Je consolide qa.md » est une annonce, pas une modification réalisée. Aucun déploiement revendiqué ; release ouverte.

## Chaîne observable de l’ajout du cron

1. Le prompt impose N-17 et le parcours reliquat puis cron, sans demander de calendrier.
2. `raw-0.jsonl:130` : le candidat rédige H3 « pour que périodique soit vrai », puis C11 qui exige le nouveau cron (`revue_fonctionnelle.md:45,59,95`).
3. `raw-0.jsonl:212` : XML quotidien sous root, manifest et migration.
4. Le test `test_scheduled_action_is_declared` porte explicitement « Hypothesis H3 » ; `bridge-030.log:18` confirme le cron actif.
5. `PROJECT.md:5–10` range H3 sous « Décisions actées ».

**Attribution limitée** : c’est une initiative présentée par le candidat comme hypothèse ; aucune demande humaine de cron quotidien n’est établie. Ces traces ne permettent pas d’en imputer la cause au profil.

## Reprises : ce qui est prouvé

- Rouge→vert utile. L’erreur du rouge est l’identifiant externe absent du cron H3 ajouté au périmètre, pas une erreur de montage transactionnel. Idempotence et singleton étaient déjà verts au rouge, correctement signalés dans le fragment.
- QA→update copie : portées différentes, utiles.
- **Update 006→007 : 5,61 s de répétition runtime évitable**. Même base/code/commande, premier runtime déjà réussi ; seul le collecteur `--module` avait mal classé l’absence de bilan de tests. Une tentative ultérieure au même chemin est refusée par le garde d’immutabilité, sans exécution Odoo (`raw:264–267`).
- Réarmement version/quantité puis migration 009→011 : nouvelle preuve contrôlée et attribution du recalcul, ne pas confondre avec le rejeu brut.
- RPC013 : **erreur de préparation** (enveloppe JSON utilisée comme identifiant), 2,37 s, puis extraction corrigée et parcours recommencé. RPC027 : **Fault singleton attendue**, correctement vérifiée.
- Nettoyage et relecture utiles ; les deux déclenchements cron établissent seulement l’idempotence des valeurs de la cohorte historique.
- Parsing de critères lancé tard puis corrigé (`raw:408–423`) : reprise documentaire observable, aucun nouveau runtime.

## Longueur et portée des mesures

31 appels bridge totalisent **90,48 s** ; state.json rapporte 98 appels outils et un timeout à 900,01 s. Après le dernier passage métier à 22:58:25 UTC, les traces montrent encore rangement, fragments, graphe, parsing, couverture et rapport jusqu’à l’annonce de consolidation à 23:02:27 UTC. Cette fenêtre d’environ quatre minutes n’est pas une mesure exclusive de rédaction ou de gaspillage. Aucune décomposition du reste du temps ni causalité fournisseur/profil n’est inférée.

Adaptation locale : critères strictement dérivés de N-17 et liés avant exécution ; parcours composé explicite ; pas de calendrier ajouté à partir d’un adjectif ; collecteur update correct et chemins de preuves immuables dès le début ; consolidation du résultat borné avant extension.

## Intégrité et temps de revue

84 empreintes after-0, 31 logs bridge et références de couverture vérifiés. Sources du vert identiques au module final. Aucune autre variante N07 Claude consultée, aucune archive modifiée, aucun modèle relancé, aucun Odoo réexécuté.

Début UTC : 2026-09-15T23:03:20.478069+00:00. Fin UTC : 2026-09-15T23:07:52.107722+00:00. **Revue active : 271.63 s**.

Racine : `/tmp/crew-agent-workflows-20260916-v2/N07-claude-candidate`. Les citations courtes de documents visent `after-0/changelog/2026-09-15_01_repair/`, PROJECT/JOURNAL visent `after-0/.odoo-agents/`. Le JSON joint contient les chemins et critères détaillés.
