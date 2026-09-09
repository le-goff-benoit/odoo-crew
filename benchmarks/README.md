# Scénarios pour améliorer les agents

[Accueil qualité](../docs/quality-lab/README.md) · [Résultats des campagnes](../docs/quality-lab/README.md#résultats-par-sujet)

Ce dossier contient les **cas à rejouer et leurs critères de réussite**.
Les tests automatiques sont dans [`tests/`](../tests/README.md) ; les résultats
obtenus sont dans [`docs/quality-lab/`](../docs/quality-lab/README.md).

## Choisir selon ce que vous voulez vérifier

| Objectif | Cas et ressources |
|---|---|
| Qualité d’une analyse et respect des décisions | [Dossiers initiaux](cases/), [dossiers approfondis](cases-v2/) |
| Développement et règles métier | [Contrats de développement](cases-dev/), [location/livraison](odoo/), [notes de frais](odoo-expense/) |
| Parcours complet avec les vrais outils des agents | [Cas natifs et correcteurs](native/) |
| Fidélité de la demande jusqu’à la mémoire du projet | [Fidélité](fidelity/README.md) |
| Reprise après interruption ou conflit | [Reprise](recovery/README.md), [reprise ordonnée](ordered_recovery/) |
| Intérêt réel de la délégation | [Comparaison solo / sous-agents](delegation_comparison/) |
| Droits, restauration, versions et navigateur Odoo | [Qualification technique](qualification/) |

Les [configurations](configs/), [variantes de consignes](variants/) et
[grilles du correcteur](judge/) servent à préparer les comparaisons.
Un dossier de cas n’est pas nécessairement un parcours exécutable : les
statuts et limites figurent dans son contrat ou son rapport de campagne.

## Lancer un essai

Pour une nouvelle amélioration, utilisez `/odoo-improve` avec le défaut observé
et le résultat attendu. Il organise la reproduction, la correction et sa vérification.

Pour intervenir directement sur le banc :

- [Mode opératoire](../docs/quality-lab/OPERATIONS.md) : choisir le type d’essai et ses commandes.
- [Guide du pilote sur dossier](PILOTE.md) : configuration, exécution et correction des réponses.
- [Tests automatiques](../tests/README.md) : vérifications locales sans appel à un modèle.

Les campagnes avec agents et les essais Odoo sont lancés explicitement, dans
un environnement équipé. Les résultats locaux vont dans un dossier de travail
hors du dépôt ; seules les preuves vérifiées et sans données client sont publiées.

## Ranger un nouveau cas

Ajoutez-le dans la famille correspondante ci-dessus, avec la demande synthétique
et ses critères attendus. Gardez le correcteur séparé du dossier vu par l’agent.
Le rapport de l’exécution rejoint une campagne datée dans `docs/quality-lab/`.
Les identifiants historiques restent stables pour permettre les comparaisons.
