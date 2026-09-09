# Estimer les minutes d’exécution des agents

**Adopté dans les outils et profils.** `/odoo-estimate` donne une prévision
par lot de travail et agent ; un lot correspond à une tâche de release.
Le chef de projet applique lui-même ses barèmes. La clôture rapproche la
prévision du temps mesuré et fournit les jetons et coûts IA disponibles.

La référence est `86b12c0f8c76ddc215d919f4df0a2b2db7bb7ae8`.
Le [protocole](protocol.json) conserve le périmètre convenu avant réalisation.
La précision des durées prédites n’est pas démontrée : les premiers chiffres
sont des jugements de confiance faible, à comparer aux futures exécutions.

## Résultat utilisable

- [Exemple d’estimation par agent et lot](example/changelog/demo/estimation.md),
  préparé sur deux demandes fictives par un agent indépendant.
- [Export CSV](example/changelog/demo/bilan-effort.csv) : durées seules à reprendre
  dans une offre ; aucun barème client appliqué.
- [Bilan d’une délégation réellement exécutée](native/changelog/execution-passee/bilan-effort.md),
  importé des traces déjà publiées de la campagne E02-D.
- [Mode d’emploi](../../EFFORT.md) : estimation, révision, mesure, import et clôture.

Le registre garde la prévision initiale, les révisions motivées et les passages
successifs d’un agent. Les durées absentes restent inconnues ; le parallélisme
ne réduit pas la somme des minutes travaillées. Une prévision postérieure au
travail ou un périmètre changé ne produit pas de faux écart comparable.

## Essais et corrections

La [relecture indépendante](evidence/review/review.md) compte **16 contrôles
réussis après correction** : temps incomplet, montant natif perdu à l’arrêt,
modèle connu tardivement, périmètre sans plan et deux tarifs au même instant.
Les [résultats rouges initiaux](evidence/review/results-before-fixes.json) sont
conservés séparément des contre-épreuves. Deux risques de lecture supplémentaires
ont été corrigés avant reproduction ; aucun résultat rouge n’est revendiqué pour eux.

L’[essai d’utilisation](evidence/trial/review.md) a exécuté **7 commandes et
11 contrôles** : deux lots, huit lignes, recette commune unique et révision
partielle. Les sept autres lignes restent identiques, l’initial est conservé.
L’anglais « low » relevé dans cet essai a été traduit en « faible » dans le
Markdown final. La sortie CLI reste du JSON destiné à l’orchestrateur ; le
chef de projet reçoit les livrables lisibles.

L’import d’une ancienne session a révélé le besoin de déclarer une tâche sans
inventer sa prévision. `add-task` couvre ce cas ; [7 contre-épreuves CLI](evidence/review/add-task-review.md)
passent après correction d’un titre différent accepté silencieusement.
Le rouge et le résultat corrigé sont conservés.

**251 tests déterministes réussis**, contre 198 à la référence. Ils comprennent
un cycle de scellement/vérification avec suivi activé, mesures absentes et
altération de chaque livrable. Une ancienne release sans registre reste compatible.
Graphe valide ; builds isolé et actif conformes ; parité de **28 fichiers,
2 blocs d’aiguillage et pointeur personnel** ; nouveau skill validé.
Les [journaux de validation](evidence/validation/) conservent les sorties.
La CI du commit livré est vérifiée après publication ; son identifiant est
consigné dans la mémoire locale du dispositif.

## Vérification sur une vraie délégation

Les deux traces natives publiques d’[E02-D](../delegation-comparison-2026-09-09/README.md)
ont été importées séparément : **3,44835 min** pour le principal et
**1,0081167 min** pour la relecture, soit **4,45647 min cumulées** sur
**3,44910 min écoulées**, et **571 715 jetons**. Ces résultats concordent avec
les compteurs de la campagne précédente. Aucun coût n’est inventé sans tarif,
aucune estimation initiale n’est reconstruite. Le [résultat JSON](native/result.json)
et le registre gardent la provenance ; aucune nouvelle conversation brute n’est publiée.
Ce cas prouve l’import parent/enfant, pas l’exactitude d’une prévision future.

## Limites à conserver

L’estimation est un jugement structuré à trois points, pas un modèle prédictif
entraîné ni une conversion en temps humain. Les outils et attentes internes
font partie du temps mobilisé ; les attentes humaines doivent être arrêtées
explicitement. Le bilan de l’orchestrateur s’arrête aux derniers compteurs déjà
observables : son propre message final n’y figure pas encore.

La fourniture du chemin de session est explicite, sans découverte automatique
universelle. Le parseur refuse les formats ambigus ; les tests synthétiques
Codex/Claude et l’import Codex réel ne couvrent pas toutes les versions historiques.
Une durée native partielle est laissée inconnue, même si cela perd son sous-total.
L’attribution des tâches est déclarative ; le contenu métier privé n’est pas inspecté.
Le refus de doubles attributions est limité aux releases du même projet.

Le coût IA est déclaré par la source ou calculé avec une carte technique datée
explicitement fournie, jamais avec un barème d’offre. Une valorisation API n’est
pas une facture d’abonnement ; les catégories et devises restent séparées.
Les essais ont utilisé les sous-agents disponibles dans cette session, sans
appel API/CLI de modèle facturé séparément, base client ou environnement de production.

Pour rejouer les scripts de revue archivés, utiliser une copie de travail jetable :
ils recréent leurs propres cas sous `/tmp/odoo-effort-review-20260909` et lisent
le référentiel installé. Les tests de `tests/` sont portables et exécutés en CI.
