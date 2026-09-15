# Boucle agents : correctifs Odoo et réception

Campagne ouverte le 15 septembre, exécutée les 15–16 septembre 2026.
[Protocole figé](protocol.json) · [Calibration ORM](calibration.md) ·
[Extension PDF 18/19](pdf-cohorts.md).

## Point de départ

Les six parcours W01–W06 étaient des calibrations de contrôles. Les essais de
modèles légers portaient sur des réalisations Python ; ils ne démontraient pas
une accélération des développements Odoo. La campagne mémoire conservait deux
acceptations, une réserve et un rejet, sans nouveau passage après correction.

Cette campagne ajoute deux réalisations natives :

- **N06** : réparer des brouillons tout en préservant références déjà émises et
  autre société, reprendre les données existantes, vérifier l’idempotence et les
  droits d’un utilisateur ordinaire malgré une ancienne QA trompeuse.
- **N07**, réservé : préparation périodique, saisie manuelle à zéro, copie et
  reliquat. Vrais modèles ORM synthétiques ; ce cas ne qualifie pas `stock.picking`.

Les mécanismes sont issus de régressions récentes ; la correspondance aux projets
et documents clients reste dans le dossier privé local. Aucun fichier client
n’entre dans le corpus ou dans le contexte des agents du banc.

## Reproduire la boucle

```bash
python3 scripts/odoo_bench_agent_workflows.py baseline --output /tmp/nouvelle-boucle
# Examiner les deux N06, corriger les seules causes observées, commiter le candidat.
python3 scripts/odoo_bench_agent_workflows.py candidate --output /tmp/nouvelle-boucle --candidate <commit>
python3 scripts/odoo_bench_agent_workflows.py status --output /tmp/nouvelle-boucle
```

Huit appels natifs maximum, 900 secondes par appel, deux environnements isolés.
La deuxième commande réserve six appels : N06 candidat puis N07 référence/candidat.
Aucune reprise automatique ni appel modèle en CI. Les cas, correcteurs, helpers et
révisions sont figés. Un essai interrompu reste conservé ; une phase déjà commencée
ne peut pas être relancée silencieusement.

## Mesures et interprétation

Le runner conserve préparation, durée de l’agent, commandes, modèle/effort observés,
oracle indépendant et empreintes du code avant/après chaque contrôle. Lint, QA et
update doivent concerner les sources finales. Une erreur fournisseur ne devient
pas un succès parce que le CLI a aussi émis une fin de réponse.

La porte mécanique ne remplace pas la réception sémantique. Le délai jusqu’à
réception acceptée reste **non mesuré** tant que cette réception n’a pas eu lieu.
Un échec rapide n’est pas une amélioration. Les reprises des agents sont distinctes
des nouvelles variantes d’instructions de l’expérience. Ne pas additionner les
jetons d’entrée et le cache, ni transformer un coût manquant en zéro.

La comparaison native est terminée : **8 appels, 7 exécutions achevées et un
arrêt au plafond de 900 s**. Les huit codes passent l’oracle métier ; cela ne
suffit pas à recevoir les huit travaux. Les réceptions indépendantes et les
mesures détaillées sont conservées dans [les preuves](evidence/native/) et
[le bilan machine](summary.json).

### Durée des agents — comparaison à réglages constants

| Cas | Fournisseur | Référence | Candidat | Variation observée | Réception candidat |
|---|---|---:|---:|---:|---|
| N06 | Codex | 10 min 33 s | 11 min 33 s | +9.3 % | Avec réserves |
| N06 | Claude | 12 min 52 s | 9 min 34 s | -25.6 % | Avec réserves |
| N07 | Codex | 10 min 28 s | 10 min 30 s | +0.3 % | Avec réserves |
| N07 | Claude | 13 min 16 s | 15 min 00 s | Plafond atteint | Refusé, incomplet |

**Qualité :** huit oracles métier verts, sept réceptions avec réserves et un rejet.
Aucune porte mécanique entièrement verte : sept essais gardent le lint global
rouge ; le dernier a les contrôles finaux verts mais une exécution interrompue.
Le candidat Claude N07 ajoute un cron quotidien non demandé, ne livre pas le test
« reliquat puis cron » et laisse journal/réception inachevés. Cet exemple montre
pourquoi l’oracle et la réception indépendante doivent rester distincts.

### Travail mesuré jusqu’au verdict indépendant

