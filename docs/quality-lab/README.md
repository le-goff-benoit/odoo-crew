# Qualité et amélioration des agents

[Présentation du dispositif](../../README.md) · [Améliorations livrées](../IMPROVEMENTS.md)

**Un point d’entrée pour comprendre ce qui a été testé, ce qui a changé et ce qui reste à améliorer.**
Nous ajustons les consignes et les outils à partir des résultats observés.
Il s’agit d’essais et de retours d’expérience ; les modèles ne sont pas réentraînés.

## Où aller ?

| Votre objectif | Ouvrez… |
|---|---|
| Comprendre les résultats et leurs limites | Les campagnes classées par sujet ci-dessous |
| Vérifier les outils après un changement | [Les tests automatiques](../../tests/README.md), rangés en pilotage, outillage et laboratoire |
| Choisir ou ajouter un cas à soumettre aux agents | [Le catalogue des scénarios](../../benchmarks/README.md) |
| Exécuter une campagne | [Le mode opératoire](OPERATIONS.md) |
| Voir quelles améliorations sont installées | [Le suivi des améliorations](../IMPROVEMENTS.md) |

## Résultats par sujet

Commencez par le bilan le plus récent du sujet qui vous intéresse.
Chaque rapport précise son périmètre : une réussite sur un cas n’est pas une garantie générale.

| Sujet | Bilan à lire | Ce qu’il permet de savoir |
|---|---|---|
| **Email de clôture — retiré** | [Retrait et compatibilité](email-removal-2026-09-11/README.md) | Fonctionnalité abandonnée ; anciennes commandes inertes et données conservées. |
| **Temps prévu et réalisé** | [Estimation par agent](effort-2026-09-09/README.md) | Le suivi est livré ; la précision des prévisions reste à calibrer. |
| **Délégation et langage pour le chef de projet** | [Comparaison solo / sous-agents](delegation-comparison-2026-09-09/README.md) | La délégation reste un choix au cas par cas ; le langage attendu est intégré aux consignes. |
| **Reprise du travail** | [Reprise ordonnée](ordered-recovery-2026-09-09/README.md) | Les passations et reprises sont éprouvées sur des cas délimités. |
| **Conflits dans la mémoire du projet** | [Reprise après réception](recovery-2026-09-09/README.md) | Les corrections adoptées et les conditions de reprise. |
| **Respect de la demande** | [Fidélité de bout en bout](fidelity-2026-09-09/README.md) | La réception compare demande, preuves et mémoire proposée. |
| **Droits, restauration et navigateur** | [Qualification technique](qualification-2026-09-09/README.md) | Les composants contrôlés, distincts des parcours métier complets. |
| **Couverture des critères** | [Réception structurée](coverage-2026-09-09/README.md) | Une couverture manquante bloque la réception lorsque le contrat est activé. |
| **Parcours complets des agents** | [Campagne native](native-2026-09-09/README.md) | Les évolutions éprouvées avec les outils et une copie Odoo synthétique. |

<details>
<summary>Premiers essais et étapes intermédiaires</summary>

- [Pilote du 8 septembre](pilot-2026-09-08/README.md) : premières erreurs observées, sans amélioration encore démontrée.
- [Premières corrections](experiment-2026-09-08/README.md) : corrections adoptées et variantes restées expérimentales.
- [Première délégation réelle](delegation-2026-09-09/README.md) : sous-agents observés et défaut de consolidation relevé.
- [Consolidation et messages RPC](consolidation-2026-09-09/README.md) : correction du banc et variantes de consignes retirées.

</details>

## Proposer une amélioration

Décrivez le problème et le résultat souhaité, par exemple :

> `/odoo-improve Les questions de l’analyste sont trop techniques pour le chef de projet. Je veux pouvoir décider sans devoir interpréter les noms d’outils.`

Le parcours est **observer → reproduire → corriger → vérifier → adopter**.
Un rapport doit distinguer une amélioration installée, une expérience et un
point encore non mesuré. Les échecs et réserves restent consultables.

## Ranger les prochaines campagnes

Une campagne = un dossier `sujet-AAAA-MM-JJ/`, ajouté au tableau ci-dessus.
Utilisez cette structure pour les nouvelles campagnes :

```text
sujet-AAAA-MM-JJ/
├── README.md       Résultat, décision, bénéfice et limites
├── protocol.json   Ce qui sera testé et les critères retenus
├── JOURNAL.md      Changements et enseignements
└── evidence/       Preuves détaillées, accessibles depuis le bilan
```

Les cas réutilisables vont dans `benchmarks/`, les tests automatiques dans
`tests/`, les résultats dans ce dossier. Les campagnes existantes conservent
leurs fichiers d’origine : certains chemins et empreintes font partie des preuves.
Il n’est pas nécessaire de parcourir ces archives pour utiliser les agents.
