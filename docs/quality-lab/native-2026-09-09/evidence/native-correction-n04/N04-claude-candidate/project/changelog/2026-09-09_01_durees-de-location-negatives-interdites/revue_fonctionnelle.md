# Revue fonctionnelle — Interdire les durées de location négatives (D-31)

**Projet** work (Éole, coopérative synthétique) · **série** 19.0 (origine : `__manifest__.py`)
**Module** `lab_rental` · **Modèle** `lab.rental` · **Analyste** claude-odoo-analyst · **Date** 2026-09-09

## Demande

Interdire les jours négatifs sur `lab.rental` par une **contrainte SQL Odoo**, en
conservant les jours nuls valides et le calcul de total existant. Tests attendus :
création refusée, modification refusée, et conservation d'une location valide
après un rejet.

## Verdict : SPEC SAINE → développement, voie module custom

Le contrat est entièrement arbitré par la décision **D-31** (Luc Roy,
`decisions/2026-09-08.md`). Aucune question bloquante ne subsiste.

| Question | Arbitrage D-31 |
|---|---|
| Q1 — la borne zéro est-elle valide ? | **Oui, zéro autorisé** → contrainte `days >= 0`, pas `> 0` |
| Q2 — type de contrainte | **SQL** explicitement demandée (pas de `@api.constrains` Python) |
| `daily_rate`, `amount_total` | **Inchangés** : total = jours × tarif, aucune règle nouvelle |
| Périmètre | Aucune facturation, aucune mise en production |

## Le standard couvre-t-il le besoin ?

Non. `fields.Integer` n'offre aucune borne inférieure déclarative en 19.0 ; la
borne est à écrire. La forme 19.0 est `models.Constraint('CHECK (…)', "<message>")`
en attribut de classe — `_sql_constraints` a disparu de la série (SERIES_MATRIX,
confirmé dans `odoo/orm/table_objects.py:79`). Une contrainte SQL est le bon
outil ici : garde-fou au niveau base, non contournable par un `write` SQL de l'ORM.

## Voie retenue

**Module custom** (`odoo-developer`). Le projet est déjà un module ; Studio ne
sait pas poser une contrainte SQL.

## Périmètre

**Dans** : `lab_rental/models/business.py` (une contrainte), tests unitaires
(`lab_rental/tests/`), manifest si un dossier de tests doit être déclaré.

**Hors** : aucune vue, aucun droit, aucun champ nouveau, aucune modification du
compute `_compute_amount_total`, aucune donnée. Explicitement demandé : « aucun
écran ni droit à modifier ».

## Contradictions et hypothèses retenues

1. **Contradiction mineure avec l'historique du projet** — `JOURNAL.md` (2026-08-01)
   note que « les durées négatives étaient anciennement permises pour des essais ».
   D-31 remplace cette tolérance ; c'est la décision la plus récente et elle est
   explicite. *Retenu : on applique D-31.*
2. **Risque d'installation (vérifié, levé)** — un `ADD CONSTRAINT` échoue si des
   lignes existantes le violent, ce qui aurait bloqué la mise à niveau à cause de
   ces essais historiques. Relevé sur la copie `lab_client` le 2026-09-09 :
   `select count(*) from lab_rental` → **0 ligne**, dont **0 négative**, aucune
   contrainte CHECK préexistante. *La mise à niveau passe ; à re-vérifier sur une
   base réelle si le module sortait du laboratoire.*
3. **Message d'erreur** — D-31 ne le fixe pas. *Retenu : message métier en français,
   passé en second argument de `models.Constraint`, sans quoi l'utilisateur reçoit
   l'erreur Postgres brute.*
4. **Portée** — la contrainte s'applique aux deux `kind` (`rental` et `loan`) :
   D-31 dit « lab.rental.days >= 0 » sans distinction. *Retenu tel quel.*

## Critères d'acceptation

| # | Critère |
|---|---|
| C1 | Une création avec `days < 0` est refusée par la base (`IntegrityError`) |
| C2 | Une modification portant `days` à une valeur négative est refusée |
| C3 | `days = 0` reste valide, création et modification |
| C4 | `days > 0` reste valide et `amount_total` vaut toujours jours × tarif |
| C5 | Après un rejet, une location valide créée avant subsiste intacte (transaction utilisable) |
| C6 | La contrainte est bien une contrainte SQL au niveau table (visible dans `pg_constraint`) |
| C7 | Aucune vue, aucun droit, aucun autre comportement modifié |

## Ce que l'utilisateur verra

Rien de nouveau à l'écran. Seul changement perceptible : saisir un nombre de
jours négatif fait apparaître un message d'erreur au lieu d'être accepté
silencieusement. Aucune capture à produire (pas de vue dans ce module).
