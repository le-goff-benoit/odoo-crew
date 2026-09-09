```
[4/4 journal]   entrée écrite · PROJECT.md : décisions réécrites (D-03 en vigueur, D-01/D-02 mortes), 3 pièges ajoutés · flow TERMINÉ
```

# Frais de préparation révisés (D-03)

**Projet** Atelier Boréal (`/work`) · **série** 19.0 (manifest) · **release** `2026-09-09_01_frais-de-preparation-des-locations` (point n°2) · **module** `lab_rental`

## À décider

- **`'author': 'Camptocamp'`** au manifest reste à confirmer (dette héritée du point 1).
- **Paramétrage du seuil et du montant** : la règle a été réécrite trois fois en deux jours (D-01 → D-02 → D-03). C'est resté hors périmètre, à raison, mais c'est à reproposer au client. Je ne l'ai pas fait de moi-même.

## Cadrage

D-03 remplace D-02 dans la release en cours. Verdict standard inchangé : à développer. Deux constats ont structuré le travail, et aucun n'était une simple retouche de constantes :

- `lab_client` portait **déjà** les montants D-02 (52.0 / 152.0 / 12.0), donc la reprise part de l'état migré — et certains montants devaient **baisser** ;
- le module y était installé en 19.0.1.1.0, donc son dossier de migration n'aurait **pas** été rejoué. Sans montée de version, la copie serait restée à 12 EUR / 4 jours : vert en test, faux chez le client.

## Réalisation

`models/business.py` (15.0 / 5, docstring sur la filiation D-01 → D-02 → D-03) · `__manifest__.py` en **19.0.1.2.0** · `migrations/19.0.1.2.0/post-migrate.py` (nouveau ; celui de 19.0.1.1.0 est conservé pour une base encore en 19.0.1.0.0) · `tests/test_preparation_fee.py` réécrit en 12 tests, dont deux de non-régression qui interdisent le retour des 7 % de D-01 **et** des 12 EUR de D-02.

## QA de tâche — VALIDÉ

| Contrôle | Résultat |
|---|---|
| Lint des fichiers touchés | 0 erreur, 0 avertissement, 0 info |
| Install base neuve + tests ciblés | `install=ok` · 12/12 · 23 s |
| Mise à jour + tests ciblés | `update=ok` · 12/12 · 8 s |
| Reprise sur `lab_client` | `[19.0.1.2.0>] post-migrate` · 4 j **52.0 → 40.0**, 7 j 152.0 → 155.0, 5 j tarif nul 12.0 → 15.0, prêts et 3 j inchangés |
| Idempotence | second `-u` sans dérive **et** corps de la reprise rappelé sans écart |
| Périmètre en base | 0 vue, 0 action, 0 menu, 0 règle, 7 champs, dépendance `base` seule |
| XML-RPC réel | 4 j → 40.0 · 5 j → 65.0 · prêt 5 j → 50.0 · copie rendue propre |

**14/14 critères couverts**, détail et empreintes dans `qa_reception_point2.md` et `coverage.json`.

Une réserve consignée plutôt que masquée : le second `labctl update` ne rejoue pas le post-migrate (version déjà 19.0.1.2.0). Il prouve l'absence de dérive, pas l'idempotence de la reprise — que j'ai donc mesurée séparément en rappelant le corps du script.

## Traitement du point 1

Sa QA n'était pas « à rejouer » : ses oracles sont **faux** sous D-03 (elle atteste 52.0 pour une location de 4 jours). Le point 1 est marqué **PÉRIMÉ** dans le README de la release et en tête de `qa.md`, avec les trois preuves nommément invalidées. Rien n'a été effacé ni réécrit : la revue, les artefacts et le flow `frais-preparation` sont intacts, hashes compris.

## Reste à faire

Recette complète à la clôture (`/odoo-close`), en incluant le chemin d'un client encore en 19.0.1.0.0 qui traverserait les deux reprises — non joué ici. La communication de clôture ne doit jamais mentionner l'étape 12 EUR / 4 jours : elle n'a existé que sur la copie de validation.

## Release

2 points, 1 réalisé et 1 périmé-remplacé. **Release toujours ouverte.**