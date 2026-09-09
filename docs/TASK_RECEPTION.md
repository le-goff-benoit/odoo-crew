# Réception de la fidélité d’une tâche

Le garde optionnel relie une demande originale et ses décisions, la spécification,
les preuves et **deux fichiers de mémoire proposés**. Il contrôle leur intégrité,
l’existence des citations et une déclaration positive de réception indépendante.
Il ne juge pas le sens des textes, ne prouve pas l’identité du relecteur et ne
remplace ni la couverture des critères ni la QA technique. Son périmètre est
coopératif ; l’édition directe du flow n’est pas une frontière de sécurité.

## Périmètre expérimental

`prepare-reception` refuse explicitement les flows portant `plan_task`, issus de
l’exécution d’un plan de release. Une modification concurrente de mémoire après
le pass pourrait sinon bloquer définitivement leur publication et la suite du
plan, sans transition de reprise appropriée dans le graphe actuel. Ces tâches
peuvent recevoir la même **réception documentaire indépendante sans activer ce
garde**. Aucun nœud, mécanisme d’annulation ni comportement de plan n’est modifié.
Le garde reste limité aux tâches autonomes avec sources disponibles ; cette
campagne ne qualifie pas son emploi dans les plans de release.

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
autre propriétaire, avant tout `pass` d’une des trois jointures QA de tâche.
Le dossier `odoo-task-reception-bundle/1` contient les chemins relatifs et hashes
SHA-256 des groupes `source`, `spec`, `evidence`, les deux couples cible/draft avec
le hash antérieur de la cible (`null` si absente), et l’empreinte du code. Le flow
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
groupes ne démontre pas l’exhaustivité sémantique. Une explication non vide est
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

Au nœud `journal_task`, l’orchestrateur, propriétaire du verrou mémoire, publie
les **octets exacts** des deux drafts approuvés, puis termine avec `done`. La
publication n’est pas automatisée par ce garde. Après la revendication de
`journal_task`, vérifier les bases et la fraîcheur en lecture seule, puis garder
le verrou mémoire pendant la copie :

```bash
python3 ~/.odoo19-agents/scripts/odoo_reception.py check-bases /chemin/projet/changelog/RELEASE/reception/bundle-1.json
```

Un code de sortie non nul interdit de poursuivre la copie. Ce contrôle relit les
hashes antérieurs des cibles et les fichiers référencés par le bundle fourni ;
le lien au hash épinglé par le flow reste vérifié à `complete`.
Les hashes antérieurs doivent encore correspondre : une tâche concurrente peut avoir écrit entre la
réception QA et la prise du verrou mémoire. Ne pas écraser ce travail ; préparer
une nouvelle réception dans un nouveau flow si le premier a déjà passé sa QA.
À `done`, le garde revalide le fragment, le dossier, ses sources et le code, puis
exige l’identité des cibles publiées avec les drafts approuvés.

Le hash porte sur **tout** PROJECT/JOURNAL. Cela peut imposer une nouvelle
réception après une modification concurrente sans rapport avec la tâche. Cette
limite est conservatrice et explicite ; ce garde ne réalise pas une fusion de
régions ni une comparaison métier. Les flows historiques sans `task_reception`,
les parcours sans jointure QA et le graphe existant restent inchangés.
