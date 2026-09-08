# Du pilote aux premières améliorations vérifiées — 8 septembre 2026

**Décision : adopter les corrections outillées et la consigne développeur sur
les entrées RPC ; conserver les variantes d'analyse comme expériences.**
Le rôle compact est plus rapide dans l'échantillon, mais les réponses ne sont
pas toutes suffisamment fiables pour remplacer le rôle complet.

## Ce qui a effectivement été mesuré

Après le pilote v1 : **34 générations**, dont 24 passations et 10 fichiers de
code, plus six appels du correcteur indépendant en contexte. Les générations
représentent 3 388,8 s cumulées (56,5 min), le correcteur 696,7 s (11,6 min).
Une partie de la dernière itération a chevauché la correction : ces sommes ne
sont pas la durée murale du chantier. Les contrôles métier prennent quelques
secondes par variante, en plus du gabarit créé pour chaque campagne.

- Analyse : B10 v2 (remise) et B11 réservé (livraison), trois variantes, deux
  outils, deux répétitions, ordre ABC puis CBA ; rôles et dossiers figés.
- Développement : B12/S-01, mêmes instructions, Codex high/medium et Claude
  medium/high. Puis deux corrections des instructions à effort medium.
- Transfert : B13/S-02, notes de frais avec une règle de revalidation inversée,
  Claude medium. V2 figée sur le défaut B12 avant lecture du résultat B13 v1.
- Exécution : Odoo 19 réel, bases synthétiques séparées, utilisateurs limités,
  sources et logs hachés, conteneurs nettoyés. Aucune base client.

Les modes sont **génération sur dossier sans outils, puis contrôle externe**.
Ils ne reproduisent pas encore toute une session native `/odoo-new`, ses couches
AGENTS/skills personnelles, ses recherches ni ses échanges avec un vrai client.

## Volume de directives, durée et fidélité métier

La référence compte **1 866 mots**, fidélité 1 930, compact 299 (−84 %).
Le compact change aussi la structure et le contenu ; ce n'est pas une expérience
qui isole le seul nombre de mots.

| Outil / effort demandé | Variante | Durée médiane, 4 essais | Conforme selon le juge | À revoir | Rejet critique |
|---|---|---:|---:|---:|---:|
| Codex / high | Référence | 97,5 s | 3 | 1 | 0 |
| Codex / high | Fidélité | 97,2 s | 3 | 1 | 0 |
| Codex / high | Compact | 89,3 s | 4 | 0 | 0 |
| Claude / medium | Référence | 135,9 s | 0 | 0 | 4 |
| Claude / medium | Fidélité | 126,5 s | 1 | 3 | 0 |
| Claude / medium | Compact | 90,6 s | 1 | 3 | 0 |

Ces verdicts sont **les avis du correcteur LLM masqué**, pas une vérité de
référence humaine ni une validation générale. Les quatre rejets critiques
portent notamment sur des hypothèses à appliquer sans arbitrage client et des
conclusions standard non vérifiées. Les réserves restantes concernent surtout
les tests de borne, les questions rouvertes alors que le client a répondu, et
l'ambiguïté entre hypothèse, règle technique et décision métier.

Le correcteur ne voit ni modèle, ni variante, ni rôle de génération. Il a
réussi les deux calibrations : passation correcte / même passation contredite
par une clôture abusive des questions. Les citations sont vérifiées contre les
réponses. Cela ne suffit pas à garantir son interprétation : voir
[la revue des arbitrages](REVIEW-NOTES.md). On conserve les avis et les réserves,
sans retoucher rétroactivement la grille ni les résultats du pilote v1.

**Pas de remplacement global du rôle analyste.** Le compact a un intérêt mesuré
sur ce dossier, notamment pour Codex, mais il reste à tester sur d'autres métiers
et dans un workflow avec outils. Une poignée de réponses ne classe pas les
fournisseurs, ni les niveaux d'effort dont les échelles diffèrent.

## Développement : une précision utile plutôt qu'un effort accru par défaut

Tous les codes ci-dessous ont été exécutés **sans réparation** avec le même
oracle final de livraison (13 méthodes : neuf métier, quatre transport).

