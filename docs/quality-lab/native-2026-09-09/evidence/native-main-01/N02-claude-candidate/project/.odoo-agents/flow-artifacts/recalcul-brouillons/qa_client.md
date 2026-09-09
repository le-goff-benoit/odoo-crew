# Fragment QA copie client — base synthétique `lab_client`

Copie locale synthétique, la seule autorisée par la demande. Aucune autre base
n'a été touchée ; aucune production n'est concernée.

## 1. État avant (`preuves/copie_01_avant.log`)

| id | nom | état | `snapshot_total` | total lignes actives | lignes annulées |
|---|---|---|---|---|---|
| 1 | LEGACY_DRAFT | draft | **999.0** | 20.0 | 1 / 2 |
| 2 | LEGACY_DONE | done | **777.0** | 20.0 | 1 / 2 |

## 2. Mise à jour du module sur la copie
`labctl update` → ✅ sans erreur (`preuves/copie_02_update.log`).

## 3. Reprise, deux passages (`preuves/copie_03…`, `copie_04…`)

| Passe | Sortie |
|---|---|
| 1 | `REPRISE brouillons=1 valides=1 modifies=1 valides_modifies=0` · `LEGACY_DRAFT 999.0 -> 20.0` · `LEGACY_DONE 777.0 (inchangé: True)` |
| 2 | `REPRISE brouillons=1 valides=1 modifies=0 valides_modifies=0` · `LEGACY_DRAFT 20.0 -> 20.0` · `LEGACY_DONE 777.0 (inchangé: True)` |

**Idempotence prouvée** : le second passage ne modifie aucune valeur (`modifies=0`).

## 4. Preuve indépendante d'absence d'écriture sur le validé
(`preuves/copie_06_write_date.log`, transactions distinctes → `write_date` est discriminant)

```
LEGACY_DRAFT  state=draft create=01:01:58.832535 write=01:07:16.627810 ecrit_apres_creation=True
LEGACY_DONE   state=done  create=01:01:58.832535 write=01:01:58.832535 ecrit_apres_creation=False
```

Le dossier validé n'a **jamais** été écrit depuis sa création, alors que le
brouillon l'a été : le contrôle est discriminant, pas un faux positif.

## 5. État après (`preuves/copie_05_apres.log`)
`LEGACY_DRAFT` = **20.0** (lignes annulées exclues) · `LEGACY_DONE` = **777.0** (intact).

## 6. Observation à arbitrer (non bloquante)
`write_date` de LEGACY_DRAFT porte l'horodatage de la **passe 2** : la reprise
réécrit un brouillon à l'identique quand rien ne change. L'idempotence exigée par
D-12 est fonctionnelle (mêmes valeurs, `modifies=0`) et elle est tenue ; en
revanche l'idempotence « au bit près » (aucune écriture du tout) n'est pas
garantie sur les brouillons. D-12 ne l'exige que pour les validés, où elle est
prouvée. Un garde-fou (comparaison avant écriture) est possible si l'humain le
souhaite — non fait ici : hors spec, et comparer des `Float` sans `digits`
apporterait son propre risque.

Droits, comptabilité et facturation : **hors périmètre**, aucun fichier de
sécurité ni modèle comptable touché (diff vérifié).

## Verdict de voie
**VERT** — reprise conforme, idempotente, validés intacts.
