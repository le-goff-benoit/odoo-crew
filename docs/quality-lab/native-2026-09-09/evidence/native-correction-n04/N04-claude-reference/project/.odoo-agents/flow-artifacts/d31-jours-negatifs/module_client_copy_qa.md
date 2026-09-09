# Fragment QA copie client — tâche 1 (D-31)

**Base** `lab_client` (copie synthétique du laboratoire, écriture permise et annoncée) · **module** `lab_rental` · **série** 19.0
Niveau **renforcé** exigé par la revue : la règle porte sur des données existantes (durées négatives historiquement tolérées, journal du 2026-08-01).

## 1. Mise à niveau sur la copie
`labctl update` → `Module lab_rental loaded in 0.04s`, `21 modules loaded`, `Registry loaded`, sortie 0
(`qa_tache1_copie_update.log`). Aucun message d'échec d'ajout de contrainte dans le log ; les seuls WARNING
liés au module sont les 3 « Missing `author` key in manifest » (dette antérieure).

## 2. La contrainte est-elle réellement en base ?
C'est le risque n°1 de la revue : PostgreSQL refuse un `ALTER TABLE ... ADD CONSTRAINT` si des lignes le violent,
et Odoo se contente d'un avertissement — le module s'installe sans être protégé.

```
CONTRAINTES CHECK: [('lab_rental_check_days_positive', 'CHECK ((days >= 0))')]
LIGNES NEGATIVES RESTANTES: 0
```
Avant la tâche, `pg_constraint` ne portait que `lab_rental_pkey` et les deux clés étrangères
(`inventaire_copie.py`, voie analyste). La contrainte est donc bien **posée**, pas seulement écrite dans le code.

## 3. Données existantes
`SELECT count(*) FROM lab_rental` → **0** avant comme après. Aucune ligne à reprendre, aucune donnée à corriger,
aucune donnée perdue. La tolérance historique du journal 2026-08-01 n'a laissé aucune trace dans cette copie.

## 4. Comportement vérifié sur la copie (et non sur la seule base de test)
| Scénario | Résultat observé |
|---|---|
| Création `days = -2` | **refusée** — `violates check constraint "lab_rental_check_days_positive"` |
| Écriture `days = -5` sur une location valide | **refusée** — même contrainte |
| État de la location valide après les deux refus | `days = 4`, `amount_total = 40.0` — **inchangés** |
| Création `days = 0` | **acceptée**, `amount_total = 0.0` |
| Message rendu à l'utilisateur (`_sql_error_to_message`) | « Le nombre de jours d'une location ne peut pas être négatif. » |

Preuves : `qa_tache1_copie_verification.log`, `qa_tache1_copie_message.log`.

## 5. Droits et écrans
`security/ir.model.access.csv` non touché ; aucune vue dans le module ; aucun groupe créé ou modifié.
Rien à vérifier côté habilitations, conformément à la consigne « aucun écran ni droit à modifier ».

## 6. Nettoyage derrière l'intervention
Les enregistrements créés pour la vérification ont été retirés ; la copie est laissée à **0 ligne `lab_rental`**,
son état d'origine (`qa_tache1_copie_nettoyage.log`, puis `LIGNES DANS LA COPIE: 0`).

## Verdict de la voie
**VERT** — contrainte présente en base sur la copie, refus prouvés sur la copie elle-même, zéro reprise de données,
copie rendue dans son état initial.
