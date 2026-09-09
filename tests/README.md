# Tests automatiques

[Accueil qualité](../docs/quality-lab/README.md) · [Scénarios des agents](../benchmarks/README.md)

Ces tests vérifient que les outils du dispositif continuent de fonctionner.
Ils utilisent des données synthétiques, sans appel à un modèle ni base client.
Ils ne remplacent pas une recette Odoo ou une campagne évaluant les réponses des agents.

## Trois domaines

| Dossier | Ce qui est vérifié |
|---|---|
| [`pilotage/`](pilotage/) | Étapes du travail, plans de release, réception, mémoire, reprise et estimation du temps. |
| [`outillage/`](outillage/) | Preuves, profils générés, packs Studio, scripts de tests/restauration et lecture des consommations. |
| [`laboratoire/`](laboratoire/) | Exécution et correction des essais, mesures de délégation et contrôles du banc Odoo. |

## Exécuter depuis la racine du dépôt

Toute la suite — également exécutée par la CI et `build.sh` :

```bash
python3 -m unittest discover -s tests -v
```

Un domaine :

```bash
python3 -m unittest discover -s tests/pilotage -t tests -v
```

Un fichier, quelle que soit sa catégorie :

```bash
python3 -m unittest discover -s tests -p test_odoo_effort.py -v
```

Ajoutez les nouveaux tests dans le domaine concerné, sous le nom
`test_*.py`. Les fichiers `__init__.py` permettent la découverte récursive.
Les projets et sorties temporaires restent hors du dépôt.
