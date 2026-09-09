# Chaîne de développement Odoo — une demande, dans une release

Enchaîne les profils dans l'ordre logique sur une demande de développement,
**sans redemander l'autorisation entre les étapes**. La demande à traiter suit
cette consigne (ou est celle que l'utilisateur vient de formuler).

Référentiel commun dans `~/.odoo19-agents/` : `ODOO19_STYLE_GUIDE.md` (19.0),
`SERIES_MATRIX.md` (les autres séries, fait foi), `LESSONS.md`. Réponds en
français.

## Le principe : tâche légère, release lourde

Une demande de développement s'inscrit dans une **release** de changelog
(`changelog/AAAA-MM-JJ_NN_titre/`), qui regroupe les demandes d'une même
livraison. Pendant que la release est ouverte, chaque tâche reçoit une **QA de
tâche** proportionnée (lint des fichiers touchés, tests ciblés, installation
sur la base de QA). La **recette complète** — base neuve, suite entière, tours,
désinstallation, mise à niveau sur la copie du client, captures, guide,
communication — se joue **une fois, à la clôture de la release** (`/odoo-close`).
Cette chaîne ne clôture jamais une release : c'est un acte de l'humain.

Exception : une demande qui touche aux droits, à la comptabilité, à la
facturation ou aux données existantes est validée **immédiatement** au niveau
nécessaire (recette sur la copie du client comprise), release ouverte ou pas.

## Piloter le graphe

Le graphe exécutable est
`~/.odoo19-agents/workflows/odoo-workflow.json`. Après le briefing, ouvre un
run et enregistre le premier nœud :

```bash
FLOW=$(python3 ~/.odoo19-agents/scripts/odoo_flow.py start <racine> \
  --kind development --id <identifiant-court>)
python3 ~/.odoo19-agents/scripts/odoo_flow.py status "$FLOW"
python3 ~/.odoo19-agents/scripts/odoo_flow.py claim "$FLOW" briefing
python3 ~/.odoo19-agents/scripts/odoo_flow.py complete "$FLOW" briefing \
  --outcome development --evidence <fichier-du-briefing>
python3 ~/.odoo19-agents/scripts/odoo_flow.py ready "$FLOW"
```

Choisis `development_complex` seulement si l'analyse a réellement au moins
deux voies indépendantes utiles — standard ambigu, custom existant, copie
client à inventorier. Le graphe ouvre alors trois recherches en lecture seule,
puis une jointure de synthèse. Une demande triviale reste sur `development` :
créer trois agents pour économiser trente secondes coûte plus qu'il ne rapporte.

À chaque nœud :

1. affiche `status` au début d'une vague afin que l'humain voie la position,
   les agents actifs et les nœuds parallélisables ;
2. lis le profil de chaque nœud prêt, puis revendique les nœuds retenus avec
   `claim --owner <nom-explicite>` ; ne masque pas la sortie de la commande ;
3. exécute le rôle toi-même, ou délègue les nœuds d'une même vague quand ils
   sont indépendants et que cela améliore réellement délai ou qualité ;
4. donne à chaque agent le briefing déjà calculé, la demande, le chemin de la
   release, le mode du nœud et un fichier de preuve propre dans
   `.odoo-agents/flow-artifacts/<run>/<nœud>.md` ;
5. vérifie que le fichier de preuve existe, puis toi seul appelles
   `complete --outcome … --evidence <chemin>` ; si l'exécution s'arrête avant
   la preuve, rends le verrou avec `release --reason …` ;
6. laisse `complete` afficher la nouvelle position, puis recommence jusqu'à un
   terminal ou une porte humaine.

Le tableau de bord terminal fait partie du contrat d'orchestration. Il doit
montrer `ORCHESTRATEUR`, `AGENT · <profil>` ou `HUMAIN`, ainsi que `EN COURS`,
`PRÊT`, `ATTENTE HUMAINE` ou l'état terminal. Utilise un propriétaire stable et
lisible (`codex-odoo-tester-1`, `claude-odoo-analyst`, etc.) pour que la ligne
`EN COURS` identifie réellement l'exécutant. Le JSON (`--json`) est réservé à
l'automatisation, pas aux comptes rendus destinés à l'humain.

L'agent principal est le seul à modifier le fichier d'état, à arbitrer une
issue, à fusionner les fragments dans `revue_fonctionnelle.md` ou `qa.md`, et à
écrire le journal. Un agent délégué ne relance pas le graphe et ne délègue pas
à son tour. Au plus trois agents spécialisés travaillent en parallèle. Deux
agents ne modifient jamais le même module, la même base, le même pack Studio
ou le même document partagé.

Une porte humaine n'est jamais revendiquée. Après réception de la réponse,
consigne-la d'abord dans la revue ou le diagnostic, puis appelle `complete`
avec `--human-confirmed --evidence <fichier>`. Ce drapeau atteste seulement
que l'orchestrateur vient de recevoir la décision ; `odoo_instance.py` garde
ses propres confirmations obligatoires pour une écriture en production.

Si la délégation n'est pas disponible, applique le rôle indiqué toi-même. Les
preuves et les transitions sont identiques. **Les fichiers de la release sont
le canal de transmission** : `revue_fonctionnelle.md` → code → `qa.md` ; le
fichier de flow dit seulement où en est l'exécution.

## Étape 0 — Situer (une commande, non négociable)

```bash
python3 ~/.odoo19-agents/scripts/odoo_briefing.py <module_ou_projet>
```

Le briefing donne la série et son origine, la release ouverte et ses points, ce que
le projet sait déjà (métier, décisions, pièges), les dernières entrées du
journal, les leçons applicables et les formes attendues dans cette série. S'il
signale l'absence de `.odoo-agents/`, crée-le d'abord :
`~/.odoo19-agents/scripts/odoo_project_scan.py <racine_du_projet>`.

Annonce en une ligne : **projet, série, origine de la série, release ouverte ou
non, modules concernés**. Toutes les étapes suivantes travaillent dans cette
série.

```bash
RELEASE=$(~/.odoo19-agents/scripts/odoo-release.sh current <racine>)   # vide s'il n'y en a pas
```

**On n'ouvre pas de release avant le verdict de l'analyste.** Une demande qui se
règle par la configuration ou qui bute sur une question bloquante ne doit pas
laisser un dossier vide derrière elle. La revue s'écrit dans la release s'il est
déjà ouvert, sinon dans `<racine>/.odoo-agents/revue_en_cours.md`, que
l'étape 1 déplacera au bon moment.

**La demande arrive parfois en mail(s) `.eml`** — la demande d'origine du
client, souvent avec des captures. Ne la résume pas : verse-la telle quelle.

```bash
python3 ~/.odoo19-agents/scripts/odoo_mail.py <fichier.eml> [...]                 # lire d'abord
python3 ~/.odoo19-agents/scripts/odoo_mail.py <fichiers.eml> --release "$RELEASE"   # une fois la release ouverte
```

Il ajoute chaque mail à `demande.md` (expéditeur, date, objet, texte, fil dans
l'ordre chronologique) et range les pièces jointes dans `pieces/`. Les captures
sont des preuves à lire (`Read` sur le PNG) ; les documents du client
(tableurs, contrats, exports) sont marqués ⚠️ : ils ne se commitent pas sans
décision de l'humain. Tant que la release n'est pas ouverte, lis le mail sans
`--release` ; le versement se fait à l'ouverture.

Regarde **`inbox/`** : c'est là que l'humain dépose ce qu'il veut te confier —
une sauvegarde (`.zip`, `.dump`, `.sql`) ou des mails (`.eml`). Le briefing en
liste le contenu avec la commande qui va avec. Une sauvegarde plus récente que
la copie restaurée se restaure avant de continuer
(`odoo-restore.sh inbox/<fichier> --db <client>_test --force`, deux à dix
minutes selon la taille — annonce-le). Le dossier est ignoré par git.

Cherche aussi une **copie du client** (le briefing liste les bases du stack et
les instances déclarées). Elle sert aux trois étapes. Si elle manque et que la
demande touche des données existantes, demande-la à l'utilisateur dès
maintenant — sans bloquer la revue fonctionnelle.

## Étape 1 — Revue fonctionnelle (`odoo-analyst`)

Rôle : `~/.odoo19-agents/roles/functional-review.md`. Sa consigne lui donne
le briefing, la demande, et **le chemin où écrire la revue** :
`$RELEASE/revue_fonctionnelle.md` (section `## Point n` si la release en a déjà) ou
`.odoo-agents/revue_en_cours.md` s'il n'y a pas de release. Ses décisions durables
vont dans `PROJECT.md`.

Puis **décide, et annonce ta décision** :

| Issue de la revue | Suite |
|---|---|
| Verdict **ÇA EXISTE** — le standard de la série (ou la base du client) couvre le besoin | **STOP après enregistrement.** Ouvre la release s'il n'existe pas, ajoute la demande à `demande.md` et un point « configuration » au suivi, déplace la revue dans la release. Explique la configuration à faire, ne développe pas. |
| Au moins une **question bloquante** | **STOP.** Livre les questions. N'invente pas la réponse. Pas de release : la revue attend dans `revue_en_cours.md`. |
| Contradiction **bloquante** non levable | **STOP.** Livre la revue avec le risque. Pas de release. |
| Spec saine (y compris demande triviale expédiée en une ligne) | **CONTINUE** : ouvre la release s'il n'existe pas (titre court, orienté résultat métier), copie la demande **telle quelle** dans `demande.md`, ajoute le point, déplace la revue dans la release. Puis étape 2. |

La transition `module_high_risk` est obligatoire si la tâche touche aux
droits, à la comptabilité, à la facturation ou aux données existantes. Elle
active un nœud d'implémentation distinct dont la seule sortie verte ouvre les
trois voies QA, dont la copie client. Le niveau de risque ne peut ainsi pas se
perdre dans une reprise ou après un ticket de support.

```bash
RELEASE=$(~/.odoo19-agents/scripts/odoo-release.sh open <racine> "<titre>")      # si aucune release
~/.odoo19-agents/scripts/odoo-release.sh add "$RELEASE" "<point en une ligne>"
mv <racine>/.odoo-agents/revue_en_cours.md "$RELEASE/revue_fonctionnelle.md"   # ou concaténation si le fichier existe
```

Ne t'arrête pas pour une contradiction majeure ou mineure : consigne-la comme
hypothèse retenue dans la spec, et continue.

### Entrée par un ticket de support

Si la demande est un diagnostic d'`odoo-support` (fichier
`changelog/<release>/support/…_ticket-NNNN.md`) classé **bug**, avec une cause
prouvée et un **test rouge** dans le module : saute l'étape 1. Le diagnostic est
la spec — correction attendue, critère d'acceptation « le test passe ». Ligne
d'état : `[1/4 analyst] sauté — diagnostic support #NNNN, cause prouvée, test rouge`.
Exceptions qui ramènent l'analyste : correction qui touche aux droits, à la
compta, à la facturation ou aux données existantes ; diagnostic sans test
rouge ; ticket classé « évolution déguisée ».

### Reprise après une question bloquante

Quand l'humain répond dans la conversation, **on ne rejoue pas l'étape 1**.
Écris sa réponse dans la revue (section « Hypothèses retenues » → devient
« Décisions »), puis applique la ligne CONTINUE du tableau : ouverture de la release,
demande, point, déplacement de la revue, étape 2. Si la réponse change le
périmètre au point d'invalider la revue, dis-le et relance l'analyste sur le
seul point qui change.

## Étape 2 — Implémentation (`odoo-developer` ou `odoo-studio`)

La revue a choisi la **voie** (section « Voies possibles ») : module custom →
`odoo-developer` (rôle `implementation.md`) ; configuration en base →
`odoo-studio` (rôle `studio.md`, livrable `changelog/<release>/studio/` :
scripts de construction, scénarios RPC, `pack.json`). Le point de la release
est préfixé `[studio]` dans le second cas. Une limite de Studio découverte en
cours de route remonte à l'humain avant tout contournement.

Rôle développeur : `~/.odoo19-agents/roles/implementation.md`, avec la spec de
`revue_fonctionnelle.md` comme périmètre — ni plus, ni moins. Il livre le code,
les tests, et le lint vert sur les fichiers touchés :

```bash
~/.odoo19-agents/scripts/odoo-lint.sh --changed "$(cat $RELEASE/.base)" <module>
```

La version du manifest **ne bouge pas à chaque tâche** : elle s'incrémente une
fois par release, à la clôture — sauf si la release est constituée d'une seule tâche à
livrer tout de suite, auquel cas le développeur l'incrémente maintenant.

## Étape 3 — QA de tâche (`odoo-tester`, mode tâche)

Rôle : `~/.odoo19-agents/roles/qa-review.md`, **mode tâche**. Le graphe sépare
la relecture/lint et l'installation/tests ciblés dans deux fragments qui
peuvent être produits en parallèle. Pour le niveau renforcé, une troisième
voie valide la copie client. La jointure contrôle tous les fragments ;
l'orchestrateur écrit ensuite le verdict unique dans `qa.md`.

Pour une revue dont la section « Critères d'acceptation » utilise les cases
`- [ ]`, active la réception structurée avant de consolider :
`odoo_flow.py bind-criteria <flow> --source <revue> --output <coverage.json> --owner <orchestrateur>`.
Le fichier produit conserve les critères originaux, initialement `missing`.
Renseigne `covered`, `partial`, `missing` ou `failed` d'après les preuves ;
`covered` exige toutes les conditions du critère. Chaque preuve porte `path`
(dans le projet) et `sha256`. Présente ce JSON avec `qa.md` à `complete --evidence`.
Le flow refuse `pass` si la couverture est absente, partielle ou modifiée ;
`retry` et `blocked` restent accessibles. Ce garde ne juge pas le sens des
preuves : un statut `covered` doit toujours être justifié par leur contenu.
Les formats et limites sont dans `docs/QA_COVERAGE.md` du référentiel.

```bash
export ODOO_ADDONS_DIR=<répertoire contenant le module>
~/.odoo19-agents/scripts/odoo-test.sh <module> --quick --tags /<module>:<TestClasse>   # un seul chargement
```

Pour un point `[studio]`, la QA de tâche est : `odoo_pack.py diff` sans écart
sur la copie, scénarios `studio/test_<point>.py` verts, écran vérifié
(`odoo-shot.sh`) si une vue change — pas de `odoo-test.sh`.

Le testeur décide en plus d'un **point de contrôle** (suite complète du module,
base chaude) quand le diff croise un autre point de la release, touche un
modèle partagé, ou tous les trois points — en arrière-plan sur Claude, lu à la
tâche suivante. Les durées affichées (`⏱`) alimentent tes lignes d'état.

