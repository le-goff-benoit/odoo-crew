# Fragment QA — voie « scénarios RPC » (point 1)

**Testeur** claude-odoo-tester-runtime · **Base** `lab_client` (19.0) · **2026-09-09**

Scénario : `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/test_01_needs_review.py`, rejoué par le testeur après coup,
serveur neuf, valeurs relues **côté serveur** (jamais la valeur envoyée), données de
recette supprimées à la fin.

| Cas | Attendu (D-22) | Obtenu | État |
|---|---|---|---|
| C1 définition du champ | booléen stocké, calculé, readonly, manual, `depends` sur les deux champs | conforme | VERT |
| C2 location 7 jours | True (seuil **inclus**) | True | VERT |
| C3 location 6 j / 30 j | False / True | False / True | VERT |
| C4 prêt 7 j / 30 j | False / False (prêts **exclus**) | False / False | VERT |
| C5 genre vide, durée 0, durée −3 | False, sans erreur | False ×3 | VERT |
| C6 recalcul 6 j→7 j puis rental→loan | True puis False | False → True → False | VERT |
| C7 champs existants intacts, aucun doublon | 3 champs d'origine, XML-ID `lab_seed_*` conservés | 3 champs, 5 XML-ID `lab_seed_*` | VERT |
| C8 unicité | 1 champ, 1 XML-ID | champs=1 xmlids=1 | VERT |
| nettoyage | 0 donnée « — recette » résiduelle | 0 | VERT |

**9/9 vert, sortie 0.** Preuve : `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/preuves/09_qa_scenario_rejeu.txt`.

## Rouge avant, vert après

Sur la copie remise à l'état initial (champ supprimé), le scénario est **ROUGE**
(C1, sortie 1) : `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/preuves/01_scenario_avant.txt`.
Après `build_01_needs_review.py`, il est **VERT** 9/9 :
`changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/preuves/04_scenario_apres.txt`. Le scénario discrimine donc bien.

## Ce que ce passage RPC ne prouve pas

- Ni le rendu visuel, ni les droits d'un autre utilisateur (limite du transport RPC).
  Sans objet ici : **aucune vue** n'existe sur `x_lab_request` (0 avant, 0 après) et
  aucun droit n'a été touché — c'est exactement le périmètre demandé.
- Le champ reste invisible à l'écran : c'est le périmètre, pas un défaut. À reprendre
  si la release doit un jour l'afficher.

## Anomalie corrigée en cours de tâche (transparence)

La première version des deux scripts empaquetait un niveau de liste en trop dans
l'appel `execute_kw`, ce qui faisait échouer `read` et `unlink` par un
`TypeError: unhashable type: 'list'` côté serveur. Corrigé (signature explicite
`rpc(model, method, args, kwargs)`), puis **toute la séquence a été rejouée depuis
une copie remise à zéro** : les preuves conservées sont celles de la version corrigée.

## Verdict de la voie

**VERT** — les huit critères de comportement de la spec sont couverts par une exécution réelle.