Inclut préparation, exécution, oracle et revue ; **ce n’est pas un délai jusqu’à
acceptation sans réserve**. L’attente avant revue figure séparément dans le JSON.

| Cas | Fournisseur | Référence (s) | Candidat (s) | Verdicts référence / candidat |
|---|---|---:|---:|---|
| N06 | Codex | 865.24 | 903.50 | Réserves / réserves |
| N06 | Claude | 1016.85 | 824.98 | Réserves / réserves |
| N07 | Codex | 920.43 | 947.27 | Réserves / réserves |
| N07 | Claude | 1053.35 | 1205.17 | Réserves / refus |

Sur N06 Claude, le travail mesuré baisse de **18,9 %**, contre **25,6 %** pour
le temps agent seul. Ce résultat ne se transfère pas à N07. Sur Codex, il augmente
d’environ **4,4 %** sur N06 et **2,9 %** sur N07. Les durées jusqu’à réception sans
réserve restent inconnues pour les huit essais.

La couverture n’est pas uniformément meilleure : N06 Claude candidat omet le
contre-test de dates égales dans la même société ; ses affirmations sur une dette
de lint et des preuves « signées » ne sont pas étayées. Les réserves de la référence
restent aussi publiées. Aucun score agrégé ne masque ces écarts.

## Décision d’adoption

| Changement | Décision | Motif |
|---|---|---|
| Ordre du travail du développeur | **Adopté comme clarification** | Retire une contradiction interne : le rôle prescrivait déjà le rouge avant correction, puis indiquait les tests après le code. Aucun gain de vitesse attribué à cette seule retouche. |
| Capture anticipée, réutilisation élargie entre voies QA, fragments courts | **Expérimental, non activé** | Doublon vert Claude N06 absent après adaptation, mais captures encore rejouées et contre-épreuve Claude N07 incomplète. La variante globale n’est pas qualifiée. |
| Aide CLI de capture | **Adoptée comme correction documentaire** | `--module` exige des tests ; un simple update ne doit pas l’utiliser. Le helper réserve aussi son fichier `.log`. Texte vérifié sur le code et par `--help`, effet natif non remesuré. |
| Mesures et suivi du banc | **Adoptés** | Valeurs inconnues conservées, réception complète conditionnée aux contrôles, statut lu depuis chaque essai, même pendant l’attente d’un autre. Régressions déterministes. |
| Lecture JUnit de Tricorder | **Adoptée, version 0.3.2** | Un rapport mixte ou incohérent ne masque plus un échec. Tests backend, UI et paquet installé vérifiés. |
| Routage vers des modèles plus légers | **Inchangé** | Cette campagne compare des consignes, pas des modèles. Aucun modèle principal remplacé. |

Le candidat complet reste dans le commit `015e8a3` et dans les archives. Les
profils livrés reviennent aux consignes de référence, avec la seule clarification
d’ordre des tests conservée. **Cette combinaison finale n’est pas une nouvelle
variante native évaluée** : elle ne reçoit pas les résultats de vitesse du candidat.
Les corrections d’aide et de statut sont postérieures au gel de la campagne.

Le rejet d’une qualification n’est pas la preuve que chaque nouvelle phrase a
causé le défaut : les trois rôles avaient changé ensemble. L’ajout de cron,
les erreurs de capture et les omissions constatées ne sont pas prescrits par
les nouvelles consignes. Une comparaison supplémentaire serait nécessaire pour
isoler leurs causes ; aucune attribution causale ni économie de release n’est
revendiquée.

## Adaptation mise à l’essai

Référence `284379f4c1d120e2462625ee3878ba5fbb0da5f8`, candidat
`015e8a34861bf82b52298468b1170cbee93f445f` :

- L’orchestrateur fixe commande, portée et destination de preuve avant le premier test.
- Le développeur capture rouge et vert dans des fichiers distincts ; la contradiction
  « tester d’abord / écrire les tests après le code » est retirée.
- La QA reçoit les preuves encore valables avant de relancer une commande ; un
  changement de code, données, environnement ou critère exige le contrôle affecté.
- Les fragments de réception pointent vers le contrat et les preuves communes.

La référence Claude N06 a exécuté une QA verte identique en fin de parcours
(22,14 s) et un inventaire supplémentaire pour sauver sa sortie (1,31 s).
Les autres relances QA et lint étaient justifiées par un changement de portée ou
de sources : aucune consigne générale ne cherche à les supprimer.

