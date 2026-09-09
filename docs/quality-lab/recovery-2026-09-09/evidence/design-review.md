# Reprise mémoire après QA — revue indépendante

Référence : `8d2b940`. Lecture seule du dépôt ; reproduction synthétique dans `/tmp/odoo-recovery-20260909/design`. Aucun Odoo, fournisseur payant ou donnée client.

## Blocage démontré

`design/reproduce.py` exporte les scripts/graphe/tests de la référence et initialise une fixture à la jointure QA (jetons synthétiques, explicitement pas une exécution métier). Après pass et claim journal, une publication concurrente :

- invalide `odoo_reception.verify_bundle(..., published=False)` ;
- empêche `complete journal_task done` ;
- empêche `prepare-reception` avec `préparation impossible après réception QA` ;
- ne permet aucune sortie blocked de journal, seulement done ;
- empêche `odoo_plan.mutate(..., reopen)` puisque le flow reste running.

Après copie du seul PROJECT approuvé, check-bases refuse le PROJECT changé tandis que done refuse le JOURNAL non encore publié. Chaque refus préserve exactement le fichier d'état. Résultats : `design/reproduction.json` ; fixtures conservées dans `design/project`.

## Proposition retenue après échange avec l'orchestrateur

1. Publication outillée idempotente sous la revendication `journal_task` : les deux cibles peuvent être chacune soit dans leur état avant, soit identiques au draft approuvé. Prévalider **toutes** les cibles et pièces avant toute écriture ; écrire seulement les cibles encore avant, via remplacement atomique par fichier. Toute troisième valeur bloque sans écrire. Revalider et conserver la revendication jusqu'à la complétion du journal.
2. Retour explicite dans le graphe : `journal_task --outcome retry` vers un **nouveau** `reception_gate`, puis pass vers journal. Ne jamais retourner aux trois gates existantes `join=all` : cela nécessiterait de recréer des jetons représentant des travaux non rejoués.
3. Seules les bases et propositions mémoire sont renouvelables dans ce retour. Demande, décisions, contrat QA, preuves et code restent identiques aux références acceptées et frais. Tout changement de ces éléments exige une autre voie de travail ; il ne peut se cacher dans une « réception mémoire ».
4. Nouvelle conversation de réception, nouveau bundle, nouveau reçu ; archiver les références antérieures. Le dernier pass remplace l'acceptation active sans supprimer les pass précédents. Aucun reçu lié à l'ancien bundle ne suffit.
5. Retour borné à deux révisions, sortie blocked accessible au journal et à la réception vers un arrêt dédié. Son libellé doit décrire l'échec de publication/réception, pas prétendre que les tests Odoo sont rouges. Le terminal permet `plan reopen` puis une nouvelle tentative lorsque nécessaire.
6. Après preuve sur plans, retirer l'interdiction `state.get('plan_task')` de prepare-reception. Les réservations de périmètre du plan persistent pendant la reprise du même flow ; les autres tâches indépendantes peuvent continuer hors verrou de mémoire.

Le bundle accepté est déjà une intention durable contenant les états avant et après de chaque fichier. Un second fichier d'intention n'est pas nécessaire pour la reprise **d'une interruption de processus** : chaque cible est reconnue indépendamment, la publication est idempotente et la revendication logique survit au processus. Cela ne promet pas une transaction atomique entre deux fichiers ni une résistance aux coupures électriques sans fsync.

## Comparaison avec abandon et nouvelle tentative

Une sortie terminale explicite suivie de `plan reopen` est sûre et plus simple à raisonner seule. Elle préserve le contrat et les preuves dans l'historique, mais remet la tâche à pending et reparcourt le graphe de développement pour un simple conflit de mémoire. Il faut alors éviter une répétition métier indue et prouver la fraîcheur des artefacts réutilisés.

La réception_gate dédiée conserve le bénéfice de la QA passée tout en invalidant uniquement la proposition de mémoire. Elle demande quelques vérifications supplémentaires (phase de reprise, bundle actif, historique, compteurs), mais répond mieux à la reprise ciblée. Garder une sortie terminale bornée comme issue de secours.

Une annulation administrative qui écrit seulement status=cancelled serait trompeuse ici : le graphe existant décrit cancelled comme consécutif à une décision humaine. Ajouter une vraie sortie autonome motivée, sans fabriquer une confirmation humaine.

## Points précis d'intégration

