# Réception de la fidélité d’une tâche

Le garde optionnel relie une demande originale et ses décisions, la spécification,
les preuves et **deux fichiers de mémoire proposés**. Il contrôle leur intégrité,
l’existence des citations et une déclaration positive de réception indépendante.
Il ne juge pas le sens des textes, ne prouve pas l’identité du relecteur et ne
remplace ni la couverture des critères ni la QA technique. Son périmètre est
coopératif ; l’édition directe du flow n’est pas une frontière de sécurité.

## Périmètre et reprise

Le garde est disponible pour les tâches directes et celles d'un plan dont le
snapshot possède la porte `reception_recovery_gate`. Le plan conserve sa
réservation pendant la reprise ; sa réception finale reste obligatoire. Les
anciens snapshots exigent une migration explicite, décrite plus bas.

## Préparer avant la réception QA

L’orchestrateur rédige des fichiers neufs contenant le **contenu complet futur**
de `.odoo-agents/PROJECT.md` et `.odoo-agents/JOURNAL.md`, en conservant les éléments
antérieurs pertinents. Il conserve les cibles actuelles jusqu’au `pass` de la
jointure. Même sans changement de PROJECT, fournir une copie identique et en
motiver l’absence de modification lors de la réception.

```bash
python3 ~/.odoo19-agents/scripts/odoo_flow.py prepare-reception FLOW.json \
  --source changelog/RELEASE/demande.md \
  --source decisions/decision.md \
  --spec changelog/RELEASE/revue_fonctionnelle.md \
  --evidence changelog/RELEASE/qa-runtime.md \
  --evidence changelog/RELEASE/coverage.json \
  --memory .odoo-agents/PROJECT.md=changelog/RELEASE/reception/PROJECT-propose.md \
  --memory .odoo-agents/JOURNAL.md=changelog/RELEASE/reception/JOURNAL-propose.md \
  --scope mon_module \
  --output changelog/RELEASE/reception/bundle-1.json \
  --owner codex-orchestrateur
```

Les chemins de cette commande sont relatifs au **projet du flow** ou absolus
à l’intérieur de celui-ci. Les sources, la spec, les preuves et les drafts doivent
être des fichiers non vides. La sortie est neuve et distincte des cibles mémoire ;
les deux drafts sont distincts des sources, des cibles et l’un de l’autre. Les
cibles canoniques ne peuvent pas être des liens redirigeant ailleurs. Le périmètre
de code est facultatif, mais doit être indiqué quand du code est contrôlé ; il
exclut les documents et les sorties du dossier.

La préparation se fait sous verrou du flow, actif et sans revendication d’un
autre propriétaire, avant tout `pass` d’une des trois jointures QA de tâche,
ou pendant la revendication de `reception_recovery_gate` par cet owner.
Le dossier `odoo-task-reception-bundle/1` contient les chemins relatifs et hashes
SHA-256 des groupes `source`, `spec`, `evidence`, les deux couples cible/draft avec
le hash antérieur de la cible (`null` si absente), une copie de chaque base
existante dans un fichier neuf adjacent au bundle, et l’empreinte du code. Le flow
épingle le chemin et le hash du dossier dans `task_reception`.

Si un contrat QA est lié, le chemin et le hash de la spécification du dossier
doivent être exactement ceux de ce contrat. Ce lien est vérifié à la préparation
et de nouveau à la réception, y compris si `bind-criteria` est intervenu après
la préparation.

Une correction permet une nouvelle préparation dans **un autre fichier** avant
le pass. Le flow conserve les anciens pointeurs dans `task_reception_history` et
les dossiers précédents restent sur disque. Cette opération ne remplace pas le
contrat QA lié par `bind-criteria` : une spécification révisée exige toujours le
traitement explicite de ce contrat.

## Fragment du relecteur

Un contexte indépendant confronte les trois axes ; le relecteur écrit uniquement
son fragment, sans modifier le dossier. Pour obtenir un squelette JSON :

