# Comparaison bornée : délégation disponible ou solo

Proposition de conception indépendante, sans exécution de candidat. Référence annoncée : `f6ea0b6`. Sources de méthode consultées : `AGENTS.md`, `docs/IMPROVEMENTS.md`, `docs/quality-lab/OPERATIONS.md`, skill `odoo-improve`.

## Question et traitement

Mesurer, pour trois demandes figées, ce que change la **possibilité de déléguer** sur la qualité livrée, le temps écoulé, les tokens et les reprises. S applique seul tous les rôles requis ; D peut employer zéro, un ou deux enfants, sans obligation d'en créer. Le prompt D expose cette autorisation ; le prompt S l'interdit. Toute autre instruction, documentation, outil métier, donnée initiale, modèle, effort et sortie attendue est identique.

Le résultat principal suit l'affectation S/D, même lorsque D choisit zéro enfant. Les résultats avec enfants sont une analyse descriptive séparée, sans reclasser les D sans enfant en S. Ne pas changer les exigences de QA de production : l'auditeur externe commun appartient au banc et ne remplace pas les validations normalement requises par le dispositif.

Quatre slots totaux : orchestrateur du banc + participant du run + au plus deux enfants. Aucun concepteur ni auditeur ne reste actif pendant un run. Aucun CLI modèle payant. Enfants de même modèle et effort que le participant ; pas de petits modèles substitués. Choisir un contexte neuf par run et ne transmettre que le paquet candidat commun, sans historique de campagne ni critères cachés. Le parent du run conserve la responsabilité de la synthèse ; les enfants reçoivent une propriété de fichiers ou une mission de lecture compatible.

## Trois cas et contrat commun

