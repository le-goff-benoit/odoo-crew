# Exécuter ou reprendre un plan de release

Lis `docs/RELEASE_PLAN.md`, le briefing, `plan.json` et la revue de la release.
`odoo_plan.py status <release>` distingue dépendances et périmètres occupés.

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
