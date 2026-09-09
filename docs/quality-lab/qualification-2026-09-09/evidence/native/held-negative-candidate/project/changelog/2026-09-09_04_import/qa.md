# QA — release 2026-09-09_04_import

## 2026-09-09 — J73 import atomique — mode tâche (QA renforcée, jointure des trois voies)

**Série** 19.0 (origine : `.odoo-agents/config`) · **révision** fixture-j73 · **build** j73-1

### Verdict
**REFUSÉ — À REPRENDRE** — le critère J73 n'est pas satisfait : la seule réponse
d'exécution citée nomme la ligne 3 alors que la ligne invalide est la 5, et ni les
identifiants ni les valeurs des huit étiquettes préexistantes n'ont été relevés.
Les trois voies proposaient VERT ; la jointure ne les suit pas.

Réception structurée (contrat lié, statuts et empreintes) :
[`reception_j73.md`](reception_j73.md) · couverture : [`coverage_j73.json`](coverage_j73.json).

### Preuves d'entrée
Les trois fragments ci-dessous sont les preuves d'entrée de cette jointure ;
aucune base ni exécution Odoo n'était disponible à ce stade, aucun contrôle
nouveau n'a été joué ici.

| Voie | Fragment | Ce qu'elle établit | Ce qu'elle n'établit pas |
|---|---|---|---|
| statique | `static.md` | lint ciblé propre, diff relu, savepoint présent autour du lot | aucun test des valeurs d'étiquettes |
| exécution | `runtime.md` | install/update OK, 2/2 tests ciblés, import joué, `count()` 8 → 8 | ne compare ni identifiants ni valeurs ; message observé « Ligne 3 » |
| copie client | `client.md` | `count()` avant/après = 8 | aucun relevé d'identifiants ou de valeurs, aucune recherche des lignes du lot |

### Anomalies bloquantes

#### B1 — Le message d'erreur désigne la ligne 3 au lieu de la ligne 5
**Constat** — `runtime.md` cite la réponse RPC observée :
`ValidationError("Ligne 3 : libellé obligatoire")`, pour un lot dont la ligne
invalide est la 5. C'est la seule citation littérale d'un message dans les trois
fragments.
**Conséquence** — le critère J73 exige que le message reçu indique la ligne 5.
L'utilisateur qui corrige son fichier ira modifier la mauvaise ligne. Le décalage
(3 au lieu de 5) est la signature d'un compteur qui numérote les lignes du lot
en cours de traitement, ou qui repart après les en-têtes, plutôt que la ligne du
fichier source.
**Correctif** — propager le numéro de ligne source jusqu'au message, et couvrir
le cas par un test qui assert le texte exact, pas seulement le type d'exception.

#### B2 — Contradiction non levée entre la voie exécution et la voie copie
**Constat** — `client.md` affirme « Message ligne 5 confirmé » sur le **même code
fixture-j73 et le même build j73-1** que `runtime.md`, qui a observé « Ligne 3 ».
Deux voies ne peuvent pas observer deux messages différents du même binaire sur
le même scénario. `client.md` ne cite pas le message qu'elle a lu.
**Conséquence** — la jointure retient l'observation étayée (citation littérale de
la réponse RPC) et traite l'affirmation non citée comme non prouvée : on ne retire
pas un diagnostic étayé sur la foi d'un constat indirect. La contradiction reste
ouverte tant que la copie n'a pas produit le texte qu'elle a réellement reçu.
**Correctif** — rejouer le scénario sur la copie en consignant le message reçu
mot pour mot ; si les deux textes divergent réellement, chercher la différence de
build ou de données avant toute correction de code.

#### B3 — L'atomicité n'est pas prouvée : `count()` n'est pas un oracle
**Constat** — les deux voies d'exécution ne disposent que de `count()` avant = 8
et après = 8. Aucune n'a relevé les identifiants ni les valeurs des huit
étiquettes préexistantes, ni recherché les lignes du lot importé.
**Conséquence** — un comptage identique est compatible avec plusieurs scénarios
non conformes : quatre lignes créées puis quatre préexistantes supprimées,
réécriture en place des valeurs des huit étiquettes, ou recréation avec de
nouveaux identifiants. Le critère J73 exige « exactement leurs identifiants et
valeurs » — un compteur ne prouve pas zéro écriture.
**Correctif** — relever avant/après la liste `(id, valeurs)` des huit étiquettes
et la comparer terme à terme, puis vérifier par une recherche que les quatre
lignes du lot sont absentes après l'échec.

### Remarques
- Le savepoint constaté en relecture statique (`static.md`) est un indice
  d'intention, pas un oracle : il ne dit rien de ce que le code exécute autour.
- Les tests ciblés sont verts (2/2) mais aucun ne porte sur les valeurs ni sur
  les identifiants : la suite ne peut pas détecter B1 ni B3 en l'état.

### Couverture des critères d'acceptation
| Critère | Couvert par | État |
|---|---|---|
| I1 — installation, mise à jour, lint ciblé sans régression | `static.md` (lint ciblé propre), `runtime.md` (install/update OK, 2/2 tests) | **covered** |
| J73 — message ligne 5, aucune ligne du lot conservée, huit étiquettes intactes (identifiants et valeurs) | `runtime.md`, `client.md`, `static.md` | **failed** — message observé « Ligne 3 » (B1), lot non recherché, identifiants et valeurs non relevés (B3) |

### Non testé / angles morts
- Identifiants et valeurs des huit étiquettes préexistantes, avant et après l'échec.
- Présence ou absence des quatre lignes du lot après le rollback (aucune recherche).
- Texte exact du message sur la copie client (jamais cité).
- Hors périmètre acté par la revue : aucun écran, aucun PDF, aucune capture.

### Appris (pour le journal)
- Trois voies vertes ne font pas un verdict vert : ici deux d'entre elles
  concluent sur un `count()` qui ne teste aucune des conditions du critère.
- Un critère composé se réceptionne condition par condition ; une seule
  citation littérale a suffi à contredire deux propositions de VERT.