| Cas | Demande | Sortie et preuve exigées dans les deux bras |
|---|---|---|
| C1 | Question fonctionnelle simple, série et règle métier explicites, réalisable en standard ou décision argumentée | Réponse concise, référence vérifiable dans les sources pertinentes, limites et éventuelle question réellement bloquante ; aucun code gratuit |
| C2 | Diagnostic/synthèse avec indices distribués entre deux pistes indépendantes, puis une contradiction à résoudre au rassemblement | Cause étayée, distinction fait/hypothèse, résolution de la contradiction, impact et contournement ; références précises aux deux pistes |
| C3 | Petit correctif réel sur module synthétique et copie DB jetable ; même règle métier à faire respecter par plusieurs canaux | Correctif, tests ciblés, preuve ORM et RPC (et interface si le contrat l'exige), absence de régression positive, install/update, lint touché, bilan honnête ; critères multicanaux fixés avant réponses |

Le concepteur de C3 conserve demande détaillée, réalisation témoin, défauts injectés et critères hors de l'exposé aux candidats jusqu'au gel de la politique. La structure du cas peut être connue ; pas sa solution. Même paquet figé communiqué ensuite à S et D. Réserver signifie **non utilisé pour ajuster**, pas simplement non exécuté en premier. Après ouverture de ses résultats, C3 n'est plus un cas inédit.

## Gel et ordre

Créer un manifeste daté avec hash du dépôt, des prompts commun/S/D, des paquets, de la grille, des scripts/oracles, image Odoo, série, configuration modèle/effort et timeouts. Enregistrer séparément le modèle demandé et celui réellement observé ; si ce dernier n'est pas exposé, l'indiquer. Préparer des workspaces et clones DB équivalents, avec contrôles de départ identiques ; gabarit commun préparé avant chrono. Pas de modifications d'instructions à l'intérieur d'une paire.

Six runs primaires strictement sériels : **C1-S, C1-D, C2-D, C2-S, C3-S, C3-D**. L'ordre des traitements est contrebalancé autant que trois paires le permettent (2 contre 1), sans prétendre à un équilibre parfait ou à une randomisation. Aucun retour d'audit entre les membres d'une paire. Idéalement aucune modification de politique pendant les six runs ; tout changement ultérieur ouvre une version distincte.

Limiter avant départ les runs à 10 min pour C1, 15 min pour C2, 25 min pour C3, sauf ajustement explicite au gel justifié par la préparation déterministe. Même plafond au sein d'une paire. Le dépassement reste un run conservé, avec artefacts partiels ; séparer timeout du transport et défaut métier. Une panne d'infrastructure ne devient pas échec métier et ne disparaît pas du journal.

## Mesure

Horodatage monotone dès envoi du paquet au participant jusqu'à sa sortie finale, enfants terminés et artefacts déposés. Ce temps inclut appels d'outils, coordination, attente, tests choisis et reprises propres au participant ; exclut préparation commune et audit posthoc. Rapporter aussi préparation et audit séparément. Employer les mêmes conditions de cache préchauffé pour les deux bras, ou constater la différence ; ne pas vider un cache pour un seul bras.

Conserver événements de création/fin d'enfants, propriété des missions et intervalles d'activité. Déclarer nombre d'enfants, chevauchement réellement observé, temps d'attente, appels métier et conflits de ressources. Ne pas confondre deux agents existants avec deux agents travaillant simultanément. Sérialiser les opérations partageant DB/module ; le parallélisme utile porte sur ressources indépendantes.

Tokens = somme des compteurs natifs du participant **et de tous ses descendants**, avec catégories entrée/cache/sortie/raisonnement telles qu'exposées. Ne pas additionner des compteurs cumulatifs de plusieurs événements. Comptabiliser contexte répliqué et coordination. Budget/usage de l'orchestrateur et de l'auditeur séparés. Si les compteurs complets ne sont pas accessibles, écrire « tokens non mesurés » ; une estimation depuis caractères reste explicitement une estimation, jamais une économie constatée. Un coût manquant n'est pas zéro.

Reprises : distinguer (a) corrections spontanées avant final, (b) réparations après retour de l'auditeur, (c) incidents du banc. Compter les cycles avec leur motif, temps et tokens ; conserver les premières sorties. Le résultat primaire est celui livré sans retour externe. Toute qualité obtenue après retour est un résultat secondaire.

## Audit commun et calibration

Après gel de chaque paire, auditeur en contexte neuf, identités opaques et ordre de présentation fixé indépendamment ; mêmes critères pour S et D, hors chrono des deux bras. Il voit contrat, dossiers utiles, artefacts et preuves, pas l'étiquette ni les traces de délégation lors de la notation qualité. Une seconde passe des traces vérifie exécution, indépendance et honnêteté sans modifier subrepticement la grille. Les désaccords critiques sont arbitrés et avis initial conservé.

Grille 10 points : exactitude métier 0–4 ; couverture du contrat 0–2 ; preuves vérifiables 0–2 ; synthèse utile et limites honnêtes 0–2. Les ancrages spécifiques sont écrits avant les réponses. Critique = règle métier fausse, perte d'invariant ou de données, contournement des droits, canal exigé non protégé, ou succès annoncé sans preuve valide. Un critique interdit le succès même avec 9/10. Une réponse courte ne perd aucun point si elle couvre le contrat.

Calibrer hors runs avec une réponse/réalisation témoin correcte et au moins un mutant critique par dimension essentielle : décision standard erronée pour C1 ; synthèse ignorant l'indice contradictoire pour C2 ; canal secondaire contournable et positif valide pour C3. Exiger témoin accepté et mutants critiques refusés avant les runs. Les contrôles runtime de C3 évaluent effectivement le code conservé, sans réparation manuelle. Si l'oracle est faux, corriger séparément, re-noter toutes les sorties affectées avec le même oracle et conserver les verdicts initiaux.

## Révisions et décision

Au plus deux révisions de politique pour un défaut critique établi. Pas de révision pour une simple petite différence de score ou de vitesse. Une révision n'écrase aucun run primaire ; rejouer **la paire complète affectée** avec nouveaux contextes et état initial, puis une contre-épreuve réservée. Si C3 a déjà été ouvert, il faut un nouveau cas inédit pour revendiquer une contre-épreuve ; sinon qualifier seulement la réparation du défaut connu. Arrêter après deux corrections sans progrès. Un budget de reprises épuisé ne rend pas une branche verte.

Seuils descriptifs préenregistrés : acceptable = zéro critique, tous critères obligatoires satisfaits et score ≥ 8/10. Pour proposer une autorisation bornée de déléguer sur tâches à pistes indépendantes : D acceptable sur les trois cas, aucun score D inférieur à S, aucun critère obligatoire perdu ; sur C2, D doit employer un enfant utile avec chevauchement observé et gagner au moins 20 % de temps ; tokens D/S ≤ 1,5 si complets ; nombre de réparations externes D ≤ S. C1 ne doit pas montrer de surcoût de temps > 25 % causé par une délégation inutile. Si tokens indisponibles, la condition d'économie de ressources est non évaluée : statut au plus expérimental, pas adoption fondée sur les coûts.

Ces seuils sont des règles de décision locales, pas des intervalles de confiance. Publier mesures par paire et différences relatives ; pas de test de significativité sur trois cas ni classement général. Si qualité maintenue mais vitesse/coût non concluants, conserver délégation **facultative et expérimentale**, sans promesse de gain. Ne pas supprimer la relecture indépendante de production à partir de cette expérience.

## Risques et conditions bloquantes avant exécution

- Un prompt D qui suggère explicitement les deux pistes alors que S ne les reçoit pas confond délégation et aide à la résolution : exposer la même structure du dossier aux deux.
- Les profils actifs du home peuvent évoluer après le gel : snapshotter leur contenu réellement transmis, pas seulement le SHA annoncé du dépôt.
- Workspaces partagés et grille accessible aux candidats empêchent de promettre un masquage technique ; isoler les ressources si possible, sinon déclarer le masquage coopératif et vérifier les traces d'accès.
- L'ordre fixe, la charge machine, les caches et la variance modèle limitent l'attribution causale. Une paire par type n'est pas une estimation stable de la moyenne du type.
- Bloquant pour l'affirmation « même modèle/effort » : impossibilité de figer les paramètres transmis aux participants/enfants ; la visibilité du modèle effectif reste une limite distincte.
- Bloquant pour C3 : pas de clones réellement indépendants, pas d'oracle calibré ou pas de canal runtime requis accessible. Ne pas substituer silencieusement un exercice documentaire.
- Non bloquant pour exécuter, bloquant pour conclure aux économies : absence de tokens natifs complets. Aucun secret, compte client ni écriture de production n'est nécessaire.
