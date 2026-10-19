# Un consultant Odoo, plusieurs compétences

Un seul interlocuteur pour comprendre le besoin métier, conseiller le client,
configurer Odoo, développer, vérifier le résultat et conserver les apprentissages.
Disponible dans Claude Code et Codex, avec les sources de la série du client.

[Installation](docs/INSTALL.md) · [Mémoire](docs/KNOWLEDGE.md) · [Contrôles et limites](docs/quality-lab/README.md)

[Release du 19 octobre : consultant unique et fiches d'apprentissage](release/2026-10-19/README.md)

## Une entrée, des procédures spécialisées

Le skill **`odoo-consultant`** est l'entrée habituelle. Décrivez directement le
résultat attendu ; le consultant mobilise les compétences nécessaires dans la
même session. Il ne crée pas un agent BA, AM, développeur ou testeur à chaque étape.
La délégation est réservée à une demande explicite de l'utilisateur. Le modèle
principal reste inchangé et une auto-relecture n'est jamais dite indépendante.

| Compétence | Ce qu'elle apporte |
|---|---|
| Analyse métier / BA | Besoin réel, standard existant, critères et arbitrages. |
| Conseil client / AM | Périmètre, offre, ateliers, hypothèses, responsabilités et suivi. |
| Expertise fonctionnelle | Modules installés, dépendances, règles métier et sources officielles. |
| Configuration / développement | Standard, Studio ou module custom, selon le projet et sa série. |
| Qualité / support | Diagnostic, contrôles proportionnés, résultats et limites vérifiables. |
| Livraison | Candidat, GitHub/Odoo.sh, autorisations et observation du résultat livré. |

Les procédures se chargent au besoin : [consultant](roles/consultant.md),
[conseil client](docs/roles/client-advisory.md), [expertise métier](docs/roles/domain-expertise.md).
Aucun profil ne garantit une connaissance universelle : le consultant vérifie les
sources pertinentes et distingue ce qui est observé de ce qui reste hypothétique.
Les estimations de prestation humaine sont séparées des minutes d'exécution IA.

Les commandes `/odoo-new`, `/odoo-plan`, `/odoo-start`, `/odoo-close`,
`/odoo-feedback` et `/odoo-improve` restent disponibles. Les anciens profils CLI
restent compatibles comme modes spécialisés. Les flows existants gardent leurs
contrats, verrous et preuves ; un garde de réception indépendante déjà lié n'est
jamais contourné au motif que le travail devient mono-agent.

Le pack Tricorder 0.4 propose uniquement le profil `odoo-consultant`. Les sections
historiques restent dans `roles/tricorder.md` pour les workflows existants ; ceux-ci
ne sont pas migrés automatiquement. Tricorder reste responsable de ses blocs,
permissions et réceptions. Cette adaptation du pack ne prouve pas une exécution
native dans une installation Tricorder externe.

## Apprendre pendant les releases et réutiliser après

Les contributions sourcées vivent dans `changelog/<release>/knowledge/`.
Les décisions acceptées alimentent `.odoo-agents/DECISIONS.json` et les découvertes
acceptées `.odoo-agents/LEARNINGS.json`. Une proposition n'est pas un acquis.
Le briefing les relit entre releases, avec leurs exceptions et contrôles de fraîcheur.

`odoo_work.py prepare` génère aussi un dossier distinct, consultable :

```text
<projet>/.odoo-agents/learnings/
├── index.json
└── <release>--<id>.json
```

Ces fiches sont des vues du registre : actuelles, périmées ou remplacées. Elles
ne remplacent ni les sources ni leur validation. L'export n'écrase pas les notes
personnelles et ne transfère rien entre clients. Une connaissance générale peut
ensuite rejoindre le référentiel partagé via `/odoo-improve`, avec vérification,
contre-exemple et retrait des données confidentielles. Cela améliore les méthodes
et références disponibles, sans réentraîner le modèle.

Pour reprendre un travail et actualiser les fiches :

```bash
python3 ~/.odoo19-agents/scripts/odoo_work.py prepare /projet --query "besoin métier"
# Avec un plan existant : ajouter --release <id> --task <id>
```

Le [guide mémoire](docs/KNOWLEDGE.md) décrit les contributions et remplacements ;
le [guide du harness](docs/HARNESS.md) décrit les contrôles et retours d'expérience.
Les commandes ne remplacent pas les vérifications fonctionnelles. Les gains de
qualité du nouveau profil ne sont pas établis par une campagne LLM comparative.

## Réduire les reprises et vérifier ce qui part

**Avant de coder**, l'analyste confronte les hypothèses sensibles à quelques cas
représentatifs : courant, historique et contre-exemple. Le principal fixe les
parcours et les contrôles. La QA reproduit les défauts avec le bon état, les droits
et le canal réel ; un appel interne impossible n'est pas une preuve de panne utilisateur.

**Pendant le travail**, les profils chargent les procédures selon leur mode
(tâche, release ou réception documentaire). Le [contexte ciblé](docs/CONTEXT.md)
garde les décisions et les exceptions, et indique les sections laissées de côté.
Le briefing peut le produire directement avec `--query`, sans charger d'abord
toute l'archive. Une intention tardive conserve les preuves indépendantes.
Les essais de réception montrent moins de texte chargé, avec des verdicts corrects,
mais **pas de gain de vitesse** sur les cas comparés : [mesures et limites](docs/quality-lab/profiles-2026-09-15/README.md).

**À la livraison**, le [garde du commit](docs/DELIVERY_GUARD.md) vérifie fichiers,
imports, versions, migrations et preuve du build convenu. Les états restent
explicites : prêt localement, poussé, puis déploiement vérifié après lecture de la
version installée et des effets attendus. L'outil ne déploie rien lui-même.

Le [banc de parcours](benchmarks/workflow_regressions/README.md) ajoute stock,
PDF historique, formulaire et reprise de plan aux contrôles déterministes.
La [boucle native N06/N07](docs/quality-lab/agent-workflows-2026-09-15/README.md)
conserve huit essais avant/après, avec un cas inédit : un gain sur un premier
cas ne se retrouve pas sur le suivant, et le candidat global reste expérimental.
Les outils de preuve et la contradiction d’ordre des tests sont corrigés ; aucun
gain général de vitesse ou de qualité n’est revendiqué.
Les [modèles par rôle](docs/MODELS.md) restent hérités du principal ; les candidats
plus légers sont comparés séparément et ne deviennent pas automatiquement les
modèles du quotidien.

## Les commandes, selon votre besoin

Après l’[installation](docs/INSTALL.md), ouvrez votre projet dans Claude Code ou Codex.
Indiquez la commande et décrivez le résultat souhaité :

```text
/odoo-plan Prepare une release pour ces trois demandes,
avec les decisions a prendre et les priorites.
```

| Commande | Quand l’utiliser | Ce que vous obtenez |
|---|---|---|
| **`/odoo-plan`** | Organiser plusieurs demandes | Un plan de release, les critères attendus et les dépendances. |
| **`/odoo-estimate`** | Prévoir le travail des agents | Des minutes par agent et tâche, avec fourchette et hypothèses. |
| **`/odoo-start`** | Lancer ou reprendre le plan | L’exécution des tâches prêtes et un suivi de l’avancement. |
| **`/odoo-new`** | Réaliser une évolution précise | Analyse, réalisation, contrôles ciblés et mémoire du résultat. |
| **`/odoo-express`** | Livrer une petite correction locale | Qualification courte, modification directe, test ciblé et push lorsqu'il est demandé. |
| **`/odoo-close`** | Préparer la livraison | Recette complète, documentation métier et bilan prévu/réalisé disponible. |
| **`/odoo-env`** | Déclarer ou vérifier un environnement | Des accès configurés et vérifiés, sans partager de secret dans la conversation. |
| **`/odoo-feedback "remarque"`** | Retenir une règle ou une difficulté | Une remarque conservée dans le journal du projet. |
| **`/odoo-feedback`** | Faire le point sur les enseignements | Une revue des retours d’expérience et des améliorations à éprouver. |
| **`/odoo-improve`** | Tester une amélioration des agents | Un essai, une correction et une décision d’adoption après vérification. |

Pour une question fonctionnelle, un ticket, une relecture ou un guide utilisateur,
décrivez simplement votre besoin : le rôle ou skill adapté prend le relais.

<details>
<summary><strong>Exemple métier : éviter une commande sans référence d’achat client</strong></summary>

**Scénario illustratif, non exécuté sur une base Odoo.** Un client exige que sa
référence d’achat figure sur chaque commande. Le commercial doit pouvoir préparer
son devis, mais la confirmation doit être bloquée si cette référence manque.

> `/odoo-new Pour les clients qui exigent une référence d’achat, empêche la
> confirmation d’une commande sans référence. Laisse les devis modifiables
> et les commandes déjà confirmées inchangées.`

```text
Chef de projet --> Analyste --> Developpeur --> Qualite
                                    ^             |
                                    +-- retour ---+
              Orchestrateur : suivi et livraison
```

| Intervenant | Son implication | Sa conclusion attendue |
|---|---|---|
| **Chef de projet** | Précise quels clients sont concernés et si une exception est permise. | La règle métier est décidée : blocage à la confirmation, aucun changement rétroactif. |
| **Analyste** | Vérifie le standard, les configurations existantes et le cas d’une confirmation de plusieurs commandes. | Périmètre et critères validés ; pour cet exemple, la voie retenue est un module spécifique. |
| **Développeur** | Ajoute l’indication sur le client, le contrôle à la confirmation, un message compréhensible et les tests associés. | La réalisation est prête pour une vérification indépendante. |
| **Responsable qualité** | Contrôle les clients concernés ou non, la référence présente ou absente, la confirmation groupée et les commandes déjà confirmées. | Accepté si tous les critères passent ; sinon, retour au développeur avec le défaut reproduit. |
| **Orchestrateur** | Suit les étapes, conserve les décisions et les preuves, puis prépare la recette complète à la clôture. | Tâche vérifiée dans la release ; livraison après recette complète, avec documentation et bilan du temps. |

**Résultat visé :** le commercial sait quoi compléter avant de confirmer,
et les commandes existantes restent inchangées. Studio et Support ne sont
pas mobilisés dans ce scénario ; ils interviennent lorsque le besoin le justifie.

</details>

## Ce que vous gardez d’une intervention à l’autre

**Les règles client et décisions**, pour éviter de repartir de zéro.
**Les preuves de vérification**, pour préparer vos livraisons.
**Les temps prévus et mesurés**, pour affiner vos estimations et appliquer vos
propres barèmes. Guides utilisateur et communications client sont disponibles sur demande.

Un relevé incomplet conserve son sous-total connu, sans transformer les périodes
manquantes en zéro. Avant une nouvelle clôture, les chronomètres doivent être
terminés ou déclarés interrompus avec une raison ; aucune durée passée n'est
reconstituée automatiquement. Voir le [suivi des temps](docs/EFFORT.md).

**Vous gardez le contrôle.** Les décisions métier vous appartiennent. Toute
écriture en production requiert votre accord explicite ; la clôture d’une
release ne déclenche pas son déploiement.

---

[Documentation](docs/README.md) · [Installation](docs/INSTALL.md) · [Estimation et suivi](docs/EFFORT.md) ·
[Qualité et amélioration](docs/quality-lab/README.md) · [Guide technique](docs/ARCHITECTURE.md)

Correctif local du 17.09 : [réception après remplacement explicite des décisions](docs/quality-lab/knowledge-supersession-2026-09-17/README.md), historique conservé et sources courantes contrôlées.

## Travail, mémoire et retours

[Guide du harness](docs/HARNESS.md) : `odoo_work.py prepare/start/receive`, briefing
ciblé par défaut (`--full-memory` pour le détail), décisions acceptées disponibles
entre releases, publication de petits ajouts mémoire et collecte automatique des
retours. Le tri ne modifie aucune règle générale sans évaluation. Tricorder propose
le parcours demande → travail → réception et garde les instruments dans Détails.

## Pilotage — octobre 2026

[Contrats de pilotage](docs/PILOTAGE.md) : résultats métier, moyens de recette,
publication avec réserves, apprentissages projet et collecte durable des mesures.
[Bilan et limites de la release](docs/quality-lab/pilotage-2026-10-07/README.md).

## Pack Tricorder

`tricorder-pack.json` expose un consultant polyvalent au moteur générique (version 0.4.0).
Sa source canonique est `roles/tricorder.md` : un contrat partagé et une section
consultant, avec les sections historiques conservées pour compatibilité.
Le chargeur fige uniquement le contrat et la section du profil choisi.
Les blocs fixent les entrées, sorties et décisions ; le profil précise la méthode.
Les questions imprévues sont conservées par le moteur de conversation. Le support
distingue urgence et risque : un test rouge est exigé pour un bug, pas pour une
question d’usage. Ces ajustements de contrat ne constituent pas une mesure de
qualité comportementale des modèles.
Ce profil remet ses résultats au moteur Tricorder ; il ne crée pas de
flows historiques. Code isolé, tests sur copie locale, accords de publication et
suivi GitHub → Odoo.sh sont séparés. Les anciennes commandes restent utilisables
pour les projets existants ; elles ne sont pas importées dans le pack.
La qualification métier et les connexions réelles restent propres à la série,
au projet et aux comptes configurés. Un résultat local ne qualifie pas Odoo.sh.
