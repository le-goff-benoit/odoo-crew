# Contexte ciblé et vérifiable

`odoo_context.py` prépare un contexte de lecture sans modifier le projet consulté.
L’API reste `context(project, query='', budget=12000)` et
`verify_context(record, project)`. Le JSON produit porte maintenant `schema: 2` ;
les anciens enregistrements restent vérifiables avec leurs contrôles de fichiers.

## Sélection

Le corpus comprend `.odoo-agents/PROJECT.md`, `JOURNAL.md`, `DECISIONS.json`,
`decisions/*.md` et `changelog/*/revue_fonctionnelle.md` lorsqu’ils existent.

1. Le rendu validé de **DECISIONS.json est obligatoire et entier** : décisions
   courantes, propositions identifiées, questions ouvertes et références aux
   remplacements. Une proposition ne devient pas une décision confirmée.
2. Les sections de compréhension métier, règles, contraintes et décisions du
   `PROJECT.md` viennent ensuite, d’après leur titre.
3. Les correspondances lexicales dans le chemin, le titre et le contenu donnent
   la pertinence à la tâche ou release demandée. Par exemple, `--query 'T08
   livraison établissement'` recherche ces mots dans toutes les sources.
4. Sans requête, les autres sections sont proposées selon la place restante.

Les unités sont des **sections Markdown complètes** au premier niveau de titres
utile, après le titre du document. Leurs sous-titres, paragraphes, listes et blocs
code restent ensemble. Un titre frère « Exceptions », « Limites », « Conditions »,
« Attention », « Sauf » ou « Cas particuliers » reste attaché à la règle précédente.
Un document sans titres reste indivisible. Une section trop longue est omise
entièrement, jamais coupée avant une exception.

Ce découpage reste structurel. Un renvoi vers une autre section exige d’ouvrir
cette section aussi ; l’outil ne comprend pas tous les liens métier implicites.
La sélection lexicale ne garantit pas le rappel des synonymes et ne résout aucune
contradiction. **Une date ne vaut jamais arbitrage**, même entre deux textes du
même jour. L’ordre des chemins en cas d’égalité sert seulement à stabiliser
l’affichage. Seul un remplacement explicite dans la mémoire de décisions permet
d’écarter une ancienne règle comme remplacée.

## Budget, omissions et provenance

Le budget est exprimé en **caractères Python**, pas en tokens. Il couvre exactement
le texte envoyé sur stdout : en-tête, avertissement, références, sections et index
des omissions compris. `actual_characters` et son alias `emitted_characters`
mesurent cette chaîne ; `budget_characters` rappelle le budget demandé.

Le texte indique les fichiers et lignes des sections omises. Le JSON conserve pour
**toutes** les sections leurs titres, lignes, empreintes, priorité, inclusion et
motif d’omission, plus le catalogue complet et les empreintes des fichiers.
`sources` conserve la projection historique des fichiers candidats à la sélection ;
`sections` et `catalog_paths` décrivent également les sources non pertinentes.
Le JSON de provenance a son propre volume et n’entre pas dans le budget stdout.

`budget_status: insufficient` signifie que les décisions obligatoires et/ou
l’index complet dépassent déjà le budget. Le texte l’annonce et restitue ces
éléments entièrement. Il faut lire les obligations et augmenter le budget si
nécessaire : ce statut n’autorise pas à ignorer une décision. Un budget d’au moins
1 000 caractères reste requis. `minimum_characters` mesure le socle obligatoire
avec l’index, avertissement d’insuffisance compris quand il est émis.

`verify_context` invalide le contexte si un fichier du catalogue est ajouté,
supprimé ou modifié, y compris un fichier ou une section omis. Il vérifie aussi le
texte, la sélection et les empreintes des sections ; une falsification de l’index
n’est pas acceptée. Les références de la mémoire sont revalidées lors du recalcul.

## Commandes

Choisir un chemin de sortie hors du projet consulté pour conserver sa lecture seule :

```bash
python3 ~/.odoo19-agents/scripts/odoo_context.py /chemin/projet \
  --query 'T08 livraison établissement' --budget 12000 \
  --output /tmp/contexte-projet.json
python3 ~/.odoo19-agents/scripts/odoo_context.py /chemin/projet \
  --verify /tmp/contexte-projet.json
```

Pour ouvrir une omission `L12-L28` de `PROJECT.md`, lire le bloc complet :

```bash
sed -n '12,28p' /chemin/projet/.odoo-agents/PROJECT.md
```

La génération n’écrit que le chemin explicitement fourni à `--output`.

## Mesure synthétique du 15 septembre 2026

Fixture : un `PROJECT.md` avec compréhension métier, une longue section historique
sans rapport, une section Livraison T08, plus une décision séparée. Corpus :
**11 316 caractères** ; requête `livraison T08` ; budget **1 800 caractères**.
Les textes, références et indices réellement émis ont été comptés ; le saut de
ligne ajouté par l’ancienne CLI est inclus dans sa mesure.

| Version | Caractères du contexte | Règle métier utile présente |
|---|---:|---|
| Avant, sélection de fichiers entiers | 210 | Non : PROJECT entièrement omis |
| Après, sélection de sections complètes | 613 | Oui, avec le contrôle de livraison |

Le JSON après sélection contient cinq sections et mesure 3 945 caractères sur
cette exécution, chemin temporaire absolu inclus ; sa taille varie avec ce chemin.
Ces résultats montrent une meilleure couverture dans le budget, **pas un gain de
tokens mesuré**. Ils ne prétendent pas que toute requête donnera un contexte plus
court que l’ancien sélecteur.

## Vérifications

```bash
cd ~/.odoo19-agents
python3 -m unittest tests.pilotage.test_odoo_context_scenarios -v
python3 scripts/odoo_flow.py validate
```

Les 23 tests de ce fichier couvrent notamment le gros PROJECT, l’index des
omissions, la mesure exacte de stdout, l’exception en fin de règle, les décisions
obligatoires dépassant le budget, les contradictions du même jour, les blocs code,
la modification d’une source omise et la falsification de provenance. Ils
utilisent des projets temporaires synthétiques. La suite complète et la génération
des profils restent les contrôles d’intégration du dépôt.

## Dès le briefing

Pour éviter de charger toute la mémoire puis de la sélectionner une seconde fois :

```bash
python3 ~/.odoo19-agents/scripts/odoo_briefing.py /chemin/projet \
  --query 'T08 livraison établissement' --budget 12000 \
  --context-output /tmp/contexte-projet.json
```

Ce mode remplace les blocs PROJECT/journal/décisions du briefing par la sélection.
La série, l'état, les formes attendues et les leçons communes restent ajoutés ;
ils sont hors du budget de mémoire. Le mode complet historique demeure disponible
sans `--query`. Le JSON ne doit pas être injecté intégralement au modèle : son
texte et son index suffisent, la provenance sert à vérifier et ouvrir les omissions.
`--full-journal` et `--query` sont incompatibles afin de ne pas annoncer une archive
complète qui aurait été filtrée. Le contrat original reste à lire.
