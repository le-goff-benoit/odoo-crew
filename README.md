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

**Un ticket : diagnostiquer, puis orienter la suite.**

```text
Votre ticket --> Support --> Diagnostic
                                |
                                +--> Usage / configuration --> Explication
                                +--> Bug prouve -------------> /odoo-new
                                +--> Nouveau besoin ---------> Analyste
                                +--> Donnees a reparer ------> Essai sur copie
```

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
