# Agents Odoo — Claude Code & Codex

**Des agents qui prennent le temps de comprendre le métier, réalisent les changements et vérifient le résultat.**

Ce projet donne à Claude Code et Codex une méthode de travail commune pour vos
projets Odoo : analyser la demande, choisir une solution adaptée, la réaliser,
la tester et conserver les décisions utiles pour la suite.

Il accompagne les questions fonctionnelles, le support, les développements et
les configurations Studio, jusqu’à la préparation d’une livraison.

[Installer ou mettre à jour](INSTALL.md) · [Voir les améliorations éprouvées](docs/IMPROVEMENTS.md)

## Ce qui fait la différence

### Comprendre le besoin avant de développer

L’analyste confronte la demande au fonctionnement réel du client et aux
possibilités d’Odoo. Il vérifie si le standard répond déjà au besoin, compare
configuration, Studio et développement, et relève les décisions manquantes.
L’objectif : une solution utile au métier et dont l’entretien reste maîtrisé.

### Garder le contexte du client d’une demande à l’autre

Les règles métier, les décisions prises et les pièges connus sont conservés dans
le projet. Une nouvelle intervention retrouve ce contexte, même dans une nouvelle
conversation. Les décisions remplacées restent identifiables pour éviter de
réappliquer une ancienne règle.

### Tester ce qui compte pour le client

Les contrôles s’appuient sur des résultats attendus concrets : un montant juste,
un document validé qui reste inchangé, une règle appliquée au bon utilisateur.
Les changements sensibles — droits, comptabilité, facturation ou données
existantes — demandent des vérifications renforcées sur une copie client.
Les tests exécutés et leurs limites accompagnent le verdict.

### Avancer avec un suivi clair

Le travail est réparti entre analyse, réalisation et contrôle. Vous pouvez suivre
l’étape en cours, ce qui est terminé et ce qui attend une décision.
Pour plusieurs demandes, un plan organise les priorités et les dépendances,
puis permet de reprendre le travail. Une validation doit être réexaminée si les
éléments sur lesquels elle repose ont changé.

### Retrouver la même méthode dans Claude Code et Codex

Les deux outils utilisent les mêmes définitions de rôles et les mêmes règles de
travail. Le dispositif tient compte de la version du projet : Odoo 17, 18, 19 et
les versions SaaS référencées. Les différences entre versions sont documentées
pour guider l’analyse et le développement.

### Améliorer les agents à partir de leurs résultats

Un banc d’essai permet de soumettre des demandes Odoo aux agents, d’observer leurs
erreurs et de tester des corrections de leurs instructions. Une amélioration
est adoptée après vérification. Les cas et les résultats sont disponibles dans
ce dépôt pour adapter les prochaines expériences à vos besoins.

## Au quotidien

Après [installation](INSTALL.md), ouvrez une conversation dans votre projet et
décrivez votre demande. Pour une évolution, utilisez par exemple :

```text
/odoo-new Lors de la validation d’une commande, prévenir le commercial
si la référence client est absente. Une commande déjà validée doit rester inchangée.
```

Le parcours habituel est :

**Comprendre → réaliser → vérifier → conserver les décisions et les résultats.**

Les étapes s’enchaînent sans redemander votre accord à chaque passage.
L’agent revient vers vous lorsqu’une décision métier manque ou qu’un blocage
empêche de poursuivre correctement.

| Votre besoin | Point d’entrée |
|---|---|
| Développer ou configurer une évolution | `/odoo-new` |
| Organiser plusieurs demandes avant de commencer | `/odoo-plan` |
| Estimer les minutes d'exécution par agent et lot de travail | `/odoo-estimate` |
| Lancer ou reprendre les tâches du plan | `/odoo-start` |
| Vérifier l’ensemble et préparer la livraison | `/odoo-close` |
| Signaler une règle client ou une leçon à retenir | `/odoo-feedback "votre remarque"` |
| Tester et améliorer les agents et leurs instructions | `/odoo-improve` |
| Déclarer les accès à un environnement | `/odoo-env` |

Vous pouvez aussi poser une question fonctionnelle, confier un ticket de support
ou demander une relecture en langage naturel. Le rôle adapté est alors mobilisé.

L'[estimation des agents](docs/EFFORT.md) donne une fourchette par tâche et rôle,
avec hypothèses et niveau de confiance. À la clôture, un bilan compare prévision
et durées mesurées, reprend les jetons et les coûts IA disponibles et s'exporte
en CSV. Les prévisions initiales restent conservées ; vous appliquez vos propres
barèmes. Les premières estimations reposent sur un jugement explicite, à calibrer
avec les releases exécutées.

## Des contrôles adaptés au moment du projet

Chaque demande reçoit une vérification ciblée. À la clôture d’une **release**
(un ensemble de changements à livrer), une vérification complète contrôle leur
bon fonctionnement ensemble. Les changements sensibles sont contrôlés dès leur
réalisation.

