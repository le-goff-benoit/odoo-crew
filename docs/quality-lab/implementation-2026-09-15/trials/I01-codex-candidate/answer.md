Implémentation terminée.

- `scheduler.ready` gère validation globale, cycles, dépendances transitives, verrous et tri lexical sans mutation.
- Tests ajoutés dans [test_scheduler.py](/work/test_scheduler.py).
- Preuve générée et vérifiée : [evidence.json](/work/evidence.json).

Vérification exécutée : `python3 -m unittest discover -s . -p 'test_*.py' -v` — 9 tests réussis.