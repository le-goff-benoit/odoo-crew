# studio_implementation — point 1

Copie : `lab_client` (19.0+e-20260817), XML-RPC, contexte `studio=True` sur toute écriture.

- Champ créé : `x_lab_request.x_studio_needs_review` — boolean, manual, stocké, calculé, `depends = x_studio_days,x_studio_kind`, readonly.
- Identifiant externe relevé (non fabriqué) : `studio_customization.x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826`, `studio=True`, `noupdate=True`.
- Champs existants `x_name`, `x_studio_days`, `x_studio_kind` : intacts, XML-ID `lab_seed_*` conservés.
- Aucun droit, aucune règle, aucune vue, aucune automatisation créés.

Livrables : `studio/lab_rpc.py`, `studio/build_needs_review.py`, `studio/test_needs_review.py`, `studio/created.txt`, `studio/pack.json`, `studio/journal_execution.md`.

Deux difficultés rencontrées, traitées et documentées dans le code :

1. Odoo ne pose `noupdate` sur l'identifiant externe qu'au premier *write* en contexte studio (`web_studio/models/ir_model_data.py:19-25`), pas à la création. Le script rejoue le chemin de Studio pour obtenir un pack protégé d'une mise à niveau.
2. `x_lab_request` n'a aucun droit d'accès (contradiction C1 de la revue). Le scénario pose un droit temporaire, hors contexte studio, et le retire ; il doit vider explicitement les caches de droits (`ir.model.access.call_cache_clearing_methods`) sans quoi le droit reste invisible du processus qui sert les appels.
