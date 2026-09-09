# Q5 — reprise native dans le même environnement

**Reprise technique qualifiée sur ce cas ; chaîne complète non qualifiée à cause de C08.** Le code, le vrai message RPC, le fonctionnement SQL, la délégation et la reprise sont démontrés. La réception native déclare pourtant `VALIDÉ`, 8/8 et `pass` alors qu'une obligation littérale de la suite de tests reste sans preuve. Les productions natives sont conservées telles quelles.

## Protocole et périmètre

Référence `152aa737c7efc14cdba5c36b2e614ecb2715adb4`, augmentée des cinq fichiers Q1 figés dans `candidate-overlay.json`. Cas N04 complet neuf, série 19.0, avec A8 explicite ajouté **avant** l'appel : création négative via le vrai XML-RPC, phrase « Le nombre de jours doit être positif ou nul. » reçue et données conservées. Le contrat et le superviseur sont empreintés avant exécution (`frozen-SHA256.json`).

Deux appels maximum, Claude `opus`, effort `medium`, 900 secondes et `--max-budget-usd 12` par appel. Le superviseur coupe uniquement lorsque l'implémentation est terminée, au moins deux claims QA sont actifs et deux testeurs natifs ont effectivement démarré. Le second contexte reprend le même Lab vivant, les mêmes bases et le même dépôt Git. Aucune réparation manuelle du code ni des preuves générées ; aucun appel supplémentaire.

Le superviseur expérimental est archivé tel qu'exécuté dans `run_recovery.py`. Il contient les chemins de cette campagne et ne constitue pas encore un runner général de reprise.

## Chronologie mesurée

| Étape | Temps depuis le début de son appel | Résultat |
|---|---:|---|
| Analyste natif | 91,460 → 235,217 s | terminé |
| Développeur natif | 290,724 → 424,962 s | terminé |
| Premier testeur QA | démarrage 463,473 s | 13 progressions observées avant coupure |
| Deuxième testeur QA | démarrage 480,971 s | interrompu au démarrage |
| Coupure du premier appel | 481,100 s | SIGKILL contrôlé, 3 claims QA abandonnés |
| Reprise : trois testeurs | démarrages 100,537 / 116,961 / 133,865 s | tous terminés à 240,445 / 212,730 / 218,595 s |
| Fin du second appel | 400,590 s | flow complet, journal écrit, release ouverte |

Sept sous-agents réels attestés par `task_type=local_agent`. Les événements `local_bash` sont exclus. Le chevauchement commun des trois enveloppes natives de reprise est **78,865 secondes**. Cette mesure utilise les événements reçus de début et de fin : elle ne prouve ni calcul CPU simultané ni gain de temps, et le pont Odoo reste sérialisé.

## Continuité et contrôles réels

Les 55 identités de processus observées au premier appel ont disparu avant la reprise, pont drainé. L'orchestrateur de reprise a libéré les trois revendications avec preuve et motif, puis les a réattribuées. Il n'a rejoué ni briefing, ni analyse, ni implémentation.

Les identités du conteneur PostgreSQL, du cluster, des OID de `lab_client` et `lab_qa`, les inodes du projet et de `.git`, le HEAD, les décisions, le code et les lignes sont strictement identiques entre le relevé après coupure et celui avant reprise. Le code et les décisions restent également identiques après la fin de la reprise. `lab_qa` a ensuite été recréée volontairement par le test `--fresh` ; `lab_client` a conservé son OID et son serveur PostgreSQL.

**Limite sur les données à la coupure :** `lab_client` ne contenait aucune location à ce moment, conformément au seed N04 initial. La continuité du service et de la base est prouvée ; la conservation d'un jeu métier non vide *pendant cette interruption* n'est pas mesurée.

Les trois voies QA ont exécuté installation neuve, mise à jour, tests ORM et RPC de création/écriture négatives, jours nuls, lectures avant/après. L'oracle indépendant final confirme SQL 4/4 et RPC 3/3 : rejet réel, phrase exacte reçue, lignes avant/après inchangées. Les audits et sorties intégrales sont dans `state.json`, `bridge-*.log`, `oracle-000.log` et `external-rpc/`.

## Défaut sémantique observé

La revue fonctionnelle originale impose C08 :

> Étant donné la suite de tests du module, quand on exécute `/bridge/labctl qa lab_rental`, alors tous les tests passent, y compris les scénarios ci-dessus couverts par un vrai appel RPC (pas seulement des appels ORM internes).

La suite contient seulement des tests ORM. Le testeur exécution le signale. La synthèse reconnaît expressément qu'aucun test RPC n'y figure, puis valide C08 grâce aux appels XML-RPC séparés de la voie copie client. Cela démontre A8 et le comportement effectif, mais ne satisfait pas littéralement l'obligation attachée à l'exécution de la suite. Le contrôle Q1 maintient bien la cohérence du titre `VALIDÉ`, de la couverture déclarée 8/8 et de `pass` ; il ne décide pas si ces preuves remplissent sémantiquement le critère.

La reprise opérationnelle est donc acquise sur cet essai. La qualification globale de bout en bout reste refusée. Aucun critère, rapport ni code n'a été modifié par le superviseur pour obtenir ce verdict.

## Temps, coût et interventions

Durée des deux appels : **881,69 secondes**, hors préparation, vérifications de continuité et oracles finaux. L'appel interrompu n'a pas produit de coût final : **coût inconnu**, jamais remplacé par zéro. Le sous-total natif cumulatif de l'appel terminé est **2,8805147 USD** ; le total de la campagne demeure inconnu. Plafond configuré : 12 USD par appel, 24 USD pour les deux. Les événements `result` répètent un coût cumulatif : ils ne s'additionnent pas.

L'orchestrateur demandé est `opus/medium` et son modèle observé `claude-opus-5`. Les métadonnées cumulatives mentionnent aussi `claude-sonnet-5` et `claude-haiku-4-5` ; ces moteurs sont observés dans l’usage global, qui peut inclure des opérations auxiliaires. L’identité du modèle de chaque enfant n’est pas attestée.

Aucune intervention humaine après autorisation. Interventions du superviseur : coupure unique, drainage du pont, vérification des processus et ajout d'une note factuelle d'interruption. Libération, réattribution et consolidation ont été réalisées par l'agent. Nettoyage final des conteneurs et du réseau du préfixe vérifié : aucun résidu.

## Preuves

`SHA256.json` couvre 145 fichiers : protocole, superviseur, chronologies natives et de flow, identités aux frontières, projets après interruption et final, journaux QA/RPC, résultats et revue indépendante. Les sorties natives brutes et les homes restent dans le scratch privé ; leurs empreintes et les seules métadonnées fournisseur utiles sont publiables. Les fichiers originaux n'ont pas été normalisés ou corrigés.