```bash
python3 ~/.odoo19-agents/scripts/odoo_reception.py draft /chemin/projet/changelog/RELEASE/reception/bundle-1.json \
  --reviewer codex-tester-reception > /chemin/projet/changelog/RELEASE/reception/review-1.json
```

Le squelette est volontairement `blocked`, avec trois axes `fail` non renseignés.
Structure à compléter :

```json
{
  "format": "odoo-task-reception/1",
  "bundle_sha256": "SHA256_DU_FICHIER_BUNDLE",
  "reviewer": "codex-tester-reception",
  "mode": "independent",
  "verdict": "pass",
  "checks": {
    "request_contract": {
      "status": "pass",
      "citations": [
        {"path": "demande.md", "quote": "Passage exact de la demande."},
        {"path": "revue.md", "quote": "Passage exact de la revue."}
      ],
      "explanation": "Constat de correspondance dans les deux sens."
    },
    "contract_evidence": {
      "status": "pass",
      "citations": [
        {"path": "revue.md", "quote": "Passage exact du critère."},
        {"path": "runtime.log", "quote": "Passage exact de la preuve."}
      ],
      "explanation": "Ce passage démontre les conditions du critère."
    },
    "source_memory": {
      "status": "pass",
      "citations": [
        {"path": "demande.md", "quote": "Passage exact de la décision métier."},
        {"path": "PROJECT-propose.md", "quote": "Phrase proposée dans la mémoire."},
        {"path": "JOURNAL-propose.md", "quote": "Constat proposé dans le journal."}
      ],
      "explanation": "Portée et exceptions conservées ; modifications de mémoire confrontées aux sources."
    }
  }
}
```

Les chemins des citations reprennent exactement les chemins relatifs du bundle.
Les citations sont des sous-chaînes exactes, non vides, des fichiers gelés.
Chaque axe doit citer au moins un fichier de chacun des deux groupes confrontés :
source/spec, spec/evidence, source/draft. Le relecteur doit couvrir **toutes les
obligations et modifications pertinentes** : ce minimum mécanique de deux
groupes ne démontre pas l’exhaustivité sémantique. Lorsque les entrées mémoire
contiennent `base`, `source_memory` doit aussi citer chacune de ces copies contenant du texte non blanc et
vérifier la conservation des contributions antérieures. Les bundles historiques
sans copie de base restent lisibles. Une explication non vide est
requise ; son exactitude demeure une responsabilité de la relecture.

Les trois clés d’axes sont obligatoires exactement. Les statuts sont `pass|fail`,
le verdict `pass|revise|blocked` et le mode `independent|self`. Seuls trois axes
`pass`, un verdict `pass`, le mode `independent` et un reviewer déclaré différent
de l’owner de préparation **et du propriétaire actuel de complétion** peuvent
autoriser la jointure. `self` documente une auto-relecture,
mais **n’autorise pas** le pass d’un flow avec ce garde. Changer seulement de nom
ne démontre pas une délégation réelle : conserver séparément la trace native du
sous-agent quand cette propriété est mesurée.

## Réception puis publication

Fournir le fragment à `complete ... --outcome pass --evidence review-1.json`, avec
la couverture et le rapport QA si ces contrôles sont activés. Les trois jointures
concernées sont `module_task_gate`, `module_high_gate`, `studio_task_gate`. La
réception est reconnue par son contenu, quelle que soit l’extension du fichier ;
une seule réception doit être fournie. Le garde contrôle l’intégrité des sources,
preuves, drafts, code et cibles mémoire encore inchangées. Il vérifie aussi la
fraîcheur des preuves structurées d’exécution et des références d’une couverture
imbriquée. Il ne transforme pas un log libre en preuve de code contrôlé.

Une complétion réussie enregistre `accepted_reception` avec chemin et hash du
fragment. Un refus ne consomme ni claim, ni verrou, ni jeton. `retry` et `blocked`
restent accessibles avec un constat même si le dossier est périmé ; le nœud
`journal_task_blocked` permet de consigner cet échec.

Au nœud `journal_task`, l'orchestrateur revendique le verrou mémoire puis publie
les **octets exacts** des deux drafts approuvés :

