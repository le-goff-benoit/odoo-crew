# Réception indépendante — 2026-09-09

**Module :** aucun module custom ; configuration Studio de `x_lab_request`. **Série :** 19.0, lue dans `.odoo-agents/config:1`, confirmée par `decisions/2026-09-08.md:1` et `archives-execution/environment.json:4`. **Mode :** réception documentaire d’archives, contexte distinct des auteurs, sans nouvelle exécution Odoo.

**Verdict : REFUSÉ en l’état pour la certification intégrale « 10/10 » et la mémoire.** La règle D-22 et les succès techniques documentés sont conservés. Aucun comportement métier défectueux n’est démontré. La réserve principale porte sur une condition historique de C7 non attestée par les pièces ; les corrections de mémoire ci-dessous ne justifient pas de rejouer les scénarios encore valides.

| Axe | Verdict | Motif |
|---|---|---|
| Demande ↔ contrat | Conforme sur la règle et les exclusions ; portée des applications à expliciter | D-22 reprise exactement ; C8 choisit explicitement le constructeur comme objet des deux applications. |
| Contrat → preuves | Partiel | C1–C6 et C8–C10 étayés dans leur portée ; C7 prouve l’état final, pas à lui seul la conservation des ids initiaux. |
| Sources → mémoire | À corriger | Règle et absence de déploiement fidèles ; « critères 10/10 » trop affirmatif et impossibilité du lint généralisée depuis une limite locale. |

Les références `R/` désignent `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/` ; `S/` désigne `R/studio/`. Les numéros sont les lignes des fichiers reçus.

## Demande et contrat

- **Objet, acteur et canal.** `demande.md:1` demande « Ajoute seulement l'indicateur booléen stocké x_studio_needs_review » sur le modèle existant, « en voie Studio », avec pack versionné et scénarios RPC rejouables. `decisions/2026-09-08.md:1` attribue D-22 à Nora Petit, coordinatrice fictive, et situe tous les tests sur la copie synthétique locale 19.0. `R/revue_fonctionnelle.md:8–10,69,83–85` conserve cette opération et ce canal. Le contexte `studio=True`, `readonly=True`, l’état `manual` et le relevé d’XML-ID sont des choix techniques cohérents avec un indicateur calculé Studio, pas de nouvelles règles métier.
- **Formule et bornes.** La décision dit « x_studio_days >= 7 ET x_studio_kind = 'rental' » et « Les prêts ('loan') sont exclus, même à 7 jours ou plus » (`decisions/2026-09-08.md:1`). La formule de `R/revue_fonctionnelle.md:38`, les bornes 6/7 et les exclusions aux lignes 40–45 reprennent exactement ces obligations. D-21 à 5 jours est explicitement remplacée. C2–C6 déclinent la formule et ses deux dépendances.
- **Cas ajoutés.** Genre vide, durée zéro ou négative (`R/revue_fonctionnelle.md:49–53`, C5 ligne 96) sont des conséquences cohérentes de la conjonction D-22 sur les champs décrits. Ils sont présentés comme hypothèses de la revue, sans ajouter de validation de saisie. Aucun nouvel accord humain n’est documenté pour eux ; il n’est pas nécessaire pour conserver ce résultat directement déduit de la formule.
- **Existant et effets interdits.** « Les champs existants ne sont pas renommés ni recréés », « pas d'automatisation d'envoi ni changement des droits » (`decisions/2026-09-08.md:1`) correspondent à `R/revue_fonctionnelle.md:25–27,57–58,87–88,98`. « Aucun écran », « Pas de module custom et pas de déploiement » et « release ouverte » (`demande.md:1`) restent respectés dans le périmètre déclaré ; la release porte toujours son marqueur d’ouverture (`R/README.md:1–7`). Aucun contrôle navigateur, déploiement ou nouvelle recette complète n’est exigible pour cette réception sur pièces.
- **Deux applications : opération exacte.** La demande dit « vérifie deux applications sans doublon » (`demande.md:1`), sans nommer explicitement `odoo_pack.py apply`. C8 contractualise « Le script de construction est idempotent » (`R/revue_fonctionnelle.md:99`). C’est un choix technique explicite. Les preuves vérifient deux passages de ce constructeur, pas deux applications du pack. Cette portée doit rester visible ; si l’intention était de vérifier le pack lui-même, elle reste à clarifier et n’est pas démontrée. Je ne transforme pas cette ambiguïté en constat certain d’échec du pack.

## Preuves et conditions composées

