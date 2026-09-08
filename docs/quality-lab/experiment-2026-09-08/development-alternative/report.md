# Banc Odoo — 20260908-215142-4142810f

État : **executed**

Exécution et qualité sont distinctes. Une grille satisfaite ne vaut pas validation générale ; une revue indépendante reste nécessaire.

| Cas | Outil | Exécution | Secondes | Conformité à la grille |
|---|---|---|---:|---|
| B12-codex | codex | completed | 63.8 | accepted |
| B12-claude | claude | completed | 206.0 | rejected |

## Configurations et mesure

| Essai | Modèle demandé | Effort demandé | Modèle observé |
|---|---|---|---|
| B12-codex | gpt-6-astra | medium | non retourné |
| B12-claude | opus | high | claude-opus-5 |

## Évaluation par dimension

Les fractions comptent les critères satisfaits ; elles ne constituent pas une moyenne de qualité.

| Essai | Réponse | Développement | QA | Connaissance client |
|---|---|---|---|---|
| B12-codex | non mesuré | 1/1 | non mesuré | non mesuré |
| B12-claude | non mesuré | 0/1 | non mesuré | non mesuré |

## Réserves hors grille


## Limites

- Pilote sans outils : aucune exécution Odoo ni validation du développement.
- Consignes du rôle injectées explicitement : routage natif non évalué.
- Comparaisons entre outils non causales ; comparer les variantes au sein du même réglage.
- Effort effectif inconnu si le fournisseur ne le retourne pas.
