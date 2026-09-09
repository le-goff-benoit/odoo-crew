# Installer les agents Odoo

Ce document couvre l'installation, la validation et la mise à jour du
dispositif partagé par Claude Code et Codex. Pour son fonctionnement, voir
[README.md](README.md).

## Prérequis

- Linux avec Bash et Git ;
- Python 3.10 ou plus récent ;
- Docker avec le plugin Compose pour la QA Odoo réelle ;
- Claude Code, Codex, ou les deux ;
- les sources Odoo des séries utilisées, en lecture seule.

Disposition attendue par défaut :

```text
~/odoo-sources/
├── 17.0/
├── 17.0-enterprise/
├── 18.0/
├── 18.0-enterprise/
├── 19.0/
├── 19.0-enterprise/
└── …
```

Un autre emplacement peut être déclaré avant les commandes :

```bash
export ODOO_SOURCES_DIR=/chemin/vers/odoo-sources
```

Les sources sont montées en lecture seule par le stack. Le code client ne doit
jamais être écrit dans ces dépôts.

## Première installation

```bash
git clone git@github.com:le-goff-benoit/odoo-skills.git ~/.odoo19-agents
cd ~/.odoo19-agents
./build.sh
```

`build.sh` effectue trois opérations :

1. validation du graphe et exécution de sa suite de tests ;
2. génération des agents, commandes et skills Claude Code/Codex ;
3. injection du bloc d'aiguillage délimité dans les consignes globales.

Fichiers générés :

```text
~/.claude/agents/odoo-*.md
~/.claude/commands/odoo-*.md
~/.claude/skills/camptocamp-docs/
~/.claude/CLAUDE.md              bloc Odoo uniquement

~/.codex/skills/odoo-*/SKILL.md
~/.codex/skills/camptocamp-docs/
~/.codex/AGENTS.md               bloc Odoo uniquement
```

Ces fichiers ne s'éditent pas directement. Leurs sources se trouvent dans
`roles/`, `routing.md`, `workflows/` et les référentiels de ce dépôt.

## Vérifier l'installation

Depuis `~/.odoo19-agents` :

```bash
python3 scripts/odoo_flow.py validate
python3 scripts/odoo_flow.py analyze
python3 -m unittest discover -s tests -v
```

Puis vérifier que le briefing répond sur un projet Odoo :

```bash
python3 scripts/odoo_briefing.py /chemin/vers/un/projet
```

Si le projet n'a pas encore de fiche locale :

```bash
scripts/odoo_project_scan.py /chemin/vers/un/projet
```

Le scan crée les consignes de projet et `.odoo-agents/` sans y placer de
secret.

## Construire le stack de QA

Déclarer le dossier qui contient les modules custom, puis construire l'image de
la série :

```bash
export ODOO_ADDONS_DIR=/chemin/vers/le/projet
scripts/odoo-stack.sh build
scripts/odoo-stack.sh up
```

Ports par défaut :

| Service | Port |
|---|---:|
| Odoo HTTP | `8079` |
| Odoo gevent | `8082` |
| PostgreSQL | `5439` |

Chaque série possède son projet Compose, son image et ses volumes. Chaque
module utilise une base de test distincte. Pour faire cohabiter plusieurs
stacks, ajuster les ports selon les options décrites par
`scripts/odoo-stack.sh --help`.

## Mettre à jour

```bash
cd ~/.odoo19-agents
git pull --ff-only
./build.sh
```

`build.sh` doit être relancé après chaque mise à jour : les fichiers Claude et
Codex sont des sorties générées, pas les sources du dispositif.

Sur un autre poste, la même séquence suffit si les prérequis et les sources
Odoo sont présents.

## Déclarer les environnements distants

Utiliser `/odoo-env`, ou directement :

```bash
scripts/odoo_instance.py add /chemin/vers/le/projet
scripts/odoo_instance.py list /chemin/vers/le/projet
scripts/odoo_instance.py check /chemin/vers/le/projet staging
```

La boîte de dialogue enregistre la clé API dans le trousseau GNOME. Seules les
métadonnées sans secret sont écrites dans
`<projet>/.odoo-agents/instances.json`.

En production, l'accès reste en lecture seule. Chaque écriture exige une
confirmation humaine portant sur l'opération précise et les protections de
`odoo_instance.py`.

## Diagnostic rapide

### Le build refuse de générer les profils

Lire d'abord l'erreur du validateur ou du test affichée par `build.sh`. Corriger
la source dans ce dépôt ; ne jamais contourner le contrôle en modifiant un
profil généré.

### Un module est annoncé comme introuvable

Vérifier que `ODOO_ADDONS_DIR` désigne le dossier contenant le module et que le
chemin est lisible par l'uid 101 du conteneur. `odoo-test.sh` considère
`invalid module names, ignored` comme un échec, même si Odoo renvoie le code 0.

### Les tours sont ignorés

Reconstruire l'image de QA. Elle fournit Chrome et `websocket-client` ; un tour
ignoré faute de dépendance est traité comme un échec.

### Les profils semblent anciens

```bash
cd ~/.odoo19-agents
./build.sh
```

Vérifier ensuite la date et le commentaire « Généré par » dans le profil
concerné. La source à corriger reste le fichier correspondant sous `roles/`.

### Le graphe d'un run a changé

Le moteur refuse une reprise silencieuse. Si la nouvelle définition reste
compatible avec l'historique :

```bash
python3 scripts/odoo_flow.py migrate \
  <projet>/.odoo-agents/flows/<run>.json
```

Libérer auparavant tous les nœuds encore revendiqués.

## Mise à jour du 9 septembre 2026

Après `git pull`, `./build.sh` installe aussi `/odoo-plan`, `/odoo-start` et
`/odoo-improve` sur Claude Code et Codex. Le contrôle couvre 26 fichiers générés,
les deux blocs d'aiguillage et le pointeur personnel. Relancer une nouvelle
conversation pour charger les nouvelles descriptions de skills.

Le build remplace les anciens blocs générés du `~/AGENTS.md` par le pointeur
commun et retire le doublon documentaire généré de `~/.agents/skills` ; les
originaux sont sauvegardés sous `~/.odoo-agents-backups/loaded-instructions/`.
Le texte personnel hors des blocs est conservé. Un doublon non généré exige une
réconciliation explicite et n'est pas supprimé. Les projets clients ne sont pas
réécrits automatiquement.

Les releases nouvelles utilisent les contrôles décrits dans
[RELEASE_PLAN.md](docs/RELEASE_PLAN.md). Pour un run déjà ouvert, suivre la section
« Continuer un run commencé avec l'ancien graphe » avant de le reprendre. Les
preuves anciennes ne deviennent pas conformes par simple mise à jour des outils.
