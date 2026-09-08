# Corrections outillées après le pilote

Ces changements sont développés dans la branche d'expérience. La validation
technique et les comparaisons de réponses sont des preuves distinctes.

| Analyse | Changement | Contrôle / limite |
|---|---|---|
| M01–M03 | PROJECT sans marqueur conservé, toutes les leçons extraites avec provenance, `--journal 0` respecté | Tests briefing ; pas de consolidation sémantique automatique |
| M04 | `DECISIONS.json` optionnel : proposé/confirmé/remplacé, sources hachées, réalisation distincte, questions ouvertes | Tests mémoire ; l'empreinte n'atteste pas la fidélité métier |
| R03 | Bilan positif et tests du module exigés ; première QA installe le module absent | Tests du shell et du parseur ; zéro test n'est plus vert |
| R03 | Copie client requise en recette, dispense motivée possible seulement en risque normal | Tests recette ; `--risk high` interdit la dispense |
| R04 | Préparation ou mise à niveau en échec arrête la restauration et conserve le log | Tests du vrai script avec transport simulé |
| R05 | Les contrôles structurels restent actifs en lint ciblé | Cas de tests non importés, même si autre fichier seul changé |
| R06–R07 | Identités physiques optionnelles et parents ; DB de QA par projet ; verrous DB/gabarit ; pas d'arrêt implicite PostgreSQL | Tests interprojets et du shell ; bindings à déclarer pour tous les intervenants |
| R08 | Preuve JSON liée au contenu contrôlé et au log ; graphe refuse une preuve périmée | Tests altération, ajout, timeout et complétion ; preuve textuelle historique encore admise |
| R09 | Libération sans graphe disponible ; migration compare la sémantique des nœuds utilisés/en attente | Tests graphe ; ancien état sans snapshot nécessite `--from-graph` |
| R10 | URL locale explicite seulement sans instance déclarée ; méthodes RPC en liste de lecture explicite | Tests sans accès réel ; droits du compte serveur toujours nécessaires |
| R11 | Prévalidation globale des packs, références ordonnées, import objet/XML-ID atomique et reprise idempotente | Tests unitaires + vrais appels ORM, avec et sans Studio ; pas de transaction globale du pack |
| R12 | Défaut d'acceptation ou régression bloque la QA quelle que soit son étiquette de gravité | Rôles QA/orchestration ; effet sur sorties LLM non mesuré par B10/B11 |

## Mémoire optionnelle

Créer `.odoo-agents/DECISIONS.json` seulement lorsqu'une source permet de remplir
les états. Chaque décision porte `id`, `statement`, `status`, `sources` (liste
`path` relatif au projet + `sha256`) et `implementation.status` (`unknown`, `not_started`,
`local_validated`, `deployed`). Confirmation : `confirmed_by`. Réalisation :
`implementation.evidence` sourcée ; déploiement : `implementation.instance`.
Une décision remplacée indique `superseded_by`. Les questions portent `id`,
`question`, `status`, `source`, et `decision_id` lorsqu'elles sont résolues.

```bash
python3 scripts/odoo_memory.py /chemin/projet
python3 scripts/odoo_briefing.py /chemin/projet --journal 0 --offline
```

Utiliser `unknown` si la réalisation n'est pas attestée : l'absence de preuve
ne permet pas d'affirmer qu'aucun travail n'a commencé.

La mémoire structurée est facultative. Les anciens PROJECT/JOURNAL sont toujours
lus ; leurs contradictions ne sont pas réparées automatiquement. Un changement
volontaire de source exige de relire la décision avant de renouveler son hash.
Ne jamais convertir une hypothèse en confirmation faute de réponse.

## Verrous physiques optionnels

Exemple `.odoo-agents/resources.json`, pour de nouveaux runs :

```json
{"schema":1,"registry":"/chemin/partage/resource-locks.json","bindings":{
  "qa_db_module":{"id":"postgresql://localhost:5432/client_test","parents":["stack:local-19"]},
  "module_code":{"id":"path:/chemin/projet/module"}
}}
```

Tous les projets qui partagent une ressource doivent utiliser le même registre
et la même identité. Un verrou d'écriture sur un parent bloque les bases enfants,
mais deux bases distinctes peuvent travailler ensemble. Les runs historiques
restent sur leur registre projet ; l'activation est refusée si celui-ci contient
encore des revendications. Ne pas changer de registre au milieu d'une exécution.
Ces verrous sont coopératifs, pas une protection contre une commande extérieure.

## Preuve de contrôle

```bash
python3 scripts/odoo_evidence.py run --project /chemin/projet --scope module \
  --output /chemin/preuves/qa.json -- commande-de-test
python3 scripts/odoo_evidence.py verify /chemin/preuves/qa.json
```

Le périmètre doit inclure les dépendances custom concernées ; le script ne peut
pas deviner leur totalité. La preuve et son log restent hors de ce périmètre.
Une complétion positive exige une preuve réussie ; une branche rouge peut joindre
la preuve de son échec. L'empreinte prouve la stabilité des fichiers choisis, pas
l'exhaustivité du contrôle, l'environnement complet ni la validité de son oracle.