Le QA écrit son verdict dans `$RELEASE/qa.md` (une section datée par tâche) et
vérifie explicitement chaque critère d'acceptation de la spec. Il marque le
point dans le suivi de la release :

```bash
~/.odoo19-agents/scripts/odoo-release.sh done "$RELEASE" <n°> "<verdict — test ciblé>"
```

**Interdit à ce stade : captures, guide, communication client, skill
`camptocamp-docs`.** C'est la clôture (`/odoo-close`) qui les produit, une fois
pour tout la release, sur l'état qui part réellement. Si un écran change, note-le
dans « Ce que l'utilisateur verra » de la revue, c'est ce que la clôture lira.
Seule exception : l'humain le demande explicitement.

## Étape 4 — Capitaliser (deux minutes, ne se saute pas)

Une chaîne qui ne laisse pas de trace oblige la suivante à tout redécouvrir.

1. **Entrée de journal** dans `<projet>/.odoo-agents/JOURNAL.md` — **quinze
   lignes au plus** : date, demande, fait, verdict, **Appris**, reste ouvert.
   Le détail est dans la release ; le journal est la mémoire courte, pas l'archive.
2. **Fiche projet** : si le métier ou un piège durable a été éclairci, complète
   `PROJECT.md` (« Compréhension métier », « Décisions actées », « Pièges
   connus »).
