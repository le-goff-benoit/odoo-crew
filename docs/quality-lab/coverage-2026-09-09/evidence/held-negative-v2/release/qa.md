# QA — release 2026-09-09_04_import

## 2026-09-09 — I7, import atomique d'étiquettes — mode tâche (risque renforcé)

**Série** 19.0 (origine : `.odoo-agents/config`) · **module** fixture-i7 · **flow** `d31-jours-negatifs`, nœud `module_high_gate` (jointure des trois voies)

### Verdict
**REFUSÉ** — le critère I7 n'est pas prouvé : aucune des trois voies n'a relevé les identifiants ni les valeurs des huit étiquettes préexistantes, et le manque ne peut pas être comblé ici (aucune base ni exécution Odoo disponible dans cet exercice de consolidation).

### Nature des preuves
Les trois fragments sont des attestations produites par les voies QA du flow ; ils sont repris ici **tels quels** comme preuves d'entrée. Aucun contrôle n'a été rejoué à la jointure : la consolidation ne fait que confronter ces fragments aux critères.

### Résultats d'exécution (relevés dans les fragments, non rejoués)
| Contrôle | Résultat | Détail | Voie |
|---|---|---|---|
| Lint ciblé | vert | lint ciblé propre, diff relu sans anomalie | statique (`static.md`) |
| Relecture du diff | vert | savepoint présent autour du lot | statique (`static.md`) |
| Installation / mise à jour | vert | install + update OK, base `qa_i7`, build `i7-1` | exécution (`runtime.md`) |
| Tests ciblés | vert | 0 failed, 0 errors of 2 tests | exécution (`runtime.md`) |
| Message d'erreur ligne 3 | vert | `ValidationError("Ligne 3 : libellé obligatoire")` observé en RPC | exécution (`runtime.md`), confirmé sur copie (`client.md`) |
| Comptage avant / après | 8 → 8 | `count()` seul | exécution + copie |
| Identifiants et valeurs des 8 étiquettes | **non relevé** | aucune voie ne les a lus, ni avant ni après | les trois |
| Recherche des lignes du lot importé | **non faite** | aucune voie ne les a cherchées après l'échec | les trois |
| Copie client | jouée, mais non contributive sur le point manquant | même code `fixture-i7`, même build `i7-1`, base `copy_i7` | copie (`client.md`) |

### Anomalies bloquantes
#### B1 — Le critère I7 est prouvé par un comptage, or un comptage ne prouve pas l'absence d'écriture
**Constat** — Les trois voies concluent « VERT proposé » sur I7 à partir de `count()` avant = après = 8. `static.md` dit explicitement « aucun test des valeurs d'étiquettes », `runtime.md` « le test ne compare ni les identifiants ni les valeurs », `client.md` « aucun relevé des identifiants ou valeurs avant/après, aucune recherche des lignes du lot importé ».
**Conséquence** — Un cardinal invariant est compatible avec plusieurs scénarios que I7 interdit : quatre lignes du lot conservées en regard de quatre préexistantes supprimées ; huit étiquettes recréées avec de nouveaux identifiants ; huit étiquettes dont des valeurs ont été écrasées. Le critère I7 exige « exactement leurs identifiants et valeurs » : ce n'est pas ce qui a été mesuré. C'est la leçon du rôle QA — un compteur ne prouve pas zéro écriture.
**Correctif** — Relever, sur la copie, l'ensemble `(id, valeurs)` des huit étiquettes avant l'import puis après l'échec et comparer terme à terme ; chercher explicitement les quatre lignes du lot (par leur clé fonctionnelle) et prouver qu'aucune n'est présente. Tant que ce relevé n'existe pas, I7 reste non satisfait.

#### B2 — La voie copie client conclut au-delà de ce qu'elle a mesuré
**Constat** — `client.md` : « la voie considère le comptage suffisant pour proposer l'absence de modification des données ; aucune autre preuve disponible ».
**Conséquence** — Un « VERT proposé » est présenté sur une inférence, non sur une observation. Le niveau renforcé existe précisément pour que la copie client couvre les données existantes : ici elle ne les couvre pas, et l'annoncer vert masquerait l'angle mort au lieu de le signaler.
**Correctif** — La voie copie doit produire le relevé `(id, valeurs)` demandé en B1, ou déclarer le critère non couvert.

### Remarques
- **R1 — Les voies exécution et copie ne sont pas indépendantes sur ce point.** Même révision `fixture-i7`, même build `i7-1` ; la copie rejoue le même contrôle sur une autre base. Elle vaut comme contrôle sur données réelles, mais elle ne compense pas l'absence de relevé : les deux voies partagent le même angle mort.
- **R2 — Le savepoint relevé en statique n'est pas une preuve d'atomicité.** `static.md` constate sa présence dans le code ; sa portée effective au moment du rollback reste à observer à l'exécution.
- **R3 — Le message d'erreur est, lui, réellement prouvé** : observé en RPC sur `qa_i7` et confirmé sur `copy_i7`. C'est la seule des trois conditions de I7 qui soit établie.

### Couverture des critères d'acceptation
| Critère | Couvert par | État |
|---|---|---|
| **I1** — installation, mise à jour et lint ciblé sans régression | `static.md` (lint ciblé propre, diff relu) + `runtime.md` (install/update OK, 2/2 tests ciblés) | **couvert** |
| **I7** — message ligne 3, aucune ligne du lot conservée, huit étiquettes intactes en identifiants et valeurs | `runtime.md` + `client.md` pour le message uniquement | **partiel** — condition 1 prouvée ; condition 2 seulement suggérée par un comptage ; condition 3 non mesurée |

Contrat lié : `changelog/2026-09-09_04_import/coverage.json` (`odoo-qa-coverage/1`, empreinte `51fe4d13`).

### Non testé / angles morts
- Identifiants et valeurs des huit étiquettes préexistantes, avant et après l'import échoué.
- Présence ou absence des quatre lignes du lot après le rollback (aucune recherche par clé fonctionnelle).
- Portée réelle du savepoint à l'exécution.
- Suite complète du module, tours, désinstallation, mise à niveau : hors périmètre d'une QA de tâche, à jouer à la clôture.

### Appris (pour le journal)
- Trois voies vertes ne font pas un verdict vert : la jointure doit lire ce que chaque voie déclare **ne pas** avoir mesuré, pas seulement sa conclusion.
- Sur un critère de préservation de données, exiger le relevé `(id, valeurs)` avant/après dès la consigne de la voie copie ; sinon les trois voies convergent sur le même angle mort.
