# Revue fonctionnelle — Recalcul des dossiers logistiques et reprise des brouillons

**Projet** work (Entrepôt Silex) · **série** 19.0 (origine : `lab_dispatch/__manifest__.py`) · **modules concernés** `lab_dispatch`

## 1. Ce que je comprends

En tant que gestionnaire d'entrepôt, je veux que le bouton « Recalculer » d'un dossier
logistique remette à jour le total à partir des seules lignes encore actives, afin que le
montant affiché reflète la réalité de la demande en cours — sans jamais retoucher un
dossier déjà validé.

Périmètre : la méthode `lab.dispatch.action_recalculate` et la reprise des dossiers
brouillons déjà présents dans la base. Aucun écran, aucun droit, aucun nouveau champ.

**Problème réel** : le total stocké (`snapshot_total`) est faux à deux titres, constatés
sur la copie synthétique `lab_client` (3 dossiers, 5 lignes dont 2 annulées) :

| Dossier | État | `snapshot_total` actuel | Attendu D-12 |
|---|---|---|---|
| `LEGACY_DRAFT` | brouillon | 999.0 | 20.0 |
| `LEGACY_DONE` | validé | 777.0 | **777.0 — figé** |
| `LEGACY_FRACTION` | brouillon | 20.004 | 20.0 |

Deux défauts distincts, pas un seul : (a) la somme inclut les lignes `cancelled=True`
(`LEGACY_DRAFT` : 2×10 + 3×30 annulés) ; (b) la méthode itère sur `self` sans filtrer
l'état, donc un appel sur `LEGACY_DONE` écrase un total qui doit rester intangible.
`LEGACY_FRACTION` est le cas fourbe : l'écart est de 0,004 — invisible à l'œil, mais
une reprise qui « tolère » les petits écarts le laisserait faux.

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER (correction)** — `lab.dispatch` est un modèle entièrement custom du projet
(`lab_dispatch/models/business.py`), sans équivalent standard : `grep -rn "lab.dispatch"
~/odoo-sources/19.0/addons` ne retourne rien. Il n'y a rien à configurer, la règle métier
D-12 est propre au client. La correction est donc justifiée, mais elle doit rester une
correction : ni nouveau champ, ni changement de droits.

**Note de conception (hors périmètre, à arbitrer plus tard)** : `snapshot_total` est un
champ stocké non calculé mis à jour par un bouton. Le standard Odoo exprimerait cela par
un `fields.Float(compute=..., store=True)` — mais un champ calculé se recalculerait aussi
pour les dossiers validés, ce que D-12 interdit explicitement. Le champ « snapshot »
piloté par une action est ici le bon choix : c'est une photographie, pas un calcul. Je le
consigne pour qu'une prochaine intervention ne le « corrige » pas à tort.

**Série suivante** : rien dans ce point ne dépend d'une API mouvante ; aucune forme
retirée en 19.x n'est employée (pas d'`attrs`, pas de `_sql_constraints`, pas de `self._cr`).

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : la règle est dans du code Python custom | — | non |
| Studio | — | impossible : Studio ne surcharge pas une méthode Python | — | non |
| Code custom (`lab_dispatch`) | ~1 h | total juste, dossiers validés protégés, reprise jouée | nul (module déjà custom) | **oui** |

Profil du projet : un module custom, aucun Studio → voie module, conforme au tableau du rôle.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | **Majeure** | Le journal du 2026-08-01 (D-11) demande de recalculer *tous* les dossiers, y compris les validés | Deux règles contradictoires en mémoire ; appliquer l'ancienne détruirait les totaux validés | D-12 (2026-09-08) est la plus récente et rejette explicitement D-11 : elle fait foi. D-11 est marquée périmée dans `PROJECT.md`. |
| 2 | **Majeure** | « écraser » un validé peut se produire même en réécrivant la *même* valeur | D-12 dit « pas même recomputé » : un `write` identique changerait quand même `write_date` et polluerait le suivi | Filtrer sur `state == 'draft'` **avant** toute affectation, pas après |
| 3 | Moyenne | Sélection mixte (brouillons + validés) depuis la liste | Lever une erreur bloquerait un usage légitime ; ne rien faire du tout serait tout aussi faux | Recalculer les brouillons, ignorer les validés en silence, retourner `True` |
| 4 | Moyenne | Idempotence de la reprise face aux écarts infimes (`LEGACY_FRACTION` : 20.004 vs 20.0) | Une reprise « avec tolérance » laisserait la donnée fausse ; une reprise qui réécrit systématiquement n'est pas idempotente | Écrire la valeur exacte, mais seulement quand elle diffère de la valeur stockée (comparaison stricte, sans tolérance métier) |
| 5 | Mineure | Volume de la reprise | 3 dossiers ici, mais le motif doit tenir sur un vrai volume | Reprise par `search` + parcours simple ; pas de sujet de performance à ce volume, à revoir au-delà de ~10 000 dossiers |
| 6 | Mineure | Multi-société, archivage, portail | Non-dits classiques | Le modèle ne porte ni `company_id` ni `active` ni accès portail : sans objet ici |

