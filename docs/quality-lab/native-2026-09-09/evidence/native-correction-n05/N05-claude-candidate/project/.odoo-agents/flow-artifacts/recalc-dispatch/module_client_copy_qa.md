# Fragment QA — voie copie client (données existantes)

**Base** `lab_client` (copie synthétique, seule base autorisée par D-12) · **série** 19.0

Voie obligatoire : la tâche touche des **données existantes**. Validée immédiatement,
sans attendre la clôture.

## État avant reprise — `preuves/03_copie_avant.log`
| id | dossier | état | `snapshot_total` | `write_date` |
|---|---|---|---|---|
| 1 | LEGACY_DRAFT | draft | 999.0 | 01:20:16.855012 |
| 2 | LEGACY_DONE | done | 777.0 | 01:20:16.855012 |
| 3 | LEGACY_FRACTION | draft | 20.004 | 01:20:16.855012 |

## Passage 1 — mise à jour du module — `preuves/04_reprise_passage1.log`, `05_copie_apres_passage1.log`
`odoo.modules.migration: module lab_dispatch: Running upgrade [19.0.1.0.1>] post-recalcul_brouillons`
puis `reprise des totaux de brouillons — 2 dossier(s) repris ['LEGACY_DRAFT', 'LEGACY_FRACTION']`.

| id | dossier | état | `snapshot_total` | `write_date` |
|---|---|---|---|---|
| 1 | LEGACY_DRAFT | draft | **20.0** | 01:25:37.917950 (écrit) |
| 2 | LEGACY_DONE | done | **777.0** | **01:20:16.855012 — inchangée** |
| 3 | LEGACY_FRACTION | draft | **20.0** | 01:25:37.917950 (écrit) |

L'écart de 0,004 de LEGACY_FRACTION a bien été repris : aucune tolérance d'arrondi n'a
été introduite, le contrat n'en fixe aucune.

## Passage 2 — rejeu — `preuves/06_reprise_passage2_idempotence.log`
Rejeu de `_repair_draft_snapshots()` dans une **transaction distincte** :

- `dossiers repris : 0 []`
- `ids ayant recu un write : []` (espion posé sur `write`)
- les trois `write_date` sont **identiques** à celles du passage 1 — comparaison probante
  ici, contrairement à un test unitaire, puisque les deux passages sont dans des
  transactions différentes.

La portée prouvée est donc bien l'**absence d'écriture**, pas seulement l'égalité des
montants : compteur à 0, aucun `write`, aucune `write_date` déplacée.

## Sélection mixte sur la copie — `preuves/07_selection_mixte_copie.log`
Appel du bouton sur les 3 dossiers à la fois (2 brouillons + 1 validé), puis `rollback` :

- `erreur levee : None` · `retour : True`
- `ids ayant recu un write : [1, 3]` — le validé (id 2) **n'est pas dans la liste**
- LEGACY_DONE : `snapshot=777.0`, `state=done`, `write_date` d'origine ; `valide intact : True`
- son total D-12 *s'il avait été recalculé* serait 20.0 : l'écart de 757 entre 777.0 et
  20.0 est la preuve directe que la valeur affichée n'a pas été recomputée.

Cette vérification a été **annulée par rollback** : la copie reste dans l'état du passage 1.

**Observation transmise à la jointure** : sur un brouillon déjà juste, le bouton réécrit
quand même la valeur (ids 1 et 3 écrits alors que les montants ne changent pas). C'est
conforme au contrat — D-12 n'impose l'absence d'écriture que pour les validés — et c'est
un comportement de bouton attendu par l'utilisateur. La reprise automatique, elle, n'écrit
jamais sans écart : la distinction est délibérée.

**Verdict de la voie copie client : VERT.**
