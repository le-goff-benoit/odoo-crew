# Des essais aux nouveaux agents — campagne native du 9 septembre 2026

Cette itération vise l'adoption de corrections dans les profils Claude Code et
Codex. Le banc est le moyen de les éprouver ; ses scores ne sont pas le livrable
final. La [matrice des propositions](../../IMPROVEMENTS.md) relie l'analyse privée
aux changements, preuves et limites. Le document privé n'est pas publié.

## Protocole et portée

Référence historique `9541bba`, dispositif du 8 septembre `5868225`. Les parcours
N01–N03 comparent ces deux états. N04 compare `5868225` à `45bd620` après la
correction SQL ; N05 compare `5868225` à `c8a3796` après la réserve de précision, puis
à `c1eb5e8` avec le transport lint accessible aux deux variantes.
Les archives de profils sont générées depuis Git, pas depuis les fichiers actifs.
Les empreintes du runner et du corpus sont conservées dans chaque protocole.

Odoo 19 réel, PostgreSQL isolé, données fictives ; transport supervisé et CLI
natives. Codex : `gpt-6-astra`, effort `high` ; Claude : alias `opus`, effort
`medium`, modèle retourné `claude-opus-5`. Ces niveaux ne sont pas une échelle
commune. Codex ne restitue pas toujours l'identité effective : ne pas confondre
le modèle demandé avec une version attestée. Aucun classement général.

Les modèles lisent les skills et pilotent le graphe, produisent revue,
implémentation, tests, QA, reprise locale et journal. N01 ajoute une seconde
instruction dans un contexte neuf. Les rôles sont appliqués par un même
orchestrateur : la délégation et le navigateur ne sont pas évalués ici.
Une génération par cellule, ordre A/B inversé entre les fournisseurs. Plusieurs
campagnes simultanées : durées descriptives sous charge variable, sans effet
causal attribuable à une instruction isolée.

## Ce que les essais ont changé

| Observation | Correction canonique | Contre-épreuve et décision |
|---|---|---|
| Six erreurs de tests SQL dans N01 : exception UI attendue dans un appel ORM | Développeur : vérifier l'exception dans les sources de la série, écriture/flush et rollback appropriés ; retirer la prescription universelle `ValidationError` | N04 impose une contrainte SQL, zéro valide et état préservé. Les résultats natifs ci-dessous distinguent succès final et défaut de test |
| Reprise N02 annoncée convergée malgré un écart significatif | Développeur/QA : précision issue du champ et du contrat ; tester les petits écarts ; distinguer valeurs stables et absence d'écritures | Script original rejoué sans correction manuelle : référence conserve 20.004 au lieu de 20.0 ; candidat antérieur corrige. N05 éprouve une nouvelle génération ; pas un cas inédit |
| Réception enfant redevenue verte après nouvelle réception parent | Réception liée au hash du contrat et aux réceptions de dépendances | Revue indépendante : parent revalidé ne valide plus automatiquement l'enfant |
| Version préparée après QA, clôture contournable par route ou copie de preuves | Versions avant QA ; contrôles, périmètre et identité de release dans le sceau ; nouvelle réception possible sur flow terminé | Cinq défauts reproduits puis contre-vérifiés ; aucun faux vert conservé |
| Module vide impossible à démarrer ; nouvelle demande sans commande d'ajout | Empreinte initiale vide avant création du flow ; `odoo_plan.py add` verrouillé, historique et validation globale | Revue indépendante : démarrage vide/futur, conservation des réceptions, refus doublon/cycle/état importé |
| Nouvelle connaissance non sélectionnée pouvant rendre le contexte périmé | Empreintes du catalogue complet, blocs entiers, index des sources omises | Tests rouge puis vert ; ajout, retrait et modification de source contrôlés |
| Anciennes instructions chargées en double | Migration limitée aux blocs générés, sauvegarde, contrôle de parité | Tests de préservation du texte personnel et d'idempotence ; installation active vérifiée à la livraison |

Les défauts du plan, du sceau et du contexte ont été trouvés pendant la
qualification de ces nouveaux outils, avant leur installation. Ils ne sont pas
présentés comme des défauts de l'ancienne version déjà utilisée en production.

Les instructions sur le contrat client, les décisions et les preuves restent
communes aux deux outils. `/odoo-plan` prépare plusieurs demandes ; `/odoo-start`
reprend leurs tâches et réceptions ; `/odoo-improve` organise cette même boucle
jusqu'à adoption ou rejet motivé. `/odoo-feedback` conserve les remarques locales
et passe aussi par cette validation avant de généraliser une règle de rôle. Les projets historiques ne sont pas migrés
automatiquement. [Procédure de reprise](../../RELEASE_PLAN.md).

## Qualité, vitesse et limites de preuve

