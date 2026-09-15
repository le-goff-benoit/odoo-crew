# Procédure — task-reception

Chargement conditionnel depuis le profil canonique. Les chemins `docs/…` et
`roles/…` sont relatifs à `~/.odoo19-agents/`.

Pour une revue dont la section « Critères d'acceptation » utilise les cases
`- [ ]`, active la réception structurée avant de consolider :
`odoo_flow.py bind-criteria <flow> --source <revue> --output <coverage.json> --owner <orchestrateur>`.
Le fichier produit conserve les critères originaux, initialement `missing`.
Renseigne `covered`, `partial`, `missing` ou `failed` d'après les preuves ;
`covered` exige toutes les conditions du critère. Chaque preuve porte `path`
(dans le projet) et `sha256`. Génère le verdict de réception depuis cette couverture :
`odoo_flow.py qa-report <flow> <jointure> --coverage <coverage.json> --outcome <pass|retry|blocked> --output <nouveau-rapport-qa.md> --owner <propriétaire-de-la-jointure>`.
Présente le rapport généré et le JSON à `complete --evidence` avec la même issue.
Si `qa.md` existe déjà, référence ce nouveau rapport depuis la section de tâche,
sans réécrire son verdict. Le rendu conserve les critères et les références ;
les notes libres ne deviennent pas des attestations de build ou d'environnement.
Si les preuves ont changé, régénère la couverture et un nouveau rapport ;
un constat libre du manque permet toujours `retry` ou `blocked` sans le rapport périmé.
Le flow refuse `pass` si la couverture est absente, partielle ou modifiée ;
`retry` et `blocked` restent accessibles. Ce garde ne juge pas le sens des
preuves : un statut `covered` doit toujours être justifié par leur contenu.
Les formats et limites sont dans `docs/QA_COVERAGE.md` du référentiel.

**Réception de la demande et de la mémoire avant `pass`.** Prépare deux fichiers
neufs contenant les versions complètes proposées de `PROJECT.md` et `JOURNAL.md`
(contenu existant conservé, corrections nécessaires et entrée de quinze lignes
au plus). Ne les publie pas encore. Lorsque les sous-agents sont disponibles,
sur une tâche directe ou un flow du plan équipé de la reprise de réception, active le garde
avec `odoo_flow.py prepare-reception <flow>` :
`--source` pour la demande originale et chaque décision applicable, `--spec`
pour la revue, `--evidence` pour la couverture et les fragments/logs QA,
`--scope` pour les répertoires de code concernés, puis
`--memory .odoo-agents/PROJECT.md=<proposition-project>` et
`--memory .odoo-agents/JOURNAL.md=<proposition-journal>`, `--output <nouveau-bundle>`
et `--owner <orchestrateur>`. Les chemins sont relatifs au projet ; le format
et un exemple complet sont dans `docs/TASK_RECEPTION.md` du référentiel.

Délègue une **nouvelle conversation** à `odoo-tester`, mode réception
documentaire, avec le bundle et un fichier de retour isolé. Ne réutilise pas
un agent auteur de la revue, de la QA ou de la mémoire et ne lui fournis pas
le verdict attendu. Ce relecteur confronte demande, contrat, preuves et mémoire
proposée ; il ne modifie aucun de ces fichiers. Joins sa réception JSON aux
preuves de `complete --outcome pass`, avec le rapport QA et la couverture.
Le garde contrôle les empreintes et la publication, pas la justesse du jugement
ni l'identité réelle du contexte : conserve aussi la trace de la délégation.

Sur défaut de preuve, utilise les issues `retry`/`blocked` existantes. Sur
défaut du texte proposé, corrige seulement ce texte puis prépare un nouveau
bundle et une nouvelle réception ; conserve les tests toujours valides.
Deux reprises au plus. Un contrat lié erroné exige une correction tracée et un
nouveau flow/contrat, pas son affaiblissement pour obtenir le vert. Une erreur
de transcription de l'agent n'exige pas une nouvelle permission ; une vraie
ambiguïté métier suit l'arbitrage déjà prévu. Sans mécanisme de délégation,
effectue cette relecture toi-même et annonce son caractère non indépendant ;
n'active pas le garde qui exige une réception indépendante.

Un ancien snapshot ne gagne pas silencieusement ces transitions. Avant sa première
publication mémoire, sans revendication active, `odoo_flow.py upgrade-recovery
<flow> --owner <orchestrateur>` installe uniquement le sous-graphe de reprise
prévu et conserve l'historique. Si le fichier de graphe historique a été remplacé,
fournis son archive exacte avec `--from-graph`. En cas de refus, lis sa cause ; ne modifie jamais
le JSON pour forcer la migration. La réception du plan reste applicable après
le flow ; ne crée pas un run extérieur pour contourner ses réservations.


Si une réception est liée, après `claim journal_task`, utilise
`odoo_flow.py publish-memory <flow> --owner <orchestrateur>`, puis
`complete journal_task --outcome done` avec la preuve de publication. La commande
vérifie toutes les pièces et les deux cibles avant d'écrire les propositions
approuvées. Après interruption, elle reconnaît chaque fichier encore à sa base
ou déjà publié : relance-la sous la même revendication, sans restaurer les anciennes
valeurs ni ajouter deux fois l'entrée du journal. Un changement d'owner passe par
`release --reason` puis `claim`, après constat d'arrêt de l'ancien exécutant.

Si une autre tâche a modifié la mémoire, conserve son travail et un constat isolé.
Termine le journal avec `--outcome retry --evidence <constat>`, puis revendique
`reception_recovery_gate`. Prépare deux nouveaux drafts à partir de la mémoire
courante en y conservant les contributions déjà publiées ; seuls les changements
de cette tâche s'y ajoutent. Prépare un nouveau bundle avec les mêmes sources,
spec, preuves et code, puis délègue une nouvelle réception documentaire. La nouvelle entrée mémoire conserve explicitement
le résultat déjà reçu, sa portée et ses limites : raconter la reprise ou dire
« preuve conservée » ne transmet pas que le contrôle a réussi ou échoué. Distingue
ce résultat acquis des étapes encore à venir. Le
relecteur compare aussi les bases mémoire figées aux propositions ; aucune fusion
sémantique n'est faite automatiquement. Le pass de cette porte retourne au journal
pour publication. Les anciens bundles et réceptions restent en historique.

Cette reprise ne revalide pas un code, une décision ou une preuve modifiés : dans
ce cas, ou après deux retours infructueux, choisis `blocked` avec un constat puis
termine `memory_task_blocked`. Le plan peut alors être rouvert avec une raison,
sans perdre l'ancienne tentative. Aucun test Odoo n'est à rejouer pour un simple
conflit de texte si ses preuves sont restées valables. Les points ci-dessous
décrivent le contenu préparé à l'étape 3 ; sans réception liée, écris-le ici.
