# Revue fonctionnelle — recalcul des dossiers logistiques en brouillon

**Projet** work (Entrepôt Silex) · **série** 19.0 (origine : `lab_dispatch/__manifest__.py`) · **modules concernés** `lab_dispatch`

## 1. Ce que je comprends

En tant que gestionnaire d'entrepôt, je veux que le recalcul d'un dossier
logistique reflète les seules lignes encore actives, sans jamais toucher un
dossier déjà validé, afin que les totaux figés restent des références fiables.

**Problème réel** : `action_recalculate` (`lab_dispatch/models/business.py:13`) a
deux défauts cumulés, prouvés sur la copie synthétique `lab_client` :

| Dossier | État | `snapshot_total` en base | Total toutes lignes | Total lignes actives |
|---|---|---|---|---|
| `LEGACY_DRAFT` (id 1) | brouillon | 999.0 | 110.0 | **20.0** |
| `LEGACY_DONE` (id 2) | validé | 777.0 | 110.0 | 20.0 |

1. la somme porte sur **toutes** les lignes, y compris `cancelled=True` (110 au
   lieu de 20) ;
2. la méthode écrit sur **tous** les enregistrements de `self`, donc écrase le
   total figé d'un dossier validé (777 → 110).

Les deux dossiers portent en plus un `snapshot_total` faux hérité de l'historique
(999 et 777) : la correction du code ne suffit pas, il faut une reprise.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER (correction d'un défaut du custom)**

`lab.dispatch`, `lab.dispatch.line`, `snapshot_total` et `action_recalculate`
n'existent que dans `lab_dispatch` — aucune occurrence dans les 625 addons de
`~/odoo-sources/19.0/addons`. Il n'y a rien à configurer : le comportement
attendu est celui d'une méthode custom mal écrite. Aucun autre code du projet
n'appelle `action_recalculate` ni ne lit `snapshot_total` (grep sur `/work`).

**Série suivante** : sans objet, modèle entièrement custom ; rien à calquer sur
un futur standard.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : le défaut est dans du code Python | — | non |
| Studio / configuration en base | — | impossible : Studio ne surcharge pas une méthode et n'a pas de test Python | — | non |
| Code custom (`odoo-developer`) | faible (une méthode + tests + script de reprise) | recalcul conforme à D-12 et données existantes assainies | nul (le module est déjà custom) | **oui** |

Profil du projet : un module custom, aucun Studio → voie module, conforme au
tableau du rôle.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | majeure (levée) | `JOURNAL.md` 2026-08-01 (D-11) demande de recalculer **tous** les dossiers, validés compris | contredit frontalement D-12 | D-12 (2026-09-08, Marc Colin) est postérieure et explicite : elle prime. Les validés sont définitivement figés ; on ne rejoue pas D-11. Consigné dans `PROJECT.md`. |
| 2 | majeure | « pas même recomputé » pour un validé | un `record.snapshot_total = <même valeur>` reste une écriture (`write_date` bouge, tout `compute`/`onchange`/règle en aval se déclenche) | filtrer sur `state == 'draft'` **avant** toute écriture, pas comparer après |
| 3 | moyenne | sélection mixte brouillons + validés | une exception ferait échouer le lot entier côté utilisateur | ignorer silencieusement les validés, aucun `UserError` |
| 4 | moyenne | reprise des données existantes | rejouée deux fois, elle ne doit rien changer de plus ; elle ne doit jamais toucher un validé | reprise = appel de la méthode corrigée sur les seuls brouillons ; idempotence prouvée par double passage avec comptages avant/après |
| 5 | mineure | `quantity`/`price` sont des `Float` sans `digits` | arrondi non maîtrisé sur de gros volumes | hors périmètre de D-12, signalé comme dette, non corrigé ici |
| 6 | mineure | pas de vue ni d'action XML dans le module | l'action n'est appelable que par code/RPC | conforme au projet synthétique, hors périmètre |

**Non-dits vérifiés** : pas de multi-société ni de multi-devise sur ces modèles ;
`state` n'a que `draft` et `done` ; aucun droit ne change (D-12) ; aucune
transformation d'état (un validé ne redevient pas brouillon).

## 5. Questions bloquantes

Aucune. D-12 tranche Q1 (validés figés) et Q2 (lignes annulées exclues).

## 6. Spécification

`lab.dispatch.action_recalculate` :

- ne traite que les enregistrements de `self` dont `state == 'draft'` ;
- pour ceux-là, `snapshot_total = Σ (quantity × price)` sur les lignes dont
  `cancelled` est faux ;
- n'effectue **aucune** écriture sur un dossier `done`, pas même identique ;
- ne lève aucune erreur sur une sélection mixte ou vide ; retourne `True`.

Reprise des données existantes sur la copie `lab_client` : appel de la méthode
corrigée sur les seuls dossiers `draft`, idempotent, avec comptages avant/après.

### Critères d'acceptation

| # | Critère | Testable par |
|---|---|---|
| CA1 | Un brouillon obtient la somme des lignes non annulées (lignes annulées exclues) | test Python |
| CA2 | Un dossier validé garde son `snapshot_total` **et** son `write_date` (aucune écriture) | test Python |
| CA3 | Une sélection mixte recalcule les brouillons, ignore les validés, sans exception | test Python |
| CA4 | Deux appels consécutifs donnent le même résultat (idempotence de la méthode) | test Python |
| CA5 | Sur la copie `lab_client` : `LEGACY_DRAFT` 999 → 20 ; `LEGACY_DONE` reste 777 ; second passage sans aucun changement | reprise outillée, comptages avant/après |

**Hors périmètre** : arrondi/`digits` des `Float`, vues et actions, droits,
version du manifest (incrémentée à la clôture de la release).

## 7. Ce que l'utilisateur verra

Aucun écran ne change. Seuls les totaux des dossiers en brouillon sont corrigés
(exclusion des lignes annulées) ; les dossiers validés sont désormais protégés
contre tout recalcul.

## 8. Verdict et voie

**Spec saine → CONTINUE**, voie **module** (`odoo-developer`).
Transition **`module_high_risk`** : la tâche modifie des **données existantes**
(reprise sur la copie), donc la QA renforcée avec validation sur la copie client
est obligatoire immédiatement, release ouverte ou non.
