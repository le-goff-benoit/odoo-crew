Travail terminé et vérifié.

## Implémentation — `scheduler.py`

L'API publique reste `scheduler.ready(tasks, active_locks)`, aucun `implementation.py` n'a été nécessaire. La fonction ne lit que ses entrées (aucune mutation) et procède en quatre temps :

1. **Modes de verrou** — toute valeur d'`active_locks` hors `read`/`write` lève `ValueError`, y compris sur une ressource que personne ne touche.
2. **Indexation/validation** (`_index`) — identifiants dupliqués, statuts inconnus, dépendances absentes (sur *toutes* les tâches, pas seulement les pending).
3. **Cycles** (`_reject_cycles`) — DFS itératif tri-couleur sur le graphe entier, donc les cycles d'une composante non pending ou inatteignable sont rejetés ; l'auto-dépendance compte comme cycle.
4. **Éligibilité** (`_satisfied`) — post-ordre itératif mémoïsé : une tâche est libérée si chaque dépendance **transitive** est `received` *et* `proof_current`. Une dépendance reçue mais fondée sur une dépendance périmée ne libère donc pas sa descendante. Le `proof_current` du candidat lui-même est ignoré (conforme à `test_public.py`).
5. **Verrous** (`_lock_free`) — écrire exige une ressource sans aucun verrou ; lire n'est bloqué que par un verrou `write`. Les pending proposées ne se verrouillent pas entre elles.

Les deux parcours sont itératifs plutôt que récursifs : sur une chaîne de 5 000 dépendances, une version récursive dépasserait la limite de pile.

## Bilan des tests

`python3 -m unittest discover -s . -p 'test_*.py' -v` → **43 tests, OK** (0 échec, 0 erreur).

- `test_public.py` conservé intact (1 test).
- `test_scheduler.py` ajouté (42 tests) en quatre classes : `EligibilityTest` (transitivité, preuve périmée, diamant, tri lexicographique, chaîne profonde), `LockTest` (les 4 combinaisons lecture/écriture × read/write, non-revendication entre candidats), `RejectionTest` (doublon, dépendance absente, statut et mode inconnus, cycles y compris hors composante pending), `PurityTest` (entrées inchangées via `deepcopy`, idempotence).

Un échec est survenu au premier passage — il venait de mon propre test (`{}` passé en verrous alors que l'assertion attendait un blocage) ; le test a été corrigé pour vérifier les deux cas, l'implémentation n'était pas en cause.

## Preuve

`/work/evidence.json` (+ `evidence.log`) produit par `odoo_evidence.py run`, scopes `scheduler.py`, `test_public.py`, `test_scheduler.py`, environnement `implementation-bench-v1`, avec la commande unittest du contrat : `result: passed`, `exit_code: 0`, `error: null`. `odoo_evidence.py verify` confirme : « Preuve valide et périmètre inchangé. »