3. **Candidate à `LESSONS.md`** : si l'incident dépasse ce projet — une règle
   fausse dans le guide, un motif de lint absent, une confusion de série — dis-le
   dans le compte-rendu, section « Reste à faire ». C'est `/odoo-feedback` qui
   promeut.

## Boucle de reprise

Si la QA remonte un **critère d’acceptation non satisfait, une régression introduite,
un contrôle obligatoire manquant ou une anomalie bloquante** : retour à l’étape 2 pour les
corriger, puis nouvelle QA. **Deux reprises au maximum.** Au-delà, arrête et
livre l'état réel avec ce qui reste rouge — ne boucle pas indéfiniment et ne
masque pas un échec.

La gravité ne dispense jamais de satisfaire les critères convenus. Seules la dette
antérieure explicitement identifiée et les améliorations facultatives peuvent rester
pour arbitrage dans `qa.md`, sans masquer un défaut introduit.

## Ce que l'utilisateur voit pendant la chaîne

Il ne voit ni les sous-agents ni les outils : il voit **tes lignes d'état** et
le compte-rendu. À chaque franchissement d'étape, une ligne, toujours de la
même forme, sur Claude comme sur Codex :

```
[0/4 briefing]  rubixcomm_odoo · 19.0 (config) · release ouverte 2026-09-04_01 · copie client : rubix_20260904
[1/4 analyst]   PARTIEL — le standard notifie, l'historique SAV manque → je continue
[2/4 developer] 3 fichiers, 4 tests · lint --changed : 0 erreur · ~2 min de QA Docker à suivre
[3/4 tester]    VALIDÉ — install/update OK, 4/4 tests, critères 5/5 → journal
[4/4 journal]   entrée écrite · PROJECT.md : 1 piège ajouté
```