```bash
python3 ~/.odoo19-agents/scripts/odoo_flow.py publish-memory FLOW.json --owner codex-orchestrateur
python3 ~/.odoo19-agents/scripts/odoo_flow.py complete FLOW.json journal_task \
  --owner codex-orchestrateur --outcome done --evidence changelog/RELEASE/publication.md
```

Le publieur valide le bundle et le reçu épinglés, les sources, les preuves, le
code et **les deux cibles avant toute écriture**. Chaque cible doit être encore
à sa base ou déjà identique au draft accepté. Une autre valeur interdit la
publication. Chaque remplacement de fichier est atomique ; l'ensemble des deux
fichiers ne constitue pas une transaction atomique. Une interruption de processus
après le premier remplacement se reprend en relançant la même commande : le
fichier déjà publié n'est pas réécrit et le journal n'est pas ajouté deux fois.
Le verrou coopératif ne protège pas contre un processus externe qui l'ignore.
À `done`, le garde vérifie de nouveau l'identité des cibles et la fraîcheur.

Si le contexte précédent est arrêté, consigner ce constat puis utiliser les API
`release --reason` et `claim` pour transférer sa revendication. Ne jamais modifier
le registre ni les JSON d'état directement. `check-bases` reste un diagnostic en
lecture seule exigeant les bases initiales ; ce n'est pas la commande de reprise
d'une publication partielle.

## Conflit après QA : nouvelle réception dans le même flow

Une modification concurrente de PROJECT ou JOURNAL rend la proposition obsolète,
y compris si elle concerne une autre tâche. Garder ces fichiers et consigner le
refus du publieur dans une preuve isolée, puis :

1. Compléter `journal_task` avec `--outcome retry` et cette preuve.
2. Revendiquer `reception_recovery_gate` ; son verrou mémoire protège la préparation.
3. Préparer de nouveaux drafts depuis la mémoire courante, en conservant le travail
   déjà publié. Appeler `prepare-reception` avec une sortie neuve et les **mêmes**
   sources, spécification, preuves et périmètres de code que la réception acceptée.
4. Faire relire ce nouveau bundle dans un contexte indépendant. Le relecteur compare
   aussi les bases figées aux drafts et cite les contributions à conserver.
5. Compléter la porte avec `--outcome pass --evidence NOUVEAU_RECU`, puis revendiquer
   le journal, exécuter `publish-memory` et terminer le journal.

L'ancienne réception reste conservée ; seule une nouvelle réception acceptée
remplace la réception active. Le cycle ne permet pas de blanchir une modification
du code, des sources ou des preuves. Leur péremption exige un arrêt explicite et
une nouvelle tentative avec la QA appropriée. Au plus deux retours de reprise
sont autorisés. En cas d'impossibilité, compléter le journal ou la porte avec
`blocked`, puis terminer `memory_task_blocked` avec le constat d'échec mémoire.
Il s'agit d'un arrêt de publication, pas d'une déclaration de QA rouge. Le plan
peut ensuite utiliser `reopen --reason` et conserver l'ancienne tentative.

## Migration bornée des anciens snapshots

Avant la première exécution du journal, sur un flow actif sans revendication :

```bash
python3 ~/.odoo19-agents/scripts/odoo_flow.py upgrade-recovery FLOW.json \
  --owner codex-orchestrateur --from-graph /archive/odoo-workflow-original.json
```

`--from-graph` fournit les octets exacts du graphe historique lorsque son chemin
d'origine a été remplacé. L'outil vérifie son hash et son snapshot, puis exige
l'ajout exact du sous-graphe connu : les anciens nœuds et transitions restent
identiques. L'historique et les jetons sont conservés, la migration est consignée.
Tout autre changement, un flow terminal, une revendication active ou un journal
déjà exécuté entraîne un refus. Cette commande n'assouplit pas la migration
générique. Conserver l'archive historique ; ne pas reconstruire un état à la main.

Les flows sans `task_reception` gardent leur publication habituelle. Le garde
contrôle des hashes et citations ; la fidélité métier et la réalité de la
délégation exigent toujours une relecture et une trace indépendante.
