Flow terminé, release ouverte, aucun verrou pendant.

## Reprise

L'état du premier orchestrateur était intact : `briefing`, `functional_review` et `module_implementation_high_risk` → done, avec leurs preuves et empreintes. Je ne les ai pas rejoués. Les trois nœuds QA restaient revendiqués par des propriétaires morts, sans aucun rapport rendu — les 8 critères étaient tous `missing`.

Libération des trois revendications par `odoo_flow.py release`, motif et preuve joints (`recovery-interruption.json`, `evidence_sha256 f466685…`, `git_head 28fbbd6`, bases conservées), traçés dans `.odoo-agents/flow-artifacts/contrainte-jours-positifs/reprise/interruption.md` et dans `claim_events` de l'état.

## Trois voies QA réellement parallèles

Verrous compatibles (lecture partagée du code, écritures disjointes), donc une seule vague de trois sous-agents `odoo-tester` indépendants :

| Voie | Périmètre exclusif | Résultat |
|---|---|---|
| copie client | `lab_client` : update + XML-RPC réel | C02, C03, C04, C05, C07 |
| exécution | `lab_qa` : install neuve, mise à jour, tests | C06, part suite de C08 — `install=ok`, `update=ok`, 5 tests verts |
| statique | conformité 19.0, revue du diff | C01 — `models.Constraint`, message littéral, périmètre tenu |

## A8

L'implémentation déclarait explicitement ne pas avoir de preuve RPC. Elle existe maintenant, et je l'ai relue appel par appel plutôt que de croire le rapport :

- `create(days=-1)` par le vrai XML-RPC → `fault_code=2`, `fault_string` = « The operation cannot be completed: **Le nombre de jours doit être positif ou nul.** ». La phrase exigée y est mot à mot ; le préfixe vient du noyau (`odoo/service/model.py::retrying`), fait déjà arbitré en revue fonctionnelle **avant** la QA — je n'ai assoupli aucun critère après coup.
- Conservation après rejet : id 3 relu identique (`days=5`, `daily_rate=20.0`, `amount_total=100.0`), `search_read` par nom rendant **un seul** enregistrement.
- `days=0` accepté en création et en modification ; total `5×20=100` puis `0×20=0`.

QA de tâche **VALIDÉ**, 8/8 couverts, chaque critère adossé à un fichier de preuve vérifié par empreinte : `qa.md`, `coverage.json`, `qa_synthese.md`, `compte_rendu.md` dans la release. Journal à jour (`.odoo-agents/JOURNAL.md`).

## Ce que je laisse en l'état, volontairement

- Clé `author` absente du manifest : dette vérifiée antérieure à la tâche (`git show 28fbbd6`), **non corrigée** — hors du périmètre fixé.
- La suite de tests du module est ORM seule ; aucun test RPC n'y a été ajouté. La composante « vrai appel RPC » de C08 est portée par les journaux XML-RPC, pas par les tests. C'est un constat, pas une couverture masquée.
- Enregistrements de QA id 2 et 3 laissés sur la copie synthétique `lab_client`.
- Recette complète, doc métier et README final : ils appartiennent à `/odoo-close`, non joués ici. Rien n'est commité, vous ne l'avez pas demandé.