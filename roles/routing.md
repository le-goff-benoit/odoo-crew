Sources Odoo en lecture seule : `~/odoo-sources/{14.0,17.0,18.0,19.0,19.1,19.4}`
(+ `-enterprise`). Ne jamais y écrire : tout code va dans le module custom du projet.

Référentiel `~/.odoo19-agents/docs/reference/` : `ODOO19_STYLE_GUIDE.md` (ligne éditoriale,
décrit la **19.0**), `SERIES_MATRIX.md` (ce qui change par série, **fait foi**
sur le guide), `PLATEFORMES.md` (Odoo.sh / Online / on-premise / Docker, fait
foi sur déploiement et restauration), `LESSONS.md` (les erreurs déjà payées).

## La série d'abord, le briefing ensuite

Le parc est mélangé (17.0, 18.0, 19.0, saas~19.1, saas~19.4). Écrire du 19.0
dans un module 18.0 le casse ; le relire avec les règles 19.0 remonte des
anomalies fausses. **Avant toute lecture ou écriture de code Odoo**, une commande :

```bash
python3 ~/.odoo19-agents/scripts/odoo_briefing.py <module_ou_projet>
```

Elle donne la série (de `.odoo-agents/config`, sinon du manifest) et tout ce
que le projet sait déjà : `PROJECT.md` (relevé + compréhension métier,
décisions actées, pièges connus), dernières entrées de `JOURNAL.md`, release de
changelog ouvert, leçons applicables. Si `.odoo-agents/` manque :
`~/.odoo19-agents/scripts/odoo_project_scan.py <racine>`.

## Orchestration en graphe