- `scripts/odoo_flow.py::prepare_reception` : actuellement interdit tout plan et tout pass historique. Autoriser après pass uniquement au nouveau nœud de réception revendiqué par owner, avec références sources/spec/evidence/scopes/code initiales inchangées. Les claims d'autres propriétaires restent interdits. Avant pass initial, comportement actuel inchangé.
- `verify_task_reception` : reconnaître la nouvelle porte pour l'acceptation, sans élargir aveuglément `odoo_coverage.GATES` (qui sert aussi aux contrats et aux rapports QA). Le journal done continue de comparer la mémoire au bundle nouvellement accepté. Un pass historique ne doit jamais masquer la phase de réception active.
- `complete_claimed_node` : le passage retry archive/invalide l'acceptation courante de façon transactionnelle avec le déplacement du jeton. Les refus conservent état et registre byte-identiques. `accepted_reception` ne doit changer qu'une fois la transition validée.
- `odoo_reception.verify_bundle` : séparer la vérification des pièces/code de la politique de cible (avant, après, avant-ou-après), sans désactiver les empreintes de preuve imbriquées. Pour préparer une réception de reprise, la fraîcheur des sources/code doit être vérifiable même si les anciennes bases mémoire sont justement périmées.
- Publication : commande flow recommandée plutôt qu'un outil autonome recevant seulement un bundle, afin d'exiger le flow actif, le bon journal revendiqué, le bon owner et le reçu effectivement accepté. Ordre de verrouillage cohérent : state puis registre si nécessaire. Aucun auto-claim ni déverrouillage d'un autre propriétaire.
- `odoo_plan.task_status`, `available`, `mutate` : running reste running en réception ; scopes réservés. Un vrai terminal blocked permet reopen, dont l'historique conserve déjà la tentative. Aucun statut validated avant graph complete + finish. Les nouvelles réceptions de dépendances continuent d'invalider les reçus dépendants.

## Compatibilité avec les anciens snapshots

`load_state` exige actuellement le hash exact du graphe fourni. `validate_migration` refuse une nouvelle arête impliquant le journal pending, même si toutes les anciennes transitions restent présentes. Une simple mise à jour du graphe empêcherait donc la reprise des anciens flows.

Prévoir une migration **explicite et bornée** : sans revendication active, avant exécution de journal_task, vérifier l'intégrité du snapshot historique puis autoriser uniquement l'ajout connu du sous-graphe de reprise et son compteur retry. Toutes les anciennes arêtes, tous les autres nœuds et toutes les métadonnées de ressources doivent rester identiques. Refuser toute autre modification, notamment droits humains, verrou mémoire, outcomes historiques ou destination d'un pass existant. Consigner migration et empreintes anciennes/nouvelles ; ne modifier ni tokens ni événements métier passés. Les flows sans garde continuent sous leur contrat historique.

Une migration automatique silencieuse, une remise à zéro des événements ou une permission générique « ajout d'arêtes sûr » serait trop large. Un ancien flow déjà terminé ne doit pas être rouvert par ce mécanisme.

## Concurrence et interruptions

- Deux flows peuvent passer QA depuis la même mémoire initiale. Le premier publie sous verrou ; le second détecte le changement, quitte proprement journal vers réception, libère le verrou, reçoit de nouvelles propositions incluant le travail du premier puis publie.
- Une interruption après le premier remplacement laisse une paire mixte avant/draft. Le processus suivant avec le même owner reprend uniquement le second fichier ; aucun doublon ajouté au journal.
- Une interruption après les deux remplacements avant complete laisse les deux drafts et la revendication active ; la répétition ne réécrit rien, puis complete fonctionne.
- Après release explicite, un autre writer pourrait produire une troisième valeur : prévalidation globale bloque l'ensemble de la nouvelle publication. Ne pas restaurer les anciennes bases pour « débloquer » le contrôle.
- Le verrou est coopératif : une écriture externe ignorant le protocole entre prévalidation et remplacement n'est pas rendue impossible par ces commandes. Ne pas revendiquer un verrou de fichier système empêchant tout programme d'écrire.
- Un crash après write_state avant write_registry se réconcilie via le prune existant ; vérifier les chemins exacts pour que stale claims n'interdisent pas la suite. Pas de suppression de claims d'un propriétaire encore actif.

## Tests nécessaires

1. Reproduction rouge ci-dessus, puis conflit identique résolu sans perte et sans retouche des fichiers d'état.
2. Deux vrais agents préparant des tâches indépendantes, orchestration seule aux mutations partagées ; B conserve intégralement la mémoire publiée par A après nouvelle réception.
3. Positif sans conflit : une seule réception, exact publication, flow complete puis plan validated.
4. Publication interrompue avant écriture / après premier remplacement / après second remplacement : reprise idempotente, aucun doublon, preuves stables.
5. Prévalidation globale : première cible avant mais seconde tierce ; aucune cible écrite. Cible symlink / source ou draft altéré : même refus sans effet.
6. Nouvelle réception : ancien reçu refusé, nouveau reçu pass requis ; demande/code/preuve/contrat altéré interdit de se prétendre reprise mémoire.
7. Claims concurrents : aucune seconde écriture mémoire, aucun déverrouillage abusif ; transfert owner explicite possible via release/claim.
8. Deux reprises puis arrêt réel ; plan reste non validé et reopen est possible seulement après terminal.
9. Migration ancienne référence autorisée uniquement pour le delta prévu ; ancien flow terminé, claims actifs, graph tampered, changement de verrou ou gate historique refusés.
10. Sans garde, support/fonctionnel/validation et snapshots compatibles ne se voient pas imposer une réception factice.

Aucun fichier canonique modifié par cet agent.