Le passage QA complet fusionne mise à niveau et tests après installation : deux
chargements au lieu de trois. Les deux scripts passent les mêmes 13 tests Odoo,
y compris contrats RPC et packs. Mesure : ancien 16.61 s, nouveau 19.08 s sous
charge concurrente. **Aucun gain de latence démontré** ; la suppression d'un
chargement redondant ne suffit pas à annoncer une accélération. Les optimisations
de métadonnées RPC restent validées sur la correction et le rejeu, sans gain
réseau chiffré. Le pack Studio N03 produit par Claude est appliqué sans retouche
sur une autre copie neuve avec le nouvel outil : 10 contrôles vrais après chaque
application, puis 0 création / 0 modification / 1 inchangé au deuxième passage.

Le garde de clôture établit présence, périmètre, identité et fraîcheur des preuves.
Il ne juge pas leur sens métier. Les probes du plan utilisent des résultats
simulés explicitement identifiés ; ils ne remplacent pas les essais Odoo réels.
La revue indépendante N02 confirme les oracles initiaux des deux réponses, mais
signale séparément l'erreur de précision et la portée ambiguë de l'idempotence.
Elle est indépendante de contexte, **non aveugle**.

La réduction générale des directives n'est pas adoptée sur la foi de cette
campagne. Les variantes compactes précédentes restent non promues ; les ajouts
retenus répondent à des défauts précis. La couverture d'autres séries, de
comptabilité réelle, des longues mémoires et de la délégation exige d'autres cas.
Un oracle vert ne prouve pas toutes les propriétés du métier.

## Incidents conservés

- Un réseau Docker interne ne publiait pas son port HTTP : proxy de boucle locale
  borné à la copie Studio, puis étalonnage réussi.
- L'archivage refusait les liens `lib64` des environnements virtuels installés par
  les agents : exclusion des dépendances locales, maintien du refus des liens
  dans les livrables. Essais affectés conservés ; nouveaux essais séparés.
- Le premier essai du shell fusionné révélait une fixture important ses tests
  pendant l'installation sans `--test-enable`. Fixture corrigée pour les deux
  variantes, premier échec conservé ; comparaison refaite.
- L'image QA Python 3.12 n'avait pas Git : dix erreurs de prérequis, puis suite
  relancée dans un conteneur temporaire équipé. Aucun test ignoré pour obtenir vert.

- Ruff était masqué par l'isolation Docker dans certaines générations Claude,
  qui ont signalé un lint partiel. Ajout d'un transport `lint MODULE` borné au
  module du cas, appelant le vrai script et l'image QA équipée. Les générations
  antérieures gardent leur réserve ; leur code est contrôlé séparément. Une docstring fautive est alors détectée
  chez le candidat ; nouvelle génération comparative avec lint accessible aux
  deux variantes. Aucun contrôle externe n'est attribué rétroactivement à l'agent.

Les incidents techniques ne sont pas des échecs métier des modèles. Les timeouts
restent des parcours incomplets, même si une partie des oracles passe. Les
réponses et le code ne sont jamais corrigés par le banc pour améliorer leur note.

## Preuves et reproduction