Les chaînes Odoo suivent le graphe déclaré dans
`~/.odoo19-agents/workflows/odoo-workflow.json`. L'agent principal en est
l'orchestrateur et l'unique écrivain : il ouvre l'état avec `odoo_flow.py
start`, demande les nœuds prêts avec `ready`, revendique un nœud et ses verrous
avec `claim`, puis enregistre le résultat avec `complete` et une preuve réelle.
Les revendications sont contrôlées entre les runs d'un même projet et les
mises à jour d'état sont sérialisées entre processus. L'état local vit dans
`<projet>/.odoo-agents/flows/` ; les livrables qui font foi restent dans la
release et dans `JOURNAL.md`.

Dans le terminal, affiche `odoo_flow.py status <flow>` au début de chaque vague
et conserve la sortie humaine de `claim` et `complete`. Elle indique la
position, les rôles actifs, les propriétaires, les prochaines étapes, le
parallélisme et les attentes humaines. Donne à `--owner` un nom explicite qui
identifie Claude/Codex et le rôle ; n'utilise `--json` que pour une lecture
machine.

Quand plusieurs nœuds prêts sont dans la même vague et que leurs verrous sont
compatibles, l'orchestrateur peut les déléguer en parallèle aux profils
indiqués par le graphe. Il ne délègue pas une étape courte par principe et ne
fait jamais écrire deux agents dans le même module, la même base ou le même
livrable partagé. Les agents spécialisés rendent une preuve isolée ;
l'orchestrateur seul fusionne les fragments dans la revue, `qa.md`, la recette
ou le journal. Une porte humaine ne se franchit qu'avec `--human-confirmed` et
le chemin du fichier où la décision est consignée ; les protections de
`odoo_instance.py` restent obligatoires pour toute production.

## Aiguillage

| Nature de la demande | Réponse |
|---|---|
| **Fonctionnel pur** — comprendre, cadrer, challenger, chiffrer, « Odoo sait-il faire… », arbitrer une règle métier | `odoo-analyst` **seul**, aucun code |
| **Ticket de support** — « l'utilisateur voit… », « ça ne marche plus », « pourquoi… », un numéro de ticket | `odoo-support` **seul** : diagnostic prouvé, classement, contournement, réponse client ; passe la main selon le verdict (voir ci-dessous) |
| **Développement ou configuration** — créer, modifier, corriger, étendre (module ou Studio) | **`/odoo-new`** : fonctionnel → `odoo-developer` **ou** `odoo-studio` selon la voie choisie par l'analyste → QA de tâche → journal, dans la release ouverte (ouverte au besoin) |
| **Correctif express local** — résultat explicite, zone connue, sans schéma, droits, dépendance, migration, données ni calcul financier | **`/odoo-express`** : briefing → qualification courte → modification directe → QA ciblée → journal → push si demandé ; bascule vers `/odoo-new` si le périmètre s'élargit |
| **Préparation multi-demandes** — préparer et découper une release | **`/odoo-plan`** : analyse globale, tâches et critères ; ne démarre pas le dev |
| **Estimation et suivi du temps des agents** — chiffrer les durées, comparer prévu/réalisé | **`/odoo-estimate`** : minutes par tâche et agent, hypothèses ; bilan de clôture temps/jetons/coûts IA sourcés, sans barème client |
| **Exécution / reprise du plan** — lancer les tâches préparées | **`/odoo-start`** : dépendances, flows, preuves et consolidation |
| **Clôture / livraison** — « ferme la release », « prépare la livraison », « recette complète » | **`/odoo-close`** : recette entière, doc.md métier, consolidation, README ; guide et communication sur demande |
| **Validation seule** — « relis », « valide », « ce module est-il propre ? » | `odoo-tester` **seul** (mode release) |
| **Documentation** — guide utilisateur ou de décision, communication client, sur demande explicite | skill **`camptocamp-docs`** (sinon, c'est `/odoo-close` qui la produit) |
| **Environnement** — « déclare la prod / le staging », « as-tu accès à… » | **`/odoo-env`** : dialogue du bureau, trousseau, vérification ; aucun secret dans la conversation |
| **Remarque à retenir** — « pas comme ça », « chez ce client… » | **`/odoo-feedback "<remarque>"`** : journal du projet, leçon candidate |
| **Banc neutre et ajustement des agents/skills** | **`/odoo-improve`** : essais → correction → contre-épreuve → adoption dans les profils |
| **Amélioration du dispositif** — « qu'a-t-on appris », « le guide est-il à jour » | **`/odoo-feedback`** sans argument |

Règles :

- La chaîne se déroule **sans redemander l'autorisation entre les étapes** ;
  elle ne s'arrête que si le standard couvre le besoin, sur question bloquante,
  ou QA rouge après deux reprises.
- Le flux **`/odoo-express`** reste exécuté par l'orchestrateur, sans sous-agent.
  Une retouche de présentation d'un document financier est admissible lorsque
  les montants et règles restent inchangés. Les corrections liées partagent la
  même entrée de changelog express au lieu de créer un dossier par itération.
- **Tâche légère, release lourde** : pendant une release ouverte, chaque tâche reçoit lint
  des fichiers touchés, install/update et tests ciblés ; la recette complète
  se joue une fois, à la clôture. Une tâche qui touche aux droits, à la compta,
  à la facturation ou aux données existantes se valide tout de suite.
- **Une demande reçue en `.eml`** se verse telle quelle dans `demande.md`
  (`scripts/odoo_mail.py`), pièces jointes dans `pieces/` ; jamais résumée.
- **Studio ou module** : l'analyste choisit selon le profil du projet (aucun
  module ou Studio existant → Studio ; modules seuls → module ; Odoo Online →
  Studio) sauf demande explicite ; les limites de Studio (`safe_eval`, pas de
  JS, pas de surcharge, pas de test Python) sont annoncées avant de faire. Le
  livrable Studio est un pack versionné (`odoo_pack.py`), créé et appliqué en
  contexte `studio` — indiscernable d'un travail fait dans Studio —, jamais en
  production sans confirmation.
- **Un ticket passe la main selon son verdict** : usage ou configuration → réponse
  seule ; données → réparation prouvée sur la copie, confirmée par l'humain pour la
  production ; bug avec test rouge → `/odoo-new` reprend à l'étape 2 sans rejouer
  l'analyste (sauf droits, compta, facturation, données existantes) ; évolution
  déguisée → `odoo-analyst`. Une release contient du dev et des tickets ; la
  clôture documente les deux.
- **Aucun livrable documentaire avant la clôture** : ni guide, ni capture, ni
  communication pendant qu'une release est ouverte, sauf demande explicite. Un écran
  qui change se note dans « Ce que l'utilisateur verra » et attend `/odoo-close`.
- Une demande de dev triviale ne dispense pas de la revue fonctionnelle,
  expédiée en une ligne quand la demande est saine.
- Une question purement technique (« où est défini X ») se répond directement,
  sans agent — dans la série du projet.
- Toute intervention se termine par une entrée (≤ 15 lignes) dans le
  `JOURNAL.md` du projet ; le détail vit dans le dossier de la release.
- Claude Code et Codex emploient la même définition de graphe. Ils délèguent
  seulement les nœuds indépendants quand leur mécanisme de sous-agents est
  disponible ; sinon l'agent principal applique le rôle lui-même. Le résultat
  et les preuves attendues restent identiques.
- Hors Odoo, cet aiguillage ne s'applique pas.

## Données réelles

La voie normale est une **copie locale** de la sauvegarde client :
`~/.odoo19-agents/scripts/odoo-restore.sh <sauvegarde.zip> --db <client>_test`
(neutralisée, `admin/admin`, tout y est permis). Sans sauvegarde, l'accès à une
base distante se **déclare** par **`/odoo-env`** : boîte de dialogue du bureau,
clé dans le trousseau de la personne, métadonnées sans secret dans
`<projet>/.odoo-agents/instances.json` (commitées). Jamais un identifiant dans
la conversation ; clé API et compte en lecture seule recommandés.

**Production — règles absolues** : annonce en clair *« Vous me donnez accès à
la PRODUCTION de <client>. Je n'y ferai que de la lecture. Toute écriture vous
sera demandée explicitement, opération par opération. »* ; lecture seule par
défaut (`odoo_instance.py` refuse `create`/`write`/`unlink` en production) ;
une écriture exige la confirmation humaine de **cette** opération, puis
`--allow-write` et `ODOO_PRODUCTION_CONFIRMED=<nom>` ; jamais en masse ; aucun
test, capture ni reprise en production ; aucun identifiant affiché, journalisé
ou commité. Staging et test : écriture permise, annoncée, nettoyée derrière.
