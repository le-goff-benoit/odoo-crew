# Exécuter ou reprendre un plan de release

Lis `docs/RELEASE_PLAN.md`, le briefing, `plan.json` et la revue de la release.
`odoo_plan.py status <release>` distingue dépendances et périmètres occupés.
Lis `docs/KNOWLEDGE.md` pour la mémoire partagée : transmets le briefing de
release à chaque agent, publie les découvertes pendant le travail et relis les
nouveaux acquis avant réception (`finish --knowledge`). Le fragment mémoire de
chaque tâche reçue devient immédiatement disponible aux suivantes.

Avant de lancer les tâches, lis `effort.json` et `estimation.md`. S'ils manquent,
applique `roles/estimation.md` au travail encore à venir ; ne fabrique pas de
prévision initiale pour les tâches déjà exécutées. Selon `docs/EFFORT.md`,
l'orchestrateur ouvre une mesure `odoo_effort.py start` pour chaque passage de
rôle et la ferme avec `stop` sur la même session. Les reprises ont leurs propres
entrées ; les attentes humaines sont hors chronomètre.

Pour une tâche prête, `odoo_plan.py start <release> --task ID` réserve son
périmètre et ouvre son flow. Applique `roles/orchestration.md` sur **ce flow** :
ne crée pas un deuxième run, ne rejoue pas une analyse déjà arbitrée sans raison.
Le risque du plan est un minimum ; les droits, la compta, la facturation ou les
données existantes imposent la voie renforcée même après un ticket support.

Reprends un flow actif depuis ses nœuds prêts. Un état local absent sur un autre
checkout demande une réconciliation depuis les preuves durables, jamais une
recréation silencieuse de statut vert. Une tâche bloquée ou périmée est rouverte
explicitement avec une raison (`reopen`) ; les anciens essais restent en historique.

Les flows équipés de la reprise de réception utilisent le même garde que les
tâches directes. Un conflit de mémoire après QA passe par `journal_task retry`
puis `reception_recovery_gate` dans **la même tentative** ; les périmètres du
plan restent réservés. Une publication interrompue se reprend avec
`publish-memory`, après reprise légitime de la revendication. Lis
`docs/TASK_RECEPTION.md` pour la migration explicite des anciens snapshots.
Après l'arrêt terminal `memory_task_blocked`, `reopen --reason` ouvre la voie à
une nouvelle tentative et conserve l'historique ; ne rouvre pas une tâche encore
active, ne supprime pas ses verrous à la main et ne déclare pas ses dépendants prêts.

Des tâches indépendantes peuvent être préparées en parallèle quand le moteur de
sous-agents est disponible. L'orchestrateur demeure l'unique écrivain de la
release et du journal. Les agents produisent des fragments isolés ; les verrous
du graphe continuent à borner les écritures. Si leurs ressources sont communes,
ils attendent ; n'annonce pas un parallélisme que le moteur n'a pas exécuté.

Après QA et journal : conserve un fichier de réception couvrant chaque critère,
un fragment de consolidation (décisions changées, questions ouvertes, ou raison
explicite d'absence de changement) et une preuve `odoo_evidence.py` sur tout le
périmètre. `odoo_plan.py finish` vérifie la fraîcheur avant de débloquer les
suivantes. La relecture métier de ces fichiers reste ta responsabilité.

Une nouvelle décision invalide les preuves concernées et celles des tâches
dépendantes. Note sa source et son remplacement dans la mémoire avant de reprendre.
Les tâches indépendantes déjà validées restent acquises si leurs preuves sont valides.
Termine les tâches autorisées et disponibles ; la clôture reste `/odoo-close`.

## Continuer réellement et rendre l'orchestration visible

Sur le modèle principal, ouvre `odoo_orchestrate.py activate --project ... --owner
... --provider ... --model ... --session-id ...` dès la préparation identifiable.
`attach --release ... --task A --task B` conserve son identité et déclare les tâches
que l'utilisateur a autorisées ; n'élargis pas une demande portant sur A à toute
la release. Les mutations suivantes exigent le même `--owner`. `progress --phase
...` marque les étapes ; `waiting-human`, `waiting-resource`, `pause`, `interrupt`,
`resume` et `complete` distinguent activité, attente et fin. Une attente porte un
`--reason`. Ne crée pas une nouvelle activité pour rafraîchir le chronomètre.

Après le résultat d'un agent, réceptionne ses preuves, relis `odoo_plan.py status`,
puis lance avec les outils la prochaine tâche autorisée et disponible dans le même
travail. Une phrase annonçant le lancement ne constitue pas ce lancement. Le hook
Stop fourni par `odoo_orchestrate.py hook` rappelle cette obligation uniquement à
la session principale liée ; il ne reçoit aucune preuve, ne libère aucun verrou et
ne lance aucun agent. Un arrêt d'enfant ne vaut jamais réception. Il respecte les
attentes, interruptions et limites fournisseur ; le rappel est borné à une relance,
sans boucle quand `stop_hook_active` est déjà présent.

## Contrôles stables et candidats parallèles

Pour les contrats à `checks`, réceptionne toutes les preuves via `finish
--check-proofs` (objet ID → chemin), ou `--proof` pour un contrôle unique. Les
commandes et environnements doivent correspondre exactement au contrat ; une
commande réussie différente ne remplace pas le contrôle prescrit.

Une nouvelle preuve a un nouveau chemin : les logs et preuves existants restent
immuables. Une réception renouvelée avec le même contrat, sources et résultat ne
fait pas rejouer les dépendants pour sa seule date. Une source, interface, entrée
ou décision pertinente changée demande un nouveau contrôle ; une dépendance
inconnue reste conservatrice. Les lectures réelles figurent dans `reads` et dans
la preuve ; une sélection `check_scopes` exige un motif d'impact, reste interdite
en risque élevé et ne remplace jamais la recette d'intégration finale.

Une QA de A peut tourner pendant B indépendant : à la borne QA sans revendication,
fige A dans un worktree de même dépôt/révision avec `odoo_candidate.py freeze` et
ses identités physiques database/filestore/port/container/logs. Les ressources de B
doivent aussi être déclarées et disjointes, avec le même registre physique partagé
déclaré dans `resources.json` ; l'autorité des `claim` reste atomique.
Le candidat doit contenir exactement les sources annoncées. Délègue la QA en
lecture sur ce candidat et le développement de B sur son propre périmètre ; ne
fais jamais écrire deux agents sur le candidat. Une mutation du candidat refuse
la réception. Si B dépend du résultat A, attends la réception A. L'orchestrateur
intègre seul les résultats et contrôle ensuite le candidat commun de release.