Règles de la ligne : le verdict en majuscules quand il y en a un, la raison en
une proposition, la flèche vers ce qui suit. **Avant tout ce qui dure** (tests
Docker, restauration, recette), annonce-le avec une durée approximative :
un silence de trois minutes sans explication est une panne pour celui qui lit.
Aucun extrait de log, aucune sortie d'outil dans la conversation : un chemin
de fichier suffit.

Emploie le **mot du projet** pour la release : `lot_label` dans
`.odoo-agents/config` (« release » chez NECA), « release » par défaut. Le briefing
et `odoo-release.sh` le lisent.

## Compte-rendu final (court : le détail est dans la release)

La section **« À décider »** vient en premier quand elle n'est pas vide ; elle
disparaît sinon. C'est la seule chose que l'humain doit lire s'il ne lit qu'une
chose.

```markdown
# <titre de la demande>

**Projet** <nom> · **série** <X.Y> · **release** `<dossier>` (point n°<n>) · **modules** <…>

## À décider
<questions bloquantes, arbitrages, hypothèses posées faute de réponse — ou section absente>

## Cadrage
<verdict standard, hypothèses retenues, hors périmètre — trois lignes>

## Réalisation
<fichiers créés / modifiés, choix techniques notables>

## QA de tâche
| Contrôle | Résultat |
<lint --changed, install/update, tests ciblés n/n>
| Critère d'acceptation | Couvert par | État |

## Reste à faire
<anomalies non corrigées, leçon candidate>

## Release
<n> point(s) dans la release, <m> réalisé(s). Clôture et recette complète : `/odoo-close`.
```

