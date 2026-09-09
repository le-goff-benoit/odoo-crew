# Ordered recovery: public protocol

Corpus documentaire distinct. Aucun code Odoo. Le seul amorçage synthétique place
les flows AVANT QA. Aucun reçu, reviewer, bundle ou pass n'est injecté. Le banc
ne certifie jamais l'indépendance par un nom de reviewer : les traces natives
exportées, identifiants et textes réellement remis sont audités séparément.

Ne remettre au modèle que project/, task-A.txt (ou task-B.txt), reviewer.txt
pour le reviewer et resume.txt pour la reprise. oracle.json, checkpoints/,
check.py, sealed_case.py et calibration sont réservés au juge. Le détail O03
reste interdit au développeur jusqu'à son annonce de gel. Les contrôles
sémantiques admettent toute formulation équivalente ; aucun texte final exact
n'est requis. Une réussite mécanique seule n'est jamais une réussite native.

## CLI et ordre obligatoire

```
python3 materialize.py O01 --pack /path/reference --output /new/reference-O01
python3 materialize.py O02 --pack /path/reference --output /new/reference-O02
python3 checkpoint.py /new/reference-O01 A_PREPARED --agent ID_A --trace /export/A.txt
python3 checkpoint.py /new/reference-O01 A_REVIEWED --agent ID_REVIEW_A --trace /export/review-A.txt --artifact /new/reference-O01/project/path/review.json
```

A réalise preuve documentaire, drafts et prepare-reception, puis s'arrête avant
pass. Sceller A_PREPARED. Un agent réellement indépendant lit et reçoit ce
bundle ; sceller A_REVIEWED avec son artefact et sa trace. Le coordinateur fait
le complete module_task_gate --outcome pass par API publique, puis scelle
A_ACCEPTED avec sa trace. Ce snapshot doit contenir le pass et les empreintes
qui correspondent exactement à la revue précédente.

O01 : seulement ALORS démarrer B avec task-B.txt. B prépare sa preuve, ses drafts
et son bundle. Nouveau reviewer indépendant pour B ; sceller B_REVIEWED avec
son reçu. Faire le pass B, puis claim journal_task sous propriétaire explicite.
Sceller B_LOCKED (le registre doit porter le même verrou que le flow).
Faire publish-memory B par API publique et sceller B_PUBLISHED AVANT de libérer
le verrou : les deux mémoires doivent correspondre aux drafts reçus B.
Faire complete journal_task B --outcome done et terminer le contexte B.

O02 : aucune tâche B ni mutation. Réception initiale A tout aussi réelle.

Démarrer une reprise A avec fork_turns=none, lui remettre resume.txt et le projet.
Sceller A_RESUME_START avec l'identifiant de ce nouveau contexte et une trace
prouvant son ouverture, avant sa première action. Ce n'est ni le contexte auteur
ni celui du reviewer. Après sa fin, sceller A_FINISHED et lancer check.py.
La trace remise à chaque checkpoint est copiée et hachée, donc un export
ultérieur enrichi ne détruit pas la preuve déjà scellée.

```
python3 checkpoint.py RUN EVENT --agent NATIVE_ID --trace /export/event.txt
python3 check.py RUN > RUN/mechanical.json
```

Geler avant candidat : protocole, prompts, matériel, checker, calibration,
contre-épreuve et manifest sont hachés dans FROZEN.json. Le protocole global
fixe modèles, budgets, plafond de contextes et révisions ; celui-ci ne les change
pas. Les prompts remis doivent eux aussi être archivés dans les traces natives.

## Assertions et audit

Mécanique : ordre séquentiel et temporel strict, snapshots et exports intacts,
receipt initial lié à la revue avant toute B, publication B sous verrou vérifié,
originaux préservés, deux mémoires identiques aux drafts acceptés finaux,
fraîcheur sources/preuves/code, pas de claim orphelin. Positif : exactement le
reçu initial et un seul nouveau done journal, sans retry ni nouveau gate.

Audit obligatoire : vrais contextes et indépendance ; outils publics exclusifs
après amorçage ; pas de QA/relecture superflue sur O02 ; préservation sémantique
des décisions préexistantes et B, ajout de A sans doublon ni règle non demandée ;
chaque reçu fondé sur les trois axes et les sources originales ; compte rendu
fidèle et voie publique explicite si arrêt. Tout échec critique interdit la
promotion, sans compensation par score. Les plans ne sont pas exercés ici.
