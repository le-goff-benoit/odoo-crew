# Fragment QA — voie copie client (module_client_copy_qa)

Copie locale synthétique `lab_client` (données fictives, aucune donnée client). Voie
**obligatoire** ici : la tâche reprend des **données existantes**.

## Avant (`cohorte_avant.json`)
| id | nom | state | ordered | delivered | prepared | manual |
|---|---|---|---|---|---|---|
| 1 | LEGACY_AUTO | draft | 10 | 3 | **999** | non |
| 2 | LEGACY_MANUAL_ZERO | draft | 10 | 0 | 0 | oui |
| 3 | LEGACY_MANUAL_PARTIAL | draft | 10 | 3 | 2 | oui |
| 4 | LEGACY_DONE | done | 10 | 4 | 88 | non |

## Mise à niveau
`/bridge/labctl update` → `module lab_preparation: Running upgrade [19.0.1.1.0>] post-migrate`,
`Modules loaded`, aucune erreur. Le script de reprise appelle exactement `_cron_prepare()`.

## Après (`cohorte_apres.json`)
| id | prepared | écart |
|---|---|---|
| 1 | **7.0** | 999 → 7 (= max(10-3, 0)) |
| 2 | 0.0 | **aucun** |
| 3 | 2.0 | **aucun** |
| 4 | 88.0 | **aucun** |

Nombre d'enregistrements avant/après : 4 / 4 — aucune création, aucune suppression.

## Absence d'écriture, pas seulement absence d'écart
`write_date` relevée après reprise (`write_date_apres_reprise.json`) :
id 1 → `2026-09-15 22:54:59` (écrit par la migration) ; ids 2, 3, 4 → `2026-09-15 22:49:56`,
c'est-à-dire leur valeur d'origine. Les saisies manuelles et le `done` n'ont donc subi
**aucun `write`**, et pas seulement aucun changement de valeur.

## Rejeu
`_cron_prepare()` rejoué sur `lab_client` : valeurs identiques (7 / 0 / 2 / 88), ids 2, 3, 4
conservent leur `write_date` d'origine.
**Limite prouvée et annoncée** : l'idempotence est établie **sur les valeurs et sur l'absence
d'écriture des enregistrements hors périmètre**. Elle ne l'est pas sur la `write_date` des
drafts automatiques : id 1 est réécrit à chaque passage (`write_date` 22:55:25 au second tour)
avec la même valeur, car le code réaffecte sans comparer. Conforme à la lettre de N-17
(« rejouer le cron est idempotent » porte sur le résultat), mais à signaler si la piste d'audit
compte pour le métier.

**Verdict de la voie** : vert, avec la limite d'idempotence ci-dessus explicitement énoncée.
