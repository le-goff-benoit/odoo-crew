# Banc Odoo — 20260908-214544-91d4d786

État : **executed**

Exécution et qualité sont distinctes. Une grille satisfaite ne vaut pas validation générale ; une revue indépendante reste nécessaire.

| Cas | Outil | Exécution | Secondes | Conformité à la grille |
|---|---|---|---:|---|
| B10-codex-reference-r1 | codex | completed | 79.1 | accepted |
| B10-codex-fidelity-r1 | codex | completed | 77.1 | accepted |
| B10-codex-compact-r1 | codex | completed | 75.9 | accepted |
| B10-claude-reference-r1 | claude | completed | 131.8 | rejected |
| B10-claude-fidelity-r1 | claude | completed | 100.6 | accepted |
| B10-claude-compact-r1 | claude | completed | 94.1 | needs_review |
| B10-codex-compact-r2 | codex | completed | 91.2 | accepted |
| B10-codex-fidelity-r2 | codex | completed | 76.1 | accepted |
| B10-codex-reference-r2 | codex | completed | 73.1 | accepted |
| B10-claude-compact-r2 | claude | completed | 98.6 | needs_review |
| B10-claude-fidelity-r2 | claude | completed | 136.0 | needs_review |
| B10-claude-reference-r2 | claude | completed | 116.3 | rejected |
| B11-codex-reference-r1 | codex | completed | 123.8 | accepted |
| B11-codex-fidelity-r1 | codex | completed | 123.4 | needs_review |
| B11-codex-compact-r1 | codex | completed | 90.3 | accepted |
| B11-claude-reference-r1 | claude | completed | 140.0 | rejected |
| B11-claude-fidelity-r1 | claude | completed | 117.1 | needs_review |
| B11-claude-compact-r1 | claude | completed | 79.0 | needs_review |
| B11-codex-compact-r2 | codex | completed | 88.3 | accepted |
| B11-codex-fidelity-r2 | codex | completed | 117.3 | accepted |
| B11-codex-reference-r2 | codex | completed | 115.9 | needs_review |
| B11-claude-compact-r2 | claude | completed | 87.1 | accepted |
| B11-claude-fidelity-r2 | claude | completed | 142.5 | needs_review |
| B11-claude-reference-r2 | claude | completed | 146.7 | rejected |

## Configurations et mesure

| Essai | Modèle demandé | Effort demandé | Modèle observé |
|---|---|---|---|
| B10-codex-reference-r1 | gpt-6-astra | high | non retourné |
| B10-codex-fidelity-r1 | gpt-6-astra | high | non retourné |
| B10-codex-compact-r1 | gpt-6-astra | high | non retourné |
| B10-claude-reference-r1 | opus | medium | claude-opus-5 |
| B10-claude-fidelity-r1 | opus | medium | claude-opus-5 |
| B10-claude-compact-r1 | opus | medium | claude-opus-5 |
| B10-codex-compact-r2 | gpt-6-astra | high | non retourné |
| B10-codex-fidelity-r2 | gpt-6-astra | high | non retourné |
| B10-codex-reference-r2 | gpt-6-astra | high | non retourné |
| B10-claude-compact-r2 | opus | medium | claude-opus-5 |
| B10-claude-fidelity-r2 | opus | medium | claude-opus-5 |
| B10-claude-reference-r2 | opus | medium | claude-opus-5 |
| B11-codex-reference-r1 | gpt-6-astra | high | non retourné |
| B11-codex-fidelity-r1 | gpt-6-astra | high | non retourné |
| B11-codex-compact-r1 | gpt-6-astra | high | non retourné |
| B11-claude-reference-r1 | opus | medium | claude-opus-5 |
| B11-claude-fidelity-r1 | opus | medium | claude-opus-5 |
| B11-claude-compact-r1 | opus | medium | claude-opus-5 |
| B11-codex-compact-r2 | gpt-6-astra | high | non retourné |
| B11-codex-fidelity-r2 | gpt-6-astra | high | non retourné |
| B11-codex-reference-r2 | gpt-6-astra | high | non retourné |
| B11-claude-compact-r2 | opus | medium | claude-opus-5 |
| B11-claude-fidelity-r2 | opus | medium | claude-opus-5 |
| B11-claude-reference-r2 | opus | medium | claude-opus-5 |

## Évaluation par dimension

Les fractions comptent les critères satisfaits ; elles ne constituent pas une moyenne de qualité.

| Essai | Réponse | Développement | QA | Connaissance client |
|---|---|---|---|---|
| B10-codex-reference-r1 | 2/2 | non mesuré | 2/2 | 4/4 |
| B10-codex-fidelity-r1 | 2/2 | non mesuré | 2/2 | 4/4 |
| B10-codex-compact-r1 | 2/2 | non mesuré | 2/2 | 4/4 |
| B10-claude-reference-r1 | 1/2 | non mesuré | 1/2 | 3/4 |
| B10-claude-fidelity-r1 | 2/2 | non mesuré | 2/2 | 4/4 |
| B10-claude-compact-r1 | 2/2 | non mesuré | 2/2 | 3/4 |
| B10-codex-compact-r2 | 2/2 | non mesuré | 2/2 | 4/4 |
| B10-codex-fidelity-r2 | 2/2 | non mesuré | 2/2 | 4/4 |
| B10-codex-reference-r2 | 2/2 | non mesuré | 2/2 | 4/4 |
| B10-claude-compact-r2 | 1/2 | non mesuré | 2/2 | 4/4 |
| B10-claude-fidelity-r2 | 1/2 | non mesuré | 2/2 | 4/4 |
| B10-claude-reference-r2 | 1/2 | non mesuré | 2/2 | 3/4 |
| B11-codex-reference-r1 | 1/1 | non mesuré | 2/2 | 4/4 |
| B11-codex-fidelity-r1 | 1/1 | non mesuré | 1/2 | 4/4 |
| B11-codex-compact-r1 | 1/1 | non mesuré | 2/2 | 4/4 |
| B11-claude-reference-r1 | 1/1 | non mesuré | 0/2 | 1/4 |
| B11-claude-fidelity-r1 | 1/1 | non mesuré | 1/2 | 4/4 |
| B11-claude-compact-r1 | 1/1 | non mesuré | 2/2 | 3/4 |
| B11-codex-compact-r2 | 1/1 | non mesuré | 2/2 | 4/4 |
| B11-codex-fidelity-r2 | 1/1 | non mesuré | 2/2 | 4/4 |
| B11-codex-reference-r2 | 1/1 | non mesuré | 1/2 | 4/4 |
| B11-claude-compact-r2 | 1/1 | non mesuré | 2/2 | 4/4 |
| B11-claude-fidelity-r2 | 1/1 | non mesuré | 1/2 | 4/4 |
| B11-claude-reference-r2 | 1/1 | non mesuré | 1/2 | 1/4 |

## Réserves hors grille


## Limites

- Pilote sans outils : aucune exécution Odoo ni validation du développement.
- Consignes du rôle injectées explicitement : routage natif non évalué.
- Comparaisons entre outils non causales ; comparer les variantes au sein du même réglage.
- Effort effectif inconnu si le fournisseur ne le retourne pas.
