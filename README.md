![Votre équipe d’agents Odoo, réunie autour de votre projet](docs/assets/agents-odoo-banner.png)

# Votre équipe d’agents pour les projets Odoo

**Du besoin métier à la livraison, avancez avec des spécialistes à vos côtés.**

Consultant fonctionnel ou chef de projet Odoo ? Confiez vos demandes aux agents
pour cadrer, réaliser et vérifier le travail. Vous gardez la main sur les décisions
métier, avec un suivi des résultats et des prochaines étapes.

Disponible dans **Claude Code et Codex**, avec une méthode commune adaptée à la
version Odoo de votre projet.

[Commencer](docs/INSTALL.md) · [Qualité et résultats des essais](docs/quality-lab/README.md)

## À chacun son rôle, à vous le pilotage

| Votre spécialiste | Ce qu’il vous apporte |
|---|---|
| **Analyste fonctionnel** | Clarifie le besoin, vérifie le standard et compare configuration, Studio et développement. |
| **Développeur** | Réalise les évolutions spécifiques et leurs tests, selon les règles du projet. |
| **Expert Studio** | Configure les champs, écrans et automatisations, avec un suivi des changements. |
| **Responsable qualité** | Vérifie les résultats attendus et identifie ce qui reste à corriger. |
| **Support** | Recherche la cause d’un problème et propose un contournement ou la suite à donner. |

L’**agent principal orchestre le travail** : il mobilise les rôles nécessaires,
regroupe leurs résultats et vous sollicite pour les décisions manquantes.
Il peut déléguer des tâches indépendantes à des sous-agents, lorsque l’outil le permet.

## Comment les agents travaillent ensemble

**Une évolution : comprendre avant de réaliser.**

```text
Votre demande --> Analyste
                     |
                     +--> Standard suffisant --> Recommandation
                     |
                     +--> Developpeur ou Studio --> Qualite --> Resultat verifie
                                   ^                   |
                                   +--- corrections ---+
```

Chaque tâche conserve ses décisions et ses résultats dans la mémoire du projet.
Un blocage ou un contrôle qui reste en échec vous est signalé.

**La mémoire de release est partagée pendant le travail.** Une découverte ou une
question est publiée dès qu'elle peut aider une autre tâche. Les passations reçues
alimentent immédiatement les suivantes ; une nouvelle décision désigne les tâches
affectées, et leurs anciennes réceptions deviennent périmées. Documents DOCX,
XLSX et PDF gardent leurs originaux et repères ; les sources Odoo sont indexées
par série/révision, avec le custom séparé. La clôture consolide ces acquis.
[Fonctionnement et commandes](docs/KNOWLEDGE.md) ·
[Banc et limites](docs/quality-lab/knowledge-2026-09-15/README.md).

**Une investigation longue reste pilotable.** Les agents font un point sur les
acquis prouvés, la question restante et le prochain contrôle utile, avec sa durée
indicative. Le budget déclenche une revue de l'approche, pas un arrêt automatique.
L'analyste passe la main lorsque le besoin est suffisamment cadré ; un retour
partiel ne devient pas une tâche prête à réceptionner. Ces consignes sont communes
à Claude et Codex ; elles ne constituent pas un superviseur automatique.
[Essais et limites](docs/quality-lab/progress-2026-09-11/README.md).

**Un correctif express : modifier, vérifier et livrer sans coordination superflue.**

```text
/odoo-express --> Qualification courte --> Modification locale --> Test cible
                         |                                         |
                         +-- perimetre elargi --> /odoo-new        +--> Livraison demandee
```

Ce parcours s'applique aux retouches précises et réversibles dans une zone déjà
connue, par exemple la mise en page d'un rapport sans changement de ses montants.
L'agent principal réalise toutes les étapes. Le lint, la mise à jour du module et
le test ciblé restent obligatoires. Les ajustements liés partagent la même entrée
de changelog express.

**Une release : organiser plusieurs demandes jusqu’à la livraison.**

```text
/odoo-plan --> /odoo-estimate --> /odoo-start
  Cadrer         Prevoir          Executer les taches
                                       |
                                       v
                                  /odoo-close
                            Recette complete + documentation
                            + bilan du temps prevu / realise
```

L’orchestrateur suit les dépendances. Les contrôles ciblés accompagnent chaque
tâche ; la recette complète vérifie l’ensemble à la clôture.

**Intentions → Plan → Exécution.** Le principal conserve les demandes originales,
construit le plan et prescrit critères, cas et commandes de test avant délégation.
Une précision nouvelle révise les tâches concernées et conserve les réceptions
indépendantes. Le suivi d’orchestration indique les tâches autorisées et les attentes.
Le garde Stop relance un principal qui s’arrête alors qu’une action autorisée est
prête ; une fin d’enfant reste un résultat à examiner.

La QA peut lire un candidat figé pendant un développement indépendant, avec
worktree et ressources distincts ; la recette du résultat intégré reste requise.
Le principal conserve son modèle. Les [candidats par rôle](docs/quality-lab/models-2026-09-15/README.md)
restent expérimentaux. Voir le [guide d’exécution](docs/RELEASE_EXECUTION.md) et
les [essais natifs de continuation](docs/quality-lab/continuation-2026-09-15/README.md).

**Un ticket : diagnostiquer, puis orienter la suite.**

```text
Votre ticket --> Support --> Diagnostic
                                |
                                +--> Usage / configuration --> Explication
                                +--> Bug prouve -------------> /odoo-new
                                +--> Nouveau besoin ---------> Analyste
                                +--> Donnees a reparer ------> Essai sur copie
```

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
compare les agents avant/après correction, avec un cas inédit et des preuves liées
au code final ; une réponse terminée ne vaut pas réception du travail.
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