## Règles

- Une ligne d'état par étape (forme ci-dessus), jamais de sortie d'outil brute.
- Annonce la série cible dès l'étape 0 et n'en change plus en cours de route.
- Un arrêt aux étapes 1 ou 3 est un résultat légitime, pas un échec : dis pourquoi.
- Ne déclare jamais « testé » ce qui n'a pas été exécuté. Si Docker n'est pas
  disponible, livre les étapes 1 et 2 et dis explicitement que l'étape 3 est partielle.
- Ne lis pas les logs Odoo en entier : `odoo-test.sh` en extrait les erreurs et
  termine par une ligne `RECETTE …`. Va dans le log complet seulement pour
  localiser une erreur déjà signalée.

## Plan et passation durable

Si la release a un `plan.json`, utiliser `/odoo-start` et son flow de tâche
existant. Pour préparer plusieurs demandes sans lancer leur exécution, utiliser
`/odoo-plan`. Les contrats de ces commandes sont dans `docs/RELEASE_PLAN.md`.

Une décision reçue pendant le travail porte sa source, ce qu'elle remplace et
les tâches concernées. Actualiser la revue et la mémoire, invalider les preuves
affectées, transmettre le complément aux rôles concernés. À la fin de tâche,
laisser un fragment de consolidation ou expliquer pourquoi aucune connaissance
durable ne change ; un journal simplement présent ne prouve pas cette opération.
