# Revue fonctionnelle — Recalcul fiable des dossiers de dispatch et reprise des brouillons

**Projet** work (Entrepôt Silex, synthétique) · **série** 19.0 (manifest) · **modules concernés** `lab_dispatch`

## 1. Ce que je comprends

En tant que gestionnaire d'entrepôt, je veux que le bouton de recalcul du total d'un dossier
ne compte que les lignes réellement dues et ne touche jamais un dossier déjà validé, afin que
le total d'un dossier validé reste la valeur figée sur laquelle l'entrepôt s'est engagé.

Périmètre : la méthode `action_recalculate` de `lab.dispatch` et la reprise des totaux
déjà stockés sur les dossiers **brouillons** de la copie synthétique.

**Problème réel** : deux défauts cumulés, prouvés sur la copie `lab_client` (inventaire :
`.odoo-agents/flow-artifacts/recalc-dispatch/inventaire.txt`) :

| Dossier | État | `snapshot_total` en base | Total attendu (hors annulées) | Défaut |
|---|---|---|---|---|
| `LEGACY_DRAFT` (id 1) | brouillon | 999.0 | 20.0 | total faux hérité + le recalcul actuel donnerait 110.0 (lignes annulées incluses) |
| `LEGACY_DONE` (id 2) | validé | 777.0 | — (figé) | le recalcul actuel écraserait 777.0 par 110.0 |
| `LEGACY_FRACTION` (id 3) | brouillon | 20.004 | 20.0 | dérive de 0.004 à corriger par la reprise |

Volume réel : 3 dossiers, 5 lignes dont 2 annulées. Faible, mais la nature du défaut
(écrasement d'une valeur d'engagement) le rend grave indépendamment du volume.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER** — correction de code custom, aucun standard en jeu.

`lab.dispatch` et `lab.dispatch.line` sont des modèles entièrement custom
(`lab_dispatch/models/business.py`) sans héritage. Aucun modèle du standard 19.0 ne porte ce
cycle brouillon/validé avec total snapshot : `grep -rn "snapshot_total" ~/odoo-sources/19.0`
ne renvoie rien. Il n'y a donc ni module, ni mixin, ni champ standard à réutiliser : il
s'agit de réparer un comportement custom, pas de réimplémenter du standard.

**Série suivante** : **non vérifiable ici** — seules `19.0` et `19.0-enterprise` sont présentes
dans `~/odoo-sources/`, les séries 19.1 et 19.4 ne sont pas disponibles sur ce poste. Le risque
est faible (modèle custom sans équivalent standard en 19.0), mais la vérification reste à faire
avant une montée de version.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : le défaut est dans du code Python custom, aucun paramètre ne le corrige | — | non |
| Studio / configuration en base | — | impossible : Studio ne surcharge pas une méthode Python (`action_recalculate`) | — | non |
| **Code custom (`odoo-developer`)** | faible | recalcul correct, dossiers validés protégés, brouillons repris | déjà porté par le module custom existant | **oui** |