| Critère | Pièces examinées et opération attestée | Réception |
|---|---|---|
| C1 | `S/preuves/08_qa_etat_base.txt:11` contient boolean, store, readonly, compute, depends et manual ; `S/test_01_needs_review.py:57–70` vérifie leur conjonction, résultat `09_qa_scenario_rejeu.txt:2`. | Étayé. |
| C2 | Création rental/7 puis `read` serveur (`S/test_01_needs_review.py:82–88`) ; résultat `09_qa_scenario_rejeu.txt:3`. | Étayé, seuil inclus. |
| C3 | rental/6 et rental/30, deux valeurs vérifiées ensemble (`S/test_01_needs_review.py:90–94`) ; résultat `09_qa_scenario_rejeu.txt:4`. | Étayé pour les deux bornes. |
| C4 | loan/7 et loan/30 (`S/test_01_needs_review.py:96–100`) ; résultat `09_qa_scenario_rejeu.txt:5`. | Étayé pour les deux exclusions. |
| C5 | Genre absent/10, rental/0 et rental/−3 (`S/test_01_needs_review.py:102–107`) ; résultat `09_qa_scenario_rejeu.txt:6`. | Trois cas étayés, sans erreur. |
| C6 | Deux écritures successives sur days puis kind, chacune suivie d’une relecture (`S/test_01_needs_review.py:109–118`) ; « False → True → False » (`09_qa_scenario_rejeu.txt:7`). | Étayé pour les deux dépendances. |
| C7 | Trois champs et liens XML-ID présents à l’état final (`S/preuves/08_qa_etat_base.txt:8–16`) ; scénario aux lignes 120–137. | Partiel : voir B1. |
| C8 | « CRÉÉ » puis « INCHANGÉ », même id 3742 et même XML-ID (`S/preuves/02_build_application_1.txt:1–4`, `03_build_application_2.txt:1–4`), unicité finale (`09_qa_scenario_rejeu.txt:9`). | Étayé pour le constructeur et l’absence de doublon. |
| C9 | Export d’un objet (`S/preuves/05_pack_export.txt:1`), diff « 0 / 0 / 1 à créer / à modifier / inchangés » (`07_qa_pack_diff.txt:2`), pack JSON d’un champ avec référence au modèle existant, sans `unresolved` (`S/pack.json:7–51`). | Étayé. Un diff sans écriture n’est pas un apply. |
| C10 | XML-ID sous studio_customization dans `S/created.txt:1`, dans le relevé (`08_qa_etat_base.txt:18`), création avec contexte Studio (`S/build_01_needs_review.py:52,108–112`). | Étayé par la concordance contexte / résultat / artefact. |

Le bilan « 9/9 » comprend C1–C8 et le nettoyage, pas dix tests de critères (`S/preuves/09_qa_scenario_rejeu.txt:2–13`). C9 et C10 ont leurs autres pièces. Le rouge initial est l’absence du champ (`01_scenario_avant.txt:2–5`) : il discrimine cette absence, sans constituer à lui seul un test de mutation de chaque branche métier. Les assertions métier et leurs résultats verts apportent les preuves supplémentaires. Le nettoyage est attesté (`09_qa_scenario_rejeu.txt:10`, `08_qa_etat_base.txt:20`).

### B1 — Conservation des ids initiaux de C7 insuffisamment attestée

**Contrat :** « inchangés (mêmes ids, mêmes XML-ID lab_seed_*) » (`R/revue_fonctionnelle.md:98`). **Affirmation :** « x_name id 3734, x_studio_days id 3736, x_studio_kind id 3738 inchangés » (`.odoo-agents/flow-artifacts/lab-needs-review/coverage.json:95`).

**Ce que les preuves contrôlent :** `S/test_01_needs_review.py:124–135` construit `seed_map` et `by_id` depuis deux lectures de l’état courant puis vérifie que les liens courants concordent. Aucun id antérieur n’entre dans l’assertion. Le relevé `08_qa_etat_base.txt:8–16` est également final. La revue initiale (`R/revue_fonctionnelle.md:16–20`) nomme les XML-ID, sans relever les ids numériques initiaux.

**Contre-exemple documentaire :** un champ recréé sous le même nom, avec son XML-ID repointé vers son nouvel id, passerait cette assertion. Cela ne prouve pas qu’une recréation a eu lieu. Le constructeur reçu lit seulement les champs existants (`S/build_01_needs_review.py:84–93`) et limite sa création/écriture à l’indicateur (lignes 95–120), ce qui soutient la conformité de l’implémentation. Il ne remplace cependant pas la comparaison historique annoncée comme contrôlée.

**Suite justifiée :** rattacher un relevé initial daté et disponible, puis comparer les trois identités avec le relevé final. À défaut, qualifier C7 de partiellement attesté, retirer « critères 10/10 » et distinguer l’état final vérifié de la conservation historique inférée. Ne pas modifier silencieusement C7 pour l’adapter aux résultats. Une nouvelle lecture de l’état actuel ne reconstituerait pas les ids initiaux ; aucune nouvelle exécution Odoo n’est demandée dans cette réception.