[Commandes d'exploitation](../OPERATIONS.md). Cas et oracles :
`benchmarks/native/`. Les répertoires de preuves contiennent états, réponses,
logs des outils et réalisations synthétiques sélectionnées. Authentification,
homes des fournisseurs, événements CLI bruts et dépendances installées restent
hors du dépôt. `evidence/SHA256.json` contrôle les octets exportés.

Les N01–N05 sont désormais exposés. Une prochaine adoption doit réserver de
nouveaux contrats ; N05 est explicitement un contre-exemple issu de N02.

## Volume de directives

Comptage des caractères Unicode des sources canoniques, hors en-têtes générés :

| Rôle | Avant (`5868225`) | Après | Écart |
|---|---:|---:|---:|
| Analyste | 11 973 | 12 551 | +578 |
| Développeur | 12 535 | 13 724 | +1 189 |
| QA | 15 770 | 16 721 | +951 |
| Orchestration | 17 685 | 18 346 | +661 |
| Clôture | 9 156 | 11 059 | +1 903 |

Les trois nouvelles commandes sont des rôles séparés, chargés lorsqu'ils sont
utilisés. Le nettoyage des anciens blocs générés réduit la duplication du socle
personnel. Ce comptage n'est ni une tokenisation ni le volume réellement envoyé
à chaque tour ; les usages du fournisseur et les fichiers lus restent à analyser
par exécution. Cette livraison privilégie des précisions justifiées et des
contrôles outillés, sans revendiquer une réduction générale des directives.




## Dernière contre-épreuve avec lint accessible

La nouvelle génération N05 utilise effectivement le pont lint dans les deux
variantes. Ruff est exécuté et vert ; le lint global reste rouge pour la seule
clé `author` absente du manifest avant intervention. Les cinq contrôles métier
passent et les deux reprises évitent maintenant la réécriture au deuxième passage.
Ce résultat lève le contrôle manquant du parcours initial ; il ne transforme
pas les premières réponses en QA complètes.

La revue finale conserve une inexactitude du compte rendu candidat : il affirme
qu'aucun test n'a changé entre rouge et vert, alors que des corrections de style
sont visibles entre les deux lints. Aucun affaiblissement des assertions métier
n'a été observé, mais la formulation doit être considérée comme fausse. Le rapport
n'annonce donc pas une qualité rédactionnelle parfaite ni une amélioration
causale du modèle. [Revue finale](evidence/review-n05-lint.json).

<!-- RESULTS START -->
## Résultats des parcours conservés

`executed` signifie que les tours prévus sont terminés. La colonne oracle
porte sur le contrat métier contrôlé ; elle ne signifie pas QA exhaustive.
Les réserves des revues indépendantes sont conservées séparément.

| Campagne | Essai | Tours | État | Oracle | Secondes CLI | Appels outils |
|---|---|---:|---|---|---:|---:|
| smoke-01 | N01-codex-candidate | 1 | incident | non exécuté | 600.0 | 43 |
| smoke-01 | N01-codex-reference | 1 | incident | non exécuté | 547.59 | 50 |
| main-01 | N02-claude-candidate | 1 | executed | 4/4 | 432.04 | 50 |
| main-01 | N02-claude-reference | 1 | executed | 4/4 | 575.4 | 60 |
| main-01 | N02-codex-candidate | 1 | incident | non exécuté | 894.93 | 40 |
| main-01 | N02-codex-reference | 1 | incident | non exécuté | 490.76 | 42 |
| main-01 | N03-claude-candidate | 1 | executed | 10/10 | 639.37 | 60 |
| main-01 | N03-claude-reference | 1 | executed | 10/10 | 836.82 | 80 |
| main-01 | N03-codex-candidate | 1 | executed | 10/10 | 622.98 | 33 |
| main-01 | N03-codex-reference | 1 | executed | 10/10 | 760.43 | 43 |
| n01-02 | N01-claude-candidate | 2 | executed | 7/7 | 1207.83 | 126 |
| n01-02 | N01-claude-reference | 2 | executed | 7/7 | 989.67 | 99 |
| n01-02 | N01-codex-candidate | 2 | executed | 7/7 | 1065.76 | 93 |
| n01-02 | N01-codex-reference | 2 | executed | 7/7 | 1386.07 | 164 |
| n02-codex-02 | N02-codex-candidate | 1 | executed | 4/4 | 582.99 | 59 |
| n02-codex-02 | N02-codex-reference | 1 | executed | 4/4 | 758.73 | 62 |
| correction-n04 | N04-claude-candidate | 1 | executed | 4/4 | 291.2 | 35 |
| correction-n04 | N04-claude-reference | 1 | executed | 4/4 | 532.95 | 71 |
| correction-n04 | N04-codex-candidate | 1 | executed | 4/4 | 863.11 | 116 |
| correction-n04 | N04-codex-reference | 1 | executed | 4/4 | 808.67 | 40 |
| correction-n05 | N05-claude-candidate | 1 | executed | 5/5 | 512.59 | 48 |
| correction-n05 | N05-claude-reference | 1 | executed | 5/5 | 365.66 | 41 |
| correction-n05-lint | N05-claude-candidate | 1 | executed | 5/5 | 517.18 | 50 |
| correction-n05-lint | N05-claude-reference | 1 | executed | 5/5 | 362.48 | 48 |

Les durées excluent préparation des copies et correction externe ; campagnes
concurrentes, une génération par cellule. Aucun classement de vitesse. Les
incidents d’archivage sont conservés même lorsque le tour LLM a fini.

Revues : [N01](evidence/review-n01.json), [N02](evidence/review-n02.json),
[N03](evidence/review-n03.json), [N04](evidence/review-n04.json),
[N05](evidence/review-n05.json). N03 garde des réserves sur la rigueur des scripts
de test ; N05 initial garde une QA partielle faute de Ruff.
<!-- RESULTS END -->


## Validation de la version retenue

24 essais conservés : 20 parcours terminés avec oracles métier tous vrais,
4 incidents d'archivage conservés puis rejoués dans de nouveaux dossiers. Les
quatre N01 comportent chacun deux tours en contextes distincts. Ces nombres
ne sont pas un taux de qualité globale : réserves de QA, style et formulation
restent détaillées ci-dessus et dans les revues.

124 tests d'outillage réussis sous Python 3.10 et 3.12 ; graphe valide
(52 nœuds, 115 arêtes), syntaxe shell, Ruff bloquant et génération isolée conformes
(26 fichiers, deux blocs et pointeur personnel). Les nouveaux skills et les
rôles développeur/QA passent aussi la validation de format des skills.

La [revue de passation Claude](evidence/review-n01-claude.json) confirme D-03 et
la conservation exacte des anciennes preuves dans les deux variantes. Elle
conserve des réserves de formulation, dont « déjà livrée » malgré une portée
locale explicitée ailleurs. Aucune qualité rédactionnelle parfaite revendiquée.

La version retenue installe les corrections SQL/précision, les commandes
plan/start/improve, les contrôles de contexte/réception/clôture et l'assainissement
des instructions générées. Les optimisations sont retenues pour leur correction
fonctionnelle ; aucun gain général de vitesse ni supériorité de modèle annoncé.
