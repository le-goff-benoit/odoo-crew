# Revue fonctionnelle — recalcul des demandes en cours (lab.dispatch)

**Projet** Entrepôt Silex (`/work`) · **série** 19.0 (manifest) · **module** `lab_dispatch`
**Analyste** claude-odoo-analyst · **date** 2026-09-09 · **contrat** `decisions/2026-09-08.md` (D-12, Marc Colin)

## 1. Reformulation

> En tant que gestionnaire logistique, je veux que le bouton « Recalculer » remette à jour
> le total figé de mes **dossiers en brouillon** en n'additionnant que les lignes non annulées,
> **sans jamais toucher** au total des dossiers déjà validés.

Deux défauts distincts sont dans la même action, à ne pas confondre :

| # | Défaut | Preuve dans le code | Effet sur la copie |
|---|---|---|---|
| A | Les lignes annulées sont comptées | `sum(line.quantity * line.price for line in record.line_ids)` — aucun filtre sur `cancelled` | `LEGACY_DRAFT` recalculé donnerait 110.0 au lieu de 20.0 |
| B | Les dossiers validés sont écrasés | `for record in self:` — aucun filtre sur `state` | `LEGACY_DONE` (777.0, figé par D-12) serait écrasé à la première exécution |

## 2. Problème réel derrière la demande

La demande porte sur *l'action*, mais les données existantes sont **déjà fausses** : elles ont été
produites par la version fautive (ou par une reprise antérieure sous D-11). L'inventaire de la copie
synthétique `lab_client` le montre :

| id | nom | état | `snapshot_total` actuel | valeur conforme à D-12 |
|---|---|---|---|---|
| 1 | LEGACY_DRAFT | draft | 999.0 | 20.0 (2×10 ; la ligne 3×30 est annulée) |
| 2 | LEGACY_DONE | done | 777.0 | **777.0 — figé, ne pas toucher** |
| 3 | LEGACY_FRACTION | draft | 20.004 | 20.0 |

Corriger l'action sans reprendre les brouillons laisserait 999.0 et 20.004 en base jusqu'à ce
qu'un utilisateur clique. La reprise fait donc partie du périmètre, comme la demande le dit.

**Le cas `LEGACY_FRACTION` est le piège de la reprise** : l'écart est de 0,004. Une reprise qui
compare les totaux avec une tolérance monétaire (`float_is_zero(..., precision_digits=2)`) le
jugerait « déjà bon » et laisserait 20.004 en base. D-12 ne prévoit aucune tolérance : le total
d'un brouillon *est* la somme, à l'identique. La comparaison de la reprise se fait donc sur
l'égalité exacte du flottant, et non sur une précision de 2 décimales.

## 3. Confrontation au standard (19.0)

`lab.dispatch` est un modèle propre au projet ; aucun addon standard ne couvre le besoin.
**Verdict : ÇA N'EXISTE PAS**, développement justifié.

**Contradiction relevée (non bloquante)** : la forme standard d'un total de lignes en Odoo est un
champ calculé stocké (`compute` + `@api.depends`, cf. `sale.order.amount_total`). Elle est ici
**volontairement écartée** : un champ calculé se recalculerait tout seul dès qu'une ligne d'un
dossier validé bouge, ce qui violerait D-12 (« pas même recomputé »). Le champ figé mis à jour par
une action explicite est la bonne forme pour un *snapshot*. Hypothèse retenue, pas de question posée.

**Contradiction mineure** : `LEGACY_DONE` porte 777.0 alors que ses lignes valent 20.0. C'est
incohérent, et c'est assumé : D-12 tranche Q1 « validés : définitivement figés ». On ne le corrige
pas et on ne le signale pas comme anomalie de données.

## 4. Voies possibles

| Voie | Effort | Coût migration | Retenue |
|---|---|---|---|
| Configuration | sans objet (comportement en Python) | — | non |
| Studio / données | Studio ne surcharge pas une méthode Python | — | non |
| **Module custom `lab_dispatch`** | ~1 h, 2 fichiers | code déjà custom, coût inchangé | **oui** |

Profil du projet : un module custom, aucun Studio → voie **module** (`odoo-developer`).

## 5. Spécification exécutable

1. `action_recalculate` ne traite que les enregistrements `state == 'draft'` ; les autres sont
   ignorés silencieusement, y compris dans une sélection mixte (aucune exception levée).
2. Pour un brouillon, `snapshot_total = Σ quantity × price` sur les lignes dont `cancelled` est faux.
3. Un dossier validé garde son `snapshot_total` **strictement identique** (pas de `write`, donc pas
   de `write_date` modifiée non plus).
4. Un script de reprise applique la règle 2 aux seuls brouillons existants de la copie, et est
   **idempotent** : la seconde exécution ne modifie aucun enregistrement.
5. Aucun changement de droits, aucun changement d'état (`draft` ne devient pas `done`, `done` ne
   redevient pas `draft`).

### Critères d'acceptation

| # | Critère | Vérification attendue |
|---|---|---|
| C1 | Les lignes annulées sont exclues du total d'un brouillon | test rouge avant correction |
| C2 | Un dossier validé n'est pas recalculé par l'action | test rouge avant correction |
| C3 | Sélection mixte : brouillons recalculés, validés intacts, aucune erreur | test |
| C4 | La reprise corrige les brouillons de la copie (999.0 → 20.0 ; 20.004 → 20.0) | exécution sur `lab_client` |
| C5 | La reprise est idempotente : 2e passage = 0 modification | seconde exécution sur `lab_client` |
| C6 | La reprise ne touche pas `LEGACY_DONE` (777.0) ni aucun état | exécution sur `lab_client` |

### Hors périmètre

Vues, droits, correction des totaux des dossiers validés, transformation d'état, champ calculé.

## 6. Ce que l'utilisateur verra

Le bouton « Recalculer » n'a plus d'effet visible sur un dossier validé, et le total d'un brouillon
baisse quand des lignes annulées y étaient comptées. Aucun écran modifié.

## 7. Verdict

**CONTINUE — voie module, niveau sensible (`module_high_risk`)** : la tâche modifie des **données
existantes** de la copie. La QA de tâche est donc immédiate et renforcée (lint, tests ciblés,
validation sur la copie `lab_client`), release ouverte ou non. Aucune question bloquante : D-12
tranche Q1 et Q2.