## Ce que mesurent les chiffres

`agent_seconds` couvre le CLI, le fournisseur et les outils. Le travail mesuré
jusqu’au verdict ajoute préparation, oracle et réception indépendante ; le délai
calendaire ajoute aussi l’attente de réception. La revue est réalisée par un
agent distinct sur les archives immuables, sans rejouer Odoo. Les relecteurs
connaissent le nom de la variante : cette revue n’est pas en aveugle. Leur
familiarité avec le cas peut influencer sa durée.

Les huit réalisations natives sont le plafond de la comparaison, pas un décompte
de tous les échanges de l’orchestrateur et des relecteurs. Aucune reprise après
réception n’est exécutée dans cette campagne. Son coût reste inconnu ; une variante
candidate ne compte pas comme réparation rétroactive d’un résultat de référence.

Une acceptation avec réserves n’est pas une réception sans réserve. Les fixtures
comportent dès le départ un manifest sans `author`, qui maintient le lint global
rouge. La grille métier, les observations du relecteur et la porte mécanique sont
publiées séparément ; aucun oracle vert ne transforme ce lint en succès.

Les modèles demandés restent Codex `gpt-6-astra` / high et Claude `opus` / medium.
Claude retourne `claude-opus-5` ; Codex ne retourne pas le modèle effectivement
servi. Les efforts effectivement appliqués ne sont pas retournés. Les comparaisons
se font dans chaque fournisseur, sans classement entre eux. Une observation par
paire, avec deux essais concurrents isolés, ne prouve pas un gain général.

L’incident initial de build a eu lieu avant les appels modèles. Il est conservé
sous `evidence/preparation` ; la deuxième préparation utilise le même répertoire
courant de build pour les deux révisions. Ni profil de référence ni réponse native
n’ont été corrigés après coup.

## Prochaine itération ciblée

Les archives identifient des pistes à tester séparément, sans les présenter comme
une amélioration déjà obtenue :

1. **Fiabilité des preuves** : comparaison de dette sur une base exportée propre
   (un `git stash` sans fichiers non suivis ne suffit pas), distinction d’une QA
   et d’un simple update, et conservation de chaque tentative de capture.
2. **Couverture contradictoire** : même date dans la même société pour départager
   par identifiant ; contextes de droits préparés avant le scénario négatif.
3. **Mesure jusqu’à réception complète** : fixture sans dette de packaging
   parasite, budget distinct pour les reprises demandées par le relecteur et
   répétitions pour séparer variation du fournisseur et effet des consignes.
4. **Transfert au métier standard** : nouveaux appels natifs sur les parcours
   `stock.picking` et PDF déjà calibrés. N07 ORM ne les remplace pas.

Ces pistes ne justifient ni une accumulation de consignes dans tous les rôles ni
le passage automatique à un modèle plus léger. Le prochain essai devra réserver
un nouveau cas inédit : N07 a désormais été utilisé.

## Vérification et reproduction des mesures

Les quatre fichiers du runner figé correspondent exactement au commit
`f11913d` ; leurs SHA-256 et ceux du corpus sont dans
[evidence/native/campaign.json](evidence/native/campaign.json). Les changements
ultérieurs du statut et de l’aide CLI n’entrent pas dans les appels comparés.
Chaque dossier publié conserve état, code produit, preuves du projet, logs du pont,
oracle et réception indépendante. Les événements natifs complets restent dans
l’archive locale indiquée par `archive.json`, avec leurs empreintes publiées.

Recalculer les mesures publiées ne lance aucun modèle ni Odoo :

```bash
python3 docs/quality-lab/agent-workflows-2026-09-15/summarize.py \
  --campaign docs/quality-lab/agent-workflows-2026-09-15/evidence/native \
  --output /tmp/agent-workflows-summary.json
```

Validation de la livraison : graphe (59 nœuds, 129 arêtes), 394 tests automatiques
(un ignoré), build isolé puis actif, parité de 35 fichiers et deux blocs, skill
modifié valide. Les nouveaux tests de résumé refusent les inconnus transformés en
zéro et une réception sans réserve derrière une porte rouge ; les tests de statut
vérifient les états en cours/terminés/non démarrés sans mutation des archives.
Tous les environnements Docker créés par la campagne sont retirés ; les services
préexistants sont conservés. Aucun appel modèle en CI.
