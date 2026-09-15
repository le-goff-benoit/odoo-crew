# Revue fonctionnelle — Préparation périodique, duplication et reliquat (décision N-17)

**Projet** work (Atelier Nacre, synthétique) · **série** 19.0 · **modules concernés** `lab_preparation`
**Source du contrat** : `decisions/current.md` (décision N-17 confirmée) · **demande** : `demande.md`

## 1. Ce que je comprends
En tant que gestionnaire de préparation, je veux que le traitement périodique ne recalcule que
les préparations automatiques encore en brouillon, afin que mes saisies explicites (y compris
un zéro volontaire) et les préparations terminées ne soient jamais écrasées.
Périmètre : les trois points d'entrée du modèle `lab.preparation` — `_cron_prepare`, la
duplication `copy()`, `action_remainder()` — plus la reprise des données déjà en base.

**Problème réel** : le code en place écrase des données. Sur la copie synthétique `lab_client`,
`_cron_prepare` parcourt `search([])` sans filtre : il réaffecte `prepared_qty = ordered_qty`
sur les enregistrements manuels **et** sur les `done`. Cohorte relevée le 2026-09-16
(preuve : `.odoo-agents/flow-artifacts/preparation-n17/cohorte_avant.json`) :

| id | nom | state | ordered | delivered | prepared | manual | ce que le code actuel en fait |
|---|---|---|---|---|---|---|---|
| 1 | LEGACY_AUTO | draft | 10 | 3 | **999** | non | valeur fausse à reprendre (attendu 7) |
| 2 | LEGACY_MANUAL_ZERO | draft | 10 | 0 | 0 | oui | zéro volontaire, écrasé à 10 par le cron |
| 3 | LEGACY_MANUAL_PARTIAL | draft | 10 | 3 | 2 | oui | saisie écrasée à 10 par le cron |
| 4 | LEGACY_DONE | done | 10 | 4 | 88 | non | figé attendu, écrasé à 10 par le cron |

