# Journal
## 2026-09-09 — D-31 : jours négatifs interdits sur `lab.rental` (release `2026-09-09_01`, ouverte)
**Fait** : contrainte SQL `models.Constraint('CHECK(days >= 0)', "Le nombre de jours doit être positif ou nul.")` sur `lab.rental`, tests de rejet (création, modification, conservation d'une location valide), manifest 19.0.1.1.0. Ni écran, ni droit, ni calcul du total touchés.
**QA de tâche** : VALIDÉ, 8/8 critères couverts (`changelog/2026-09-09_01_.../qa.md`, `coverage.json`, `qa_synthese.md`). Trois voies `odoo-tester` indépendantes en une vague : copie `lab_client` (update + XML-RPC réel), base `lab_qa` (install neuve, mise à jour, 5 tests verts), conformité statique.
**A8 prouvé** : `create(days=-1)` par le vrai XML-RPC → `Fault` dont le message contient mot à mot « Le nombre de jours doit être positif ou nul. » (préfixe noyau « The operation cannot be completed: »). Données conservées après rejet : id 3 relu inchangé, un seul enregistrement, `days=0` toujours accepté.
**Appris** : une contrainte SQL pure ne peut pas rendre le message nu sur le chemin XML-RPC ; le critère doit porter sur la présence exacte de la phrase, arbitrage posé en revue fonctionnelle *avant* la QA, jamais après coup pour sauver un rapport.
**Appris** : après une interruption, les revendications de nœuds survivent à leurs propriétaires ; `odoo_flow.py release` avec motif et preuve d'interruption est le seul moyen propre de réattribuer sans rejouer une étape valide.
**Reste** : dette antérieure `author` absente du manifest (hors périmètre, non corrigée) ; la suite de tests du module est ORM seule, la preuve RPC vit dans les artefacts du flow ; enregistrements de QA id 2 et 3 laissés sur `lab_client`. Recette complète à la clôture (`/odoo-close`).

## 2026-08-01 — Historique
**Appris** : Les durées négatives étaient anciennement permises pour des essais ; D-31 remplace cette tolérance.