La livraison rassemble les demandes, les décisions, les résultats des tests et
une documentation métier. Un guide Word/PDF, des captures ou une communication
client peuvent être demandés selon le besoin. La clôture ne déploie pas
automatiquement les changements et n’envoie pas de message au client.

Les essais se font normalement sur une copie locale du client. La production
reste en lecture seule par défaut ; toute écriture nécessite une confirmation
explicite pour l’opération concernée.

## Une qualité vérifiée, avec des limites visibles

La campagne du 9 septembre 2026 a conduit à des modifications effectives des
agents et des outils : tests SQL, précision des règles métier, transmission du
contexte et reprise des tâches notamment.

- **20 parcours terminés avec leurs contrôles métier réussis**, sur Odoo 19.
- **124 tests d’outillage réussis** sous Python 3.10 et 3.12 pour la campagne initiale.
- Les incidents d’essai et les réserves de qualité sont conservés dans le rapport.

Ces résultats portent sur des cas synthétiques : ils ne garantissent pas toutes
les situations client. Ils ne démontrent ni une supériorité générale d’un modèle,
ni un gain global de vitesse. Les prochaines améliorations doivent à leur tour
être mises à l’épreuve.

[Lire les résultats et leurs limites](docs/quality-lab/native-2026-09-09/README.md)

Un [essai complémentaire de délégation et de reprise](docs/quality-lab/delegation-2026-09-09/README.md)
distingue les agents réellement démarrés des étapes simplement réservées et
précise les prochaines dimensions à tester. Le mode de délégation du banc
reste expérimental.

La [poursuite sur la consolidation et le RPC](docs/quality-lab/consolidation-2026-09-09/README.md)
reproduit le faux succès de QA et ajoute au banc la vérification du message
réellement retourné par Odoo. Les deux variantes de consigne restent non adoptées.

La [réception structurée des critères](docs/quality-lab/coverage-2026-09-09/README.md)
ajoute ensuite un garde optionnel au flow : une couverture absente ou partielle
ne permet plus `pass` lorsqu'un contrat est lié. Les essais montrent le blocage
attendu et l'acceptation d'un cas complet. La [qualification autonome](docs/quality-lab/qualification-2026-09-09/README.md)
ajoute un rendu QA lié à la réception, des droits testés par ORM/RPC, une vraie
restauration SQL + filestore et un parcours Chrome avec contrôle serveur. Elle
distingue ces témoins des chaînes natives et garde les limites et incidents visibles.

La [campagne de fidélité](docs/quality-lab/fidelity-2026-09-09/README.md) confronte
ensuite la demande originale, les critères, les preuves et la mémoire. Elle
introduit une réception documentaire en contexte neuf et un
[garde de publication exacte](docs/TASK_RECEPTION.md).
Les examens sur pièces, les parcours complets et les interruptions fournisseur
y sont évalués séparément. La [campagne de reprise](docs/quality-lab/recovery-2026-09-09/README.md)
éprouve ensuite les conflits mémoire, les publications interrompues et les plans,
avec des contextes Codex distincts sur des tâches documentaires synthétiques.
La [qualification ordonnée](docs/quality-lab/ordered-recovery-2026-09-09/README.md)
vérifie ensuite un vrai reçu A antérieur à B, le positif sans réception superflue
et une tâche Odoo 19.0 sur copie synthétique restaurée. Les traces natives et
leurs limites de visibilité sont conservées ; la calibration du banc entre en CI.

La [comparaison solo/délégation](docs/quality-lab/delegation-comparison-2026-09-09/README.md)
reçoit six livrables et confirme deux correctifs avec un oracle indépendant. Un
seul diagnostic utilise un sous-agent : il est plus lent et consomme davantage,
sans gain de note. La délégation reste un choix au cas par cas. Une consigne
commune rend explicite le langage attendu par un chef de projet : résultat,
impact, prochaine action et décisions compréhensibles. Ses trois essais de
communication passent sans régression, sans gain de qualité démontré.

## Pour aller plus loin

| Vous souhaitez… | Documentation |
|---|---|
| Installer le dispositif ou le mettre à jour | [Installation](INSTALL.md) |
| Comprendre les rôles, le suivi et les mécanismes techniques | [Guide technique](docs/ARCHITECTURE.md) |
| Organiser les demandes et reprendre une release | [Plans et reprise](docs/RELEASE_PLAN.md) |
| Structurer la connaissance métier du client | [Contexte, décisions et scénarios](docs/CLIENT_KNOWLEDGE.md) |
| Adapter les essais et suivre leur avancement | [Mode opératoire du laboratoire](docs/quality-lab/OPERATIONS.md) |
| Relier les propositions aux changements et à leurs preuves | [Améliorations suivies](docs/IMPROVEMENTS.md) |

Les rôles et instructions partagés évoluent dans ce dépôt, puis sont installés
pour les deux outils. Après une mise à jour, ouvrez une nouvelle conversation
pour charger les nouveaux profils.
