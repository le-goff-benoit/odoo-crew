# Préparer une release de plusieurs demandes

Cette commande prépare le travail sans lancer le développement. `/odoo-new`
reste la voie directe pour une demande de bout en bout ; `/odoo-plan` puis
`/odoo-start` conviennent à plusieurs tâches, dépendances ou reprises.

**Mesure du cadrage, avant l'analyse** : dès que le projet et la session native
sont identifiés, lis `docs/EFFORT.md` (section « Cadrage avant release ») et lance
`odoo_effort.py prepare-start <projet> --agent odoo-analyst --provider codex|claude
--source <trace-native>`. Conserve l'identifiant retourné. Aucune release ni tâche
n'est nécessaire. Si la trace n'est pas identifiable, annonce la mesure absente
et poursuis le cadrage ; n'invente pas une durée ni un compteur initial.
À une reprise, consulte `prepare-status` : ne démarre pas deux mesures sur la
même période. Ferme le passage avant une attente humaine ou un changement de rôle,
puis ouvre une nouvelle entrée au retour. Une borne perdue exige `prepare-interrupt`.

Lis le briefing et applique `roles/functional-review.md`. Conserve chaque demande
originale, les décisions actées et les questions encore bloquantes. Ouvre ou
réutilise la release avec `odoo-release.sh`. Rattache uniquement les entrées de
cette demande par `prepare-attach <projet> --entry <id> --release <release>`.
Pour les passages suivants de cadrage commun, `prepare-start --release <release>`
conserve ce rattachement dès le départ. Écris la revue globale, puis un
`plan-definition.json` suivant `docs/RELEASE_PLAN.md` : chaque tâche a un résultat
métier, des critères, une voie, un risque, des dépendances et des périmètres.
Une question bloquante reste dans la revue ; ne crée pas une tâche exécutable
fondée sur une réponse inventée.

Distingue une donnée de test provisoire d’un résultat explicitement demandé.
Évite les assertions figées sur un état intermédiaire, mais conserve les valeurs
finales si la demande les prescrit. Un cas limite ajouté au plan (égalité de
séquence, répétition d’une opération…) ne crée pas une règle métier : vérifie le
standard ou formule la question avant d’en faire un critère obligatoire. Une
amélioration souhaitable hors intention reste une proposition identifiée.
Avant de figer le plan, confronte chaque critère à sa phrase source : aucune
sortie demandée ne doit disparaître au profit d’une propriété plus générale.
Si la demande fixe un remplacement précis, vérifier seulement l’ordre, la somme
ou l’absence d’erreur ne suffit pas. Les commandes de contrôle sont des tableaux
d’arguments exécutables, jamais des phrases telles que « test à ajouter » ; le
fait que le fichier de test sera créé par le développement s’indique séparément.

Valide la définition avec `odoo_plan.py init <release> --file <définition>`.
Le fichier versionné `plan.json` est le plan ; les flows restent l'autorité des
étapes exécutées. Applique `roles/estimation.md` avant l'exécution : chaque tâche
reçoit une prévision en minutes par rôle, avec fourchette et hypothèses ; le
travail commun de clôture est compté une seule fois. `odoo_effort.py init`
reprend les identifiants du plan, puis `estimate` et `report` produisent
`estimation.md`. Présente les tâches prêtes, leur prévision et les arbitrages restants.
Termine la préparation avec `prepare-stop <projet> --entry <id> --source <trace>`
et actualise le bilan avec `report <release>`. Le cadrage reste « Préparation du
plan », sans prévision rétrospective. Dès qu'une tâche est déclarée et qu'un
nouveau passage lui est dédié, ferme la préparation puis emploie `start --task`
du registre de release ; ne redistribue jamais le travail passé entre les tâches.
Préparer ou ouvrir un document ne démarre pas l'exécution. Si l'utilisateur a
explicitement demandé d'exécuter aussi, continue avec `/odoo-start`.

Pour une nouvelle demande dans un plan existant, `odoo_plan.py add <release>
--file <definition-ajouts.json>` conserve l'historique et les réceptions. Ne
réinitialise pas le plan et ne remplace pas un identifiant existant. Les nouvelles
dépendances restent explicites et les tâches déjà reçues ne sont pas rejouées
sans changement de contrat, de preuve ou de dépendance.
Ajoute la prévision des nouvelles tâches et motive toute révision des autres ;
conserve l'estimation initiale et les mesures déjà enregistrées.

## Intentions → Plan

L'orchestrateur, sur le modèle principal de la session, écrit lui-même le plan à
partir des demandes originales et décisions de la release. Il peut déléguer une
investigation indépendante ; il conserve l'arbitrage et les critères de succès.
Avant le découpage, constitue `intentions.json` avec `odoo_intentions.py update` :
source conservée, résultat attendu, critères, contraintes, décisions et questions.
Enregistre chaque nouvelle demande dès sa réception dans la release ouverte,
sans attendre la fin de la revue globale : `clarify` si des questions restent,
`ready` si elle peut être planifiée. Le cockpit la montre comme demande à
planifier, sans autorisation de développement. Lors du découpage, conserve son
identifiant et lie les tâches retenues ; motive un report dans les décisions.
Ne supprime pas la demande originale lorsque le plan la reformule ou la remplace.
Une question sans réponse empêche la tâche concernée de démarrer. Pour les nouveaux
plans multi-demandes, emploie le schéma 2 décrit dans `docs/RELEASE_EXECUTION.md` ;
les plans historiques au schéma 1 restent lisibles.

Chaque tâche relie ses intentions ou motive son prérequis technique. Fige avant
exécution les cas de données, commandes de contrôle, environnement, lectures et
écritures, dépendances de résultat, ressources physiques, fournisseur, modèle et
effort. Un correctif trivial conserve un contrat court avec un seul contrôle utile.
Pour deux changements d'un même rapport, arbitre ensemble la hiérarchie et les
valeurs attendues avant de découper ; un test de séquence ne fixe pas une valeur
qui doit légitimement changer dans la tâche suivante. Ne confonds pas partage de
ressource et dépendance de résultat.

Une nouvelle intention conserve les précédentes. `odoo_plan.py revise --file ...
--reason ...` révise seulement les contrats concernés et archive leur ancienne
version. La satisfaction d'une intention exige la correspondance explicite de
chacun de ses critères vers un critère réceptionné de tâche (`coverage`), ou une
preuve de solution standard vérifiée ; les seuls liens de tâches ne suffisent pas.

## Prévenir les reprises coûteuses

Avant de figer une règle sur des données existantes, consigne dans la revue une
petite cohorte contradictoire (courant, historique, contre-exemple) avec acteurs,
états et valeurs attendues. Distingue dépendance de résultat et ressource partagée.
Prévois le point de contrôle commun une fois au niveau utile, puis valide les
anomalies dans un canal atteignable (UI/RPC/cron/import). Classe chaque reprise :
critère initial manquant, intention tardive, hypothèse réfutée, régression,
incident d'outillage ou simple conflit mémoire ; un nombre de reviews seul ne
mesure pas la qualité du plan.

Si la livraison est demandée, fixe aussi commit de base, build cible et effets
à relire suivant `docs/DELIVERY_GUARD.md`. Le statut « reçu localement » ne devient
pas « déployé » par un push. Ces contrôles restent distincts de la recette métier.
