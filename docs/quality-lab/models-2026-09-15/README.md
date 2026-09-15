# Modèles par rôle — qualification bornée du 15 septembre 2026

Référence Crew `72702f4`. [Protocole figé](protocol.json), [résultats](results.json),
runner explicite `benchmarks/qualification/models/run.py`. Huit appels natifs CLI,
deux cas synthétiques, aucun outil, aucune reprise, aucun projet client.

| Fournisseur | Modèle demandé | Cas | Résultat | Délai jusqu’au contrôle automatique | Modèle observé |
|---|---|---|---|---|---|
| codex | gpt-6-astra | local | accepted | 6.114 s | non retourné |
| codex | gpt-5.6-terra | local | accepted | 5.861 s | non retourné |
| claude | opus | local | accepted | 4.653 s | claude-opus-5 |
| claude | sonnet | local | accepted | 2.482 s | claude-sonnet-5 |
| codex | gpt-6-astra | holdout | accepted | 5.505 s | non retourné |
| codex | gpt-5.6-terra | holdout | accepted | 5.309 s | non retourné |
| claude | opus | holdout | accepted | 5.001 s | claude-opus-5 |
| claude | sonnet | holdout | accepted | 2.334 s | claude-sonnet-5 |

Les huit réponses passent la grille : dépendances, ressources isolées, fin d’agent
sans réception, principal conservé, tests prescrits et date de reçu non invalidante.
Le second cas était réservé avant le lancement. L’oracle est testé avec une
réponse correcte et une mutation par décision critique. Effort demandé medium,
effort effectif non retourné. Tokens et caches sont conservés séparément ; les
montants API déclarés par Claude ne mesurent pas la consommation de l’abonnement.

## Décision

- **Adopté :** politique explicite, refus des modèles légers pour le principal et
  les risques élevés, paramètres demandés/observés séparés, profils natifs Codex.
- **Expérimental :** candidats Terra/Sonnet pour tâches locales et Luna/Haiku pour
  exécutions prescrites. Luna/Haiku ne sont pas mesurés par cette petite campagne.
- Terra gagne environ 4 % sur ces deux cas, sous le seuil préfixé de 20 %.
  Sonnet gagne environ 50 %, mais deux réponses sur dossier ne qualifient pas
  l’implémentation Odoo, la QA, les migrations ou le temps de reprise du principal.
  Aucun modèle de production n’est remplacé à partir de ces chiffres.

L’orchestrateur garde le principal. `odoo_models.py --candidate` rend un choix
expérimental explicite dans le contrat ; disponibilité non observée reste
non vérifiée. Les commandes ordinaires de tests/build ne lancent pas cette campagne.

Sources de configuration : [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
et [Claude subagents](https://code.claude.com/docs/en/subagents).