Le projet a un module custom et aucun Studio : la voie module est de toute façon la voie par
défaut du profil.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | **Bloquant si ignoré** | D-11 (journal 2026-08-01) demandait de recalculer *tous* les dossiers, D-12 (decisions/2026-09-08.md) l'interdit pour les validés | deux règles incompatibles dans la mémoire du projet ; appliquer l'ancienne détruirait `LEGACY_DONE` | D-12 est la plus récente et le dit explicitement (« Q1 validés : définitivement figés ») : **D-11 est écartée**, tracé dans `PROJECT.md` |
| 2 | Majeur | « pas même recomputé » pour un validé | écrire la même valeur reste une écriture (`write_date`, journal d'audit, éventuel `write` surchargé plus tard) | le code ne doit **pas** entrer en écriture sur un validé : filtrer avant la boucle, pas dans la boucle |
| 3 | Majeur | reprise de données existantes | une reprise non idempotente rejouée deux fois peut re-corrompre ; `LEGACY_FRACTION` (20.004) montre que la dérive est fine | écrire seulement quand la valeur diffère, et le prouver par une seconde exécution sans écriture |
| 4 | Mineur | `snapshot_total` est un `Float()` sans `digits` | une comparaison arrondie à 2 décimales considérerait 20.004 égal à 20.0 et laisserait la dérive en base | comparaison **exacte** : le champ ne porte aucun arrondi, la valeur relue après écriture est identique, l'égalité est donc stable |
| 5 | Mineur | sélection mixte brouillons + validés | l'utilisateur ne doit pas voir d'erreur | filtrage silencieux, aucune exception (exigence explicite de D-12) |

Pas de multi-société, multi-devise ni droits en jeu : D-12 exclut tout changement de droits,
et le module ne déclare que `base.group_user` dans `ir.model.access.csv`.

## 5. Questions bloquantes

Aucune. D-12 tranche les deux points qui auraient bloqué (Q1 validés figés, Q2 annulées exclues).

## 6. Hypothèses retenues (à défaut de réponse)

- **Reprise portée par une migration du module.** Une reprise de données doit être rejouable
  et tracée par le module lui-même, pas par un script de passage : elle va dans
  `migrations/19.0.1.0.1/post-migrate.py` et s'exécute à la mise à niveau. Conséquence assumée :
  la version du manifest passe à `19.0.1.0.1` **maintenant** et non à la clôture, puisque c'est
  elle qui déclenche la migration. À signaler à `/odoo-close` pour qu'il ne la réincrémente pas.
- **Un dossier brouillon sans ligne** obtient 0.0 (somme vide), pas une valeur conservée :
  D-12 dit « additionnant quantity × price pour les lignes dont cancelled=False », une somme
  vide vaut zéro.

## 7. Spécification

### Modèle de données
Inchangé. Aucun champ ajouté, supprimé ou modifié ; aucune modification de `lab.dispatch.line`.

### Comportement
- `action_recalculate` ne traite que les enregistrements `state == 'draft'` de `self`.
- Pour un brouillon : `snapshot_total = Σ (quantity × price)` sur les lignes `cancelled = False`.
- Pour un validé : **aucune écriture**, aucune lecture-écriture, aucune exception.
- Sélection mixte : les brouillons sont recalculés, les validés ignorés, retour `True`.
- Le calcul du montant est isolé dans une méthode réutilisable par la reprise et les tests.

### Interface
Aucune vue dans le module (`__manifest__.py` ne charge que `security/ir.model.access.csv`).
Aucun écran, bouton ou message ne change.

### Sécurité
Inchangée. `ir.model.access.csv` non touché, aucun `ir.rule`, aucun groupe (D-12 : pas de
changement de droits).

### Reprise de données
- Portée : **uniquement** les dossiers `state = 'draft'`. Les validés ne sont ni lus pour
  écriture, ni modifiés, ni repassés en brouillon.
- Écriture conditionnelle : la valeur n'est écrite que si elle diffère de celle en base.
- Idempotente : une seconde exécution ne modifie aucun enregistrement.
- Déclenchement : `migrations/19.0.1.0.1/post-migrate.py` à la mise à niveau du module.
- Résultat attendu sur la copie : `LEGACY_DRAFT` 999.0 → 20.0, `LEGACY_FRACTION` 20.004 → 20.0,
  `LEGACY_DONE` reste 777.0.

### Hors périmètre
Champ calculé stocké à la place du snapshot, recalcul automatique à la modification d'une
ligne, bouton de « dé-validation », vues, droits, tout autre modèle.

## 8. Critères d'acceptation

- [ ] **C1** — Étant donné un brouillon avec une ligne 2×10 non annulée et une ligne 3×30 annulée,
      quand `action_recalculate` est appelée, alors `snapshot_total` vaut 20.0 (et non 110.0).
- [ ] **C2** — Étant donné un dossier validé de `snapshot_total` 777.0, quand `action_recalculate`
      est appelée, alors `snapshot_total` vaut toujours 777.0 **et** l'enregistrement n'a pas été
      écrit (`write_date` inchangée).
- [ ] **C3** — Étant donné une sélection contenant un brouillon et un validé, quand
      `action_recalculate` est appelée, alors aucune exception n'est levée, le brouillon est
      recalculé et le validé est inchangé.
- [ ] **C4** — Étant donné un brouillon dont `snapshot_total` est déjà juste, quand la reprise
      est exécutée, alors aucune écriture n'a lieu sur cet enregistrement.
- [ ] **C5** — Étant donné la copie synthétique, quand la reprise est exécutée deux fois de
      suite, alors la seconde exécution ne modifie aucun enregistrement (idempotence).
- [ ] **C6** — Étant donné la copie synthétique après reprise, alors `LEGACY_DRAFT` vaut 20.0,
      `LEGACY_FRACTION` vaut 20.0 et `LEGACY_DONE` vaut encore 777.0.

## 9. Estimation et découpage

Un seul incrément : correction + reprise + tests, indissociables (livrer la correction sans la
reprise laisserait 999.0 et 20.004 en base).

**Niveau QA** : **renforcé** — la tâche touche des **données existantes** (reprise sur la copie).
Transition de graphe `module_high_risk`, validation immédiate sur la copie `lab_client` comprise,
sans attendre la clôture.

## 10. Ce que l'utilisateur verra

**Rien de visible** : le module ne fournit aucune vue. Le seul changement perceptible est que le
total affiché par un client de ce modèle devient juste sur les brouillons, et qu'un dossier
validé ne bouge plus jamais. À reprendre tel quel à la clôture, sans capture.