| Instructions | Outil / effort | Durée de génération | Résultat métier |
|---|---|---:|---|
| Référence | Codex / high | 178,1 s | Conforme aux tests |
| Référence | Codex / medium | 63,8 s | Conforme aux tests |
| Référence | Claude / medium | 60,6 s | Rejet : défauts RPC et drapeau de contournement |
| Référence | Claude / high | 206,0 s | Même défaut critique |
| Protection RPC v1 | Codex / medium | 71,6 s | Conforme aux tests |
| Protection RPC v1 | Claude / medium | 74,6 s | Drapeau corrigé ; défauts RPC encore forgeables |
| Protection RPC v2 | Codex / medium | 63,2 s | Conforme aux tests |
| Protection RPC v2 | Claude / medium | 65,8 s | Conforme aux tests |

V1 rappelle qu'un contexte RPC ne peut pas donner une autorisation. V2 ajoute
le mécanisme manquant : **retirer une clé de `vals` ne neutralise pas le défaut
que `super().create()` ajoutera ensuite** ; fixer des valeurs sûres ou contrôler
les valeurs effectives. L'ajout ciblé est désormais dans `roles/implementation.md`.

Sur B13, les deux variantes Claude medium passent les six tests de notes de frais
après correction d'un défaut de l'oracle ; génération en 43,8 s / 40,0 s.
Le transfert est donc observé, mais V2 n'est pas supérieure à V1 sur tous les cas.
Une seule génération par réglage : ne pas changer les modèles ou efforts globaux
sur cette base. Les durées de cette itération ont aussi pu subir la concurrence
avec le correcteur ; aucun gain causal de vitesse n'est revendiqué pour V2.

## Le banc doit aussi être testé

1. **Faux vert réel** : l'ancien `odoo-test.sh` annonce installation/tests propres
   sur une base vide existante avec **zéro test**. La correction installe le module
   absent et obtient **12 tests verts** dans l'essai comparatif conservé :
   7,66 s / 8,37 s. La fiabilité augmente, pas la vitesse dans cette mesure.
2. **Sensibilité** : trois mutants de livraison et deux de notes de frais sont
   détectés (bornes, auto-approbation, accord périmé). Chaque oracle commence par
   une référence qui doit passer. Cela ne prouve pas une couverture exhaustive.
3. **Référence imparfaite** : les premiers tests renforcés ont trouvé des défauts
   dans notre propre référence (défauts RPC, réécriture identique). Elle a été
   corrigée avant les premières générations B12.
4. **Faux rejets de l'oracle** : une valeur forgée ignorée n'a pas à déclencher une
   exception donnée ; un paiement effectivement bloqué ne doit pas être rejeté
   parce que le code lève `AccessError` au lieu de `ValidationError`. Les tests
   jugent désormais les états métier. Les traces avant/après sont conservées ;
   tous les candidats ont été réévalués avec le même oracle final.

Les scripts de contrat passent **91 tests sous Python 3.10 et 3.12** ; le graphe,
la syntaxe shell et Ruff (erreurs F, hors imports de modules Odoo) passent ; les vingt fichiers générés et
les deux blocs Claude/Codex sont conformes. Le workflow GitHub répète les
contrôles déterministes sans aucun appel LLM.

## Décisions et suite du dispositif

Adoptés : briefing sans pertes silencieuses des leçons, mémoire structurée
optionnelle avec état inconnu explicite, preuves liées au code, verdicts QA plus
stricts, contrôles de restauration et de packs, protections RPC, verrous physiques
optionnels, récupération des runs et consigne développeur V2. Les détails et
limites sont dans [TOOLING-CHANGES.md](../TOOLING-CHANGES.md).

Restent non démontrés : bénéfice global d'un rôle compact, workflow natif complet,
mémoires très longues, autres séries Odoo, migrations et métier d'un vrai client.
Les bindings de ressources et `DECISIONS.json` restent facultatifs ; aucune
migration automatique des projets client. B11/B13 ne seront plus des cas réservés
après cette étude : en créer de nouveaux pour une autre itération.

Pour reproduire et adapter : [mode opératoire](../OPERATIONS.md). Les réponses,
grilles, rôles figés, avis du juge, codes candidats et preuves QA sont dans les
sous-dossiers de cette expérience. Les sorties CLI brutes et l'analyse contenant
des informations client restent locales. Il s'agit d'ajuster instructions et
outils à partir de preuves, pas de réentraîner les poids des modèles.