Le cas 1 montre aussi que la donnée existante est déjà corrompue : la reprise fait partie de la demande.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** — et c'est explicitement borné par la décision N-17 : « ce modèle synthétique
de préparation **n'est pas** `stock.picking` ». Le standard de préparation/reliquat existe bien
(`~/odoo-sources/19.0/addons/stock/models/stock_move.py` : `quantity` l.171, `picked` l.121 ;
mécanique de backorder dans `addons/stock/wizard/stock_backorder_confirmation.py`), mais il porte
un autre cycle de vie et n'est pas applicable ici par décision actée. Aucun `prepared_qty` ni
`_cron_prepare` n'existe dans les sources 19.0 (`grep -rn "prepared_qty\|_cron_prepare"
$S/addons/*/models/*.py` → 0 occurrence).
**Série suivante** : rien de comparable ajouté en 19.1/19.4 sur ce modèle synthétique ; pas de
risque de doublon à la migration.

## 3. Voies possibles
Une seule voie réelle : **module** (`lab_preparation` existe déjà, le projet n'a aucun Studio et
la correction porte sur des méthodes Python surchargées — hors capacité Studio). Configuration et
Studio sont écartés : ni l'un ni l'autre ne peut corriger `copy()` ou une méthode de cron.

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | Majeur | `action_set_manual` fait `manual = bool(quantity)` | Une saisie manuelle à **zéro** laisse `manual=False` : le cron la réécrase au tour suivant. Contredit « zéro valide » de N-17. | `manual = True` inconditionnel. |
| 2 | Majeur | `_cron_prepare` fait `search([])` et `prepared_qty = ordered_qty` | Écrase saisies manuelles et `done` ; ignore `delivered_qty` ; peut produire un négatif si livré > commandé. | Domaine `state=draft` + `manual=False`, valeur `max(ordered-delivered, 0)`. |
| 3 | Majeur | `copy()` non maîtrisée | Duplique `delivered_qty`, `prepared_qty` et `manual` : la « nouvelle demande » naît avec un passé qui n'est pas le sien. | `copy=False` sur `delivered_qty`, `prepared_qty`, `manual` ; `state` retombe sur son défaut `draft`. |
| 4 | Majeur | `action_remainder` délègue à `copy()` | Reporte `ordered_qty` intégral au lieu du reste, ne passe pas la source en `done`, crée une ligne même sans reste positif. | Création explicite, sous condition de reste strictement positif. |
| 5 | Mineur | Données existantes déjà fausses (id 1 : `prepared_qty=999`) | Corriger le code ne répare pas la base. | Reprise par script de migration `post-migrate`, strictement limitée au périmètre autorisé. |
| 6 | Mineur | Aucun enregistrement `ir.cron` n'est livré par le module | La « préparation périodique » n'a pas de déclencheur en base. | **Hors périmètre** : N-17 ne le demande pas (« aucun autre comportement à inventer »). Signalé pour arbitrage ultérieur. |

Effets de bord vérifiés : modèle sans multi-société, sans devise, sans `active`, sans vue ni
rapport (le module ne livre que le modèle et son `ir.model.access.csv`) ; aucun autre module du
projet ne dépend de `lab.preparation`. Aucun impact compta/facturation/droits.

## 5. Questions bloquantes
Aucune. La décision N-17 tranche le contrat ; la demande est saine.

## 6. Hypothèses retenues (à défaut de réponse)
- **H1 — `action_remainder()` sans reste positif** : N-17 énonce « elle passe la source done »
  comme une propriété de la méthode, et ne conditionne que la **création** au reste positif
  (« crée **si le reste est positif** … » ; « si aucun reste positif, elle retourne un recordset
  vide **sans créer de ligne** »). Hypothèse retenue : la source passe `done` dans les deux cas,
  sans que sa `prepared_qty` soit touchée ; seule la création est conditionnelle. À confirmer par
  le métier — c'est le seul point du contrat qui supporte deux lectures.
- **H2 — reste calculé** : `ordered_qty - delivered_qty`, cohérent avec la formule du cron.
- **H3 — nom du reliquat** : le suffixe ` remainder` existant est conservé (N-17 ne le spécifie pas).
- **H4 — `parent_id` à la duplication** : non listé par N-17 parmi les champs réinitialisés ;
  comportement inchangé (copié). Seul `action_remainder` le positionne explicitement.
- **H5 — reprise** : exécutée par le recalcul autorisé, c'est-à-dire exactement la logique du cron
  corrigé (drafts automatiques uniquement), ce qui garantit de ne toucher ni saisies ni `done`.

## 7. Spécification
### Modèle de données
`lab.preparation` inchangé dans sa structure (aucun champ ajouté ou supprimé, aucune migration de
schéma). Seuls les attributs `copy` de `delivered_qty`, `prepared_qty` et `manual` passent à `False`.
`state` reçoit `copy=False` pour retomber sur son défaut `draft`.

### Comportement
1. `_cron_prepare()` — parcourt les enregistrements `state='draft'` **et** `manual=False`, et leur
   affecte `prepared_qty = max(ordered_qty - delivered_qty, 0)`. N'écrit rien d'autre. Idempotent.
2. `action_set_manual(quantity)` — écrit `prepared_qty = quantity` et `manual = True`, y compris
   pour `quantity = 0`.
3. `copy()` — conserve `ordered_qty` et `name` ; produit `delivered_qty = 0`, `prepared_qty = 0`,
   `manual = False`, `state = 'draft'`.
4. `action_remainder()` — singleton. `reste = ordered_qty - delivered_qty`.
   - `reste > 0` : crée un `lab.preparation` en `draft` avec `ordered_qty = reste`,
     `delivered_qty = 0`, `prepared_qty = 0`, `manual = False`, `parent_id = source`, et le retourne.
   - `reste <= 0` : retourne `self.browse()` (recordset vide), aucune création.
   - Dans les deux cas la source passe `state = 'done'`, sa `prepared_qty` est laissée intacte (H1).

### Interface
Aucune vue, aucun menu, aucun bouton livré par le module : rien de visible ne change.

### Sécurité
`ir.model.access.csv` inchangé ; aucun groupe ni règle d'enregistrement touché.

### Reprise de données
Script `migrations/19.0.1.1.0/post-migrate.py` appelant le recalcul autorisé : uniquement les
préparations `draft` et `manual=False` existantes. Aucune écriture sur les saisies manuelles ni
sur les `done`. Attendu sur `lab_client` : id 1 passe de 999 à 7 ; ids 2, 3, 4 strictement inchangés.

### Hors périmètre
Enregistrement `ir.cron` (risque 6), vues/écrans, notion de reliquat en cascade, tout comportement
non écrit dans N-17.

## 8. Critères d'acceptation
- [ ] C1 — Étant donné un draft automatique (`manual=False`, ordered=10, delivered=3), quand le cron tourne, alors `prepared_qty = 7`.
- [ ] C2 — Étant donné un draft automatique avec `delivered_qty > ordered_qty`, quand le cron tourne, alors `prepared_qty = 0` (jamais de négatif).
- [ ] C3 — Étant donné une saisie manuelle à **zéro** (`action_set_manual(0)`), alors `manual=True` et, après passage du cron, `prepared_qty` vaut toujours 0.
- [ ] C4 — Étant donné une saisie manuelle partielle (2 sur 10), quand le cron tourne, alors `prepared_qty = 2` inchangé.
- [ ] C5 — Étant donné un enregistrement `done`, quand le cron tourne, alors aucun de ses champs ne change.
- [ ] C6 — Étant donné deux passages consécutifs du cron, alors le second ne modifie aucune valeur (idempotence).
- [ ] C7 — Étant donné une préparation avec delivered/prepared/manual renseignés, quand on la duplique, alors la copie a `ordered_qty` identique, `delivered_qty=0`, `prepared_qty=0`, `manual=False`, `state='draft'`.
- [ ] C8 — Étant donné une copie d'un enregistrement `done` avec saisie manuelle, alors la copie est `draft` et automatique, et le cron la traite normalement.
- [ ] C9 — Étant donné une préparation ordered=10 delivered=4 prepared=6, quand `action_remainder()`, alors un nouveau draft ordered=6, delivered=0, prepared=0, manual=False, parent_id=source ; la source est `done` et garde `prepared_qty=6`.
- [ ] C10 — Étant donné une préparation intégralement livrée (delivered >= ordered), quand `action_remainder()`, alors recordset vide, aucune ligne créée, source `done`, `prepared_qty` intacte (H1).
- [ ] C11 — Étant donné plusieurs enregistrements, quand `action_remainder()` est appelée sur le recordset, alors une erreur de singleton est levée.
- [ ] C12 — Étant donné la copie `lab_client` après mise à niveau, alors id 1 vaut 7 et les ids 2, 3, 4 sont strictement inchangés (valeurs du tableau §1).

## 9. Estimation et découpage
Un seul incrément : correction des quatre points + tests + reprise. ~45 min agent.
**Niveau QA** : **renforcé** — la tâche touche des **données existantes** (reprise sur `lab_client`),
donc QA immédiate incluant la copie, conformément au contrat permanent.

## 10. Ce que l'utilisateur verra
Rien de visible : aucun écran, bouton ou message ne change. L'effet est que ses saisies manuelles
— y compris un zéro — cessent d'être écrasées par le traitement périodique, et qu'une duplication
repart d'une demande vierge.
