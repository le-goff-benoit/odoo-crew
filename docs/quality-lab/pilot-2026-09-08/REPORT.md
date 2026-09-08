# Banc Odoo — 20260908-212038-8db9f91f

État : **executed**

Exécution et qualité sont distinctes. Une grille satisfaite ne vaut pas validation générale ; une revue indépendante reste nécessaire.

| Cas | Outil | Exécution | Secondes | Conformité à la grille |
|---|---|---|---:|---|
| B03 | codex | completed | 78.7 | accepted |
| B03 | claude | completed | 111.2 | accepted |
| B06 | codex | completed | 36.6 | accepted |
| B06 | claude | completed | 50.3 | needs_review |
| B10 | codex | completed | 64.6 | accepted |
| B10 | claude | completed | 169.6 | rejected |

## Configurations et mesure

| Essai | Modèle demandé | Effort demandé | Modèle observé |
|---|---|---|---|
| B03-codex | gpt-6-astra | high | non retourné |
| B03-claude | opus | medium | claude-opus-5 |
| B06-codex | gpt-6-astra | high | non retourné |
| B06-claude | opus | medium | claude-opus-5 |
| B10-codex | gpt-6-astra | high | non retourné |
| B10-claude | opus | medium | claude-opus-5 |

## Évaluation par dimension

Les fractions comptent les critères satisfaits ; elles ne constituent pas une moyenne de qualité.

| Essai | Réponse | Développement | QA | Connaissance client |
|---|---|---|---|---|
| B03-codex | 2/2 | non mesuré | 1/1 | 3/3 |
| B03-claude | 2/2 | non mesuré | 1/1 | 3/3 |
| B06-codex | 1/1 | non mesuré | 4/4 | 1/1 |
| B06-claude | 1/1 | non mesuré | 3/4 | 1/1 |
| B10-codex | 1/1 | non mesuré | 2/2 | 3/3 |
| B10-claude | 1/1 | non mesuré | 2/2 | 2/3 |

## Réserves hors grille

- **B03-claude** : §6 retient par défaut l’approbation des devis existants alors que cette décision manque ; le libellé hypothèse ne suffit pas à autoriser sa mise en œuvre.
- **B03-claude** : §3 recommande et chiffre un module avant vérification du standard ; plusieurs affirmations techniques sont non vérifiées dans ce mode.
- **B03-claude** : La grille initiale ne discrimine pas suffisamment ces risques : un accepted mesure son respect, pas une validation générale de la réponse.
- **B06-claude** : M2 assimile admin au contournement systématique des règles sans connaître le compte, ses groupes ni son mode superutilisateur dans ce dossier.
- **B06-claude** : B2 écrit « comme celle-ci est passée » à propos d’une régression malgré un verdict initial distinguant risque et preuve.
- **B06-claude** : Le gain de coût du correctif présenté comme un ordre de grandeur n’est étayé par aucune mesure.
- **B10-claude** : Le scénario supplémentaire 16→14→15 est décidé sans arbitrage : H5 compare au taux approuvé, alors que la référence de comparaison n’est pas précisée dans le dossier.
- **B10-claude** : Point positif : le cas non-partenaire approuvé à 16 puis ramené à 14 discrimine effectivement une baisse encore au-dessus du seuil.
- **B10-claude** : Les spécifications de repli sur le client principal, de paramètres modifiables et de reprise sont ajoutées sans décision client.

## Limites

- Pilote sans outils : aucune exécution Odoo ni validation du développement.
- Consignes du rôle injectées explicitement : routage natif non évalué.
- Effort effectif inconnu si le fournisseur ne le retourne pas.