## Mémoire : conserver et rectifier

**Éléments fidèles à conserver.** `.odoo-agents/PROJECT.md:7–10` garde la conjonction, le seuil inclus et l’exclusion des prêts. `.odoo-agents/JOURNAL.md:4,19` étiquette D-21 comme remplacée : il n’existe pas de règle active à 5 jours à effacer. Le journal dit « Rien de déployé » (ligne 17) et « Release ouverte » (ligne 25), conformément à la demande et à `R/qa.md:46–47`. Les scénarios établissent une validation locale sur le laboratoire décrit ; ils n’attestent ni livraison distante ni validation des droits d’un autre utilisateur.

**M1 — Rectifier la portée du bilan.** `.odoo-agents/JOURNAL.md:16–17` reprend « critères 10/10 », comme `R/qa.md:7,52` (« Aucun défaut introduit, aucun critère non satisfait »). Ces formulations doivent conserver les succès vérifiés mais porter la réserve B1. Proposition : « D-22 et les scénarios RPC documentés sont verts ; diff pack sans écart ; deux passages du constructeur sans doublon. C7 : cohérence des identités finales contrôlée, conservation des ids initiaux non comparée sur pièces. Aucun déploiement. Release ouverte. »

**M2 — Remplacer une généralisation d’outillage.** `.odoo-agents/PROJECT.md:16–17` écrit « Voie Studio = pas de module, donc pas de lint Ruff » et `.odoo-agents/JOURNAL.md:23` « Aucun lint Ruff possible sur un point Studio ». La source `R/qa.md:42–45` dit seulement que le lint **du banc** accepte un module et que Ruff n’est pas installé hors image QA. Une contrainte locale ne prouve pas une impossibilité générale de lint des scripts. Proposition : « Sur ce banc, Ruff n’a pas été exécuté ; py_compile est déclaré passé sur les deux scripts. Pour ce point Studio, les preuves fonctionnelles sont le diff du pack et les scénarios RPC. » Ce remplacement n’introduit pas d’obligation nouvelle de lint pour accepter le calcul Studio.

**M3 — Séparer conséquence de formule et décision humaine.** « hypothèse actée » et « D-22 muette » (`.odoo-agents/PROJECT.md:9–10`, `.odoo-agents/JOURNAL.md:20`) peuvent être précisés en « conséquences de la formule D-22 explicitées par la revue et couvertes par C5 ». Aucun arbitrage humain supplémentaire n’est fourni ; ne pas en inventer un. De même, la prédiction « Si la production en contient, l'application du pack les calculera de la même façon » (`R/revue_fonctionnelle.md:59–61`) reste une hypothèse hors du contrôle local sur modèle vide, pas un résultat de reprise démontré.

L’absence d’écran et le retour liste de `create` sont documentés dans leur contexte local ; leur réutilisation future doit préserver ce contexte. « Rejeu indépendant » dans `S/preuves/09_qa_scenario_rejeu.txt:1` atteste le titre d’un passage distinct, pas l’indépendance d’un second auteur : `LAB.md:2` demandait d’appliquer les rôles sans sous-agent. La présente réception est effectuée en contexte neuf ; elle ne réécrit pas cette provenance historique.

## Intégrité et clôture de cette réception

Vérifications locales effectuées : lecture des pièces ; validation de lecture JSON ; recalcul SHA-256 des huit artefacts distincts référencés par la couverture, tous concordants ; empreinte de la revue conforme au rapport (`6a737c51d5e92a4589ebba8938548bab2e08de1c5ba61eec1d58882760085909`) ; toutes les empreintes de preuves des événements du flow concordantes ; demande et décision conformes aux empreintes initiales de `archives-execution/environment.json` ; deux copies du rapport QA identiques. Ces contrôles attestent la cohérence des fichiers reçus, pas une nouvelle exécution ni une garantie externe d’authenticité des sorties historiques.

Le laboratoire est synthétique (`LAB.md:2,7`) ; ses sorties sont présentées dans le dossier comme celles d’exécutions historiques. Je ne les présente pas comme des essais rejoués ici. Aucun script d’archive, base, navigateur ou ancien processus n’a été relancé. Aucun fichier reçu ni flow historique n’a été modifié ; seul ce `reception.md` a été créé.

Pour lever le refus de certification intégrale : traiter B1 par une preuve historique disponible ou une qualification honnête du manque, remplacer les formulations M1/M2, et conserver explicitement la portée constructeur des deux applications. Les résultats D-22 valides restent acquis sur pièces ; ni développement correctif ni redémarrage du flow ne sont justifiés par cette réception seule.