Aucune contradiction bloquante : le contrat D-12 tranche tous les points ouverts.

## 5. Questions bloquantes

Aucune. Le contrat `decisions/2026-09-08.md` répond explicitement à Q1 (validés figés) et
Q2 (lignes annulées exclues), et exclut tout changement de droits.

## 6. Hypothèses retenues (à défaut de réponse)

- **H1** — « strictement inchangé » pour un validé signifie *aucune écriture*, donc pas de
  `write_date` modifiée. Contrôlée par la QA sur la copie.
- **H2** — Un dossier brouillon sans ligne, ou dont toutes les lignes sont annulées, a un
  total de `0.0` (somme vide), et non « inchangé ». C'est la lecture littérale de D-12.
- **H3** — La reprise ne concerne que `state == 'draft'` ; les validés ne sont ni lus ni
  écrits. Elle ne transforme aucun état (D-12 : « on ne transforme pas les validés en brouillons »).

## 7. Spécification

### Modèle de données
Inchangé. Aucun champ ajouté, retiré ou modifié.

### Comportement
- `lab.dispatch.action_recalculate()` : pour chaque enregistrement de `self` dont
  `state == 'draft'`, affecter à `snapshot_total` la somme `quantity × price` des lignes
  dont `cancelled` est faux. Les enregistrements `state == 'done'` sont ignorés — aucune
  lecture ni écriture de leur total. Retourne `True`. Ne lève jamais sur une sélection mixte.
- Reprise des données existantes : un script de migration `post-` rejoue la même règle sur
  tous les brouillons de la base, et n'écrit que les enregistrements dont le total stocké
  diffère réellement de la valeur cible. Deux exécutions successives ⇒ la seconde n'écrit rien.

### Interface
Inchangée : le module n'a aucune vue. Le bouton est appelé par les vues existantes de la base.

### Sécurité
Inchangée. `ir.model.access.csv` n'est pas touché (D-12 : « pas de changement de droits »).

### Reprise de données
Script de migration `lab_dispatch/migrations/19.0.1.0.1/post-recalcul_brouillons.py`, jouant
la règle sur les seuls brouillons, idempotent, journalisant le nombre de dossiers repris.
La version du manifest passe donc à `19.0.1.0.1` dès cette tâche : c'est ce qui déclenche
la reprise ; la release ne contient que ce point.

### Hors périmètre
Transformation de `snapshot_total` en champ calculé ; recalcul des validés ; arrondi ou
précision décimale du champ ; toute évolution des droits ou des écrans.

## 8. Critères d'acceptation

- [ ] **CA1** — Étant donné un dossier brouillon avec une ligne active (2 × 10) et une ligne annulée (3 × 30), quand j'appelle `action_recalculate`, alors `snapshot_total` vaut 20.0.
- [ ] **CA2** — Étant donné un dossier validé de total 777.0, quand j'appelle `action_recalculate` dessus, alors `snapshot_total` vaut toujours 777.0 **et** l'enregistrement n'a pas été écrit (`write_date` inchangée).
- [ ] **CA3** — Étant donné une sélection mixte (un brouillon, un validé), quand j'appelle `action_recalculate` sur les deux, alors le brouillon est recalculé, le validé est intact, et aucune erreur n'est levée.
- [ ] **CA4** — Étant donné un dossier brouillon dont toutes les lignes sont annulées, quand j'appelle `action_recalculate`, alors `snapshot_total` vaut 0.0.
- [ ] **CA5** — Étant donné la copie `lab_client` dans son état d'origine, quand la reprise est jouée, alors `LEGACY_DRAFT` passe de 999.0 à 20.0 et `LEGACY_FRACTION` de 20.004 à 20.0.
- [ ] **CA6** — Étant donné la reprise déjà jouée, quand elle est rejouée, alors aucun enregistrement n'est écrit (compteur de reprise à 0, `write_date` de tous les dossiers inchangée) : la reprise est idempotente.
- [ ] **CA7** — Étant donné la copie `lab_client`, quand la reprise est jouée puis rejouée, alors `LEGACY_DONE` conserve `snapshot_total = 777.0`, `state = done` et sa `write_date` d'origine.

## 9. Estimation et découpage

Un seul incrément : correction de la méthode + tests + script de reprise. ~1 h.

**Niveau QA** : **renforcé** — la tâche touche des **données existantes** (reprise sur la
copie du client). Validation immédiate sur la copie `lab_client`, sans attendre la clôture,
conformément à l'exception de la chaîne. Pas de droits, pas de compta, pas de facturation.

## 10. Ce que l'utilisateur verra

Aucun écran ne change. Le bouton « Recalculer » existant donne désormais un total qui exclut
les lignes annulées, et reste sans effet sur un dossier validé — y compris dans une sélection
multiple, où il ne produit plus ni erreur ni écrasement. Après livraison, les totaux des
dossiers brouillons déjà en base seront corrigés une fois pour toutes ; ceux des dossiers
validés seront exactement ceux d'avant.
