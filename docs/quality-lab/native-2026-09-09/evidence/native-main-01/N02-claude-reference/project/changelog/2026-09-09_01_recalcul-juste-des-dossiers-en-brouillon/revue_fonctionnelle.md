# Revue fonctionnelle — Recalcul des dossiers en brouillon et reprise des existants

**Projet** Entrepôt Silex (`/work`) · **série** 19.0 (origine : `__manifest__.py`) · **modules concernés** `lab_dispatch`

## 1. Ce que je comprends
En tant que gestionnaire logistique, je veux que le bouton « Recalculer » remette à jour le
montant d'un dossier **en brouillon** à partir de ses seules lignes actives, afin que le montant
affiché corresponde au réel sans jamais toucher un dossier déjà validé.

**Problème réel** : `action_recalculate` (`lab_dispatch/models/business.py`) fait aujourd'hui deux
fautes en même temps, constatées sur la copie synthétique `lab_client` (preuve :
`.odoo-agents/flow-artifacts/recalcul-dispatch/inventaire-avant.txt`) :
- elle additionne **toutes** les lignes, annulées comprises → dossier 1 : brut 110,00 au lieu de 20,00 ;
- elle écrit sur **tous** les enregistrements de `self`, y compris les `state = 'done'` → le
  snapshot figé du dossier 2 (777,00) serait écrasé au premier appel sur une sélection mixte.

Volume concerné sur la copie : 2 dossiers (1 brouillon, 1 validé), 4 lignes dont 2 annulées.
Le brouillon 1 porte un `snapshot_total` faux (999,00 au lieu de 20,00) : c'est lui, et lui seul,
que la reprise doit corriger.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER (correction d'un défaut du custom)**
`lab.dispatch` est un modèle entièrement custom du projet : aucune recherche dans les sources de la
série ne remonte d'équivalent (`grep -rn "snapshot_total\|def action_recalculate"
~/odoo-sources/19.0/addons/*/models/*.py` → 0 occurrence). Il n'y a donc rien à configurer : le
standard ne porte ni le modèle, ni l'action. Le sujet est un correctif de logique métier, pas une
fonctionnalité nouvelle.

Le motif « figer une valeur à la validation, ne plus jamais la recalculer » est en revanche du
standard Odoo dans l'esprit : c'est ce que font les documents validés (montants d'une pièce
comptable postée). On garde donc un champ **stocké non calculé**, écrit par une action explicite —
et surtout **pas** un `compute … store=True`, qui recalculerait les dossiers validés dès qu'une
ligne bouge et détruirait le figeage exigé par D-12.

**Série suivante** : rien à attendre du standard, le modèle restera custom ; aucune dépendance à une
forme supprimée en 19.x. `ir.model.access.csv` reste la forme correcte en 19.0
(`~/odoo-sources/19.0/odoo/addons/base/security/ir.model.access.csv`) ; il deviendra `ir.access.csv`
en 19.4 — hors périmètre ici.

## 3. Voies possibles
| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | Rien : le défaut est dans du code Python custom | — | non |
| Studio | — | Impossible : Studio ne surcharge pas une méthode | — | non |
| Code custom (`odoo-developer`) | faible (1 méthode + tests + script de reprise) | Bouton juste, dossiers validés intouchés | nul, le module existe déjà | **oui** |

Profil du projet : un module custom, aucun Studio → voie module, conforme au tableau du rôle.

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | **Bloquante — levée** | Le `JOURNAL.md` du 2026-08-01 (D-11) demande de recalculer **tous** les dossiers, validés compris ; un vieux ticket voulait même reconstruire les validés | Suivre le journal reviendrait à écraser les snapshots figés, exactement le défaut à corriger | D-12 (`decisions/2026-09-08.md`, 2026-09-08, Marc Colin) remplace D-11 : on ne touche **que** les brouillons. Contradiction tranchée par la décision la plus récente ; aucune question à l'humain |
| 2 | Majeure | « strictement inchangé (pas même recomputé) » pour un validé | Réécrire la même valeur reste une écriture : `write_date` bouge, un tracking ou une automatisation se déclencherait | Ne jamais écrire sur un `state = 'done'` : filtrer **avant** l'écriture, pas comparer après |
| 3 | Majeure | Sélection mixte brouillons + validés | Une exception ferait échouer le lot entier et bloquerait l'utilisateur | Ignorer silencieusement les validés, recalculer les brouillons, ne rien lever (exigence explicite de D-12) |
| 4 | Majeure | Idempotence de la reprise | Une reprise rejouée qui réécrit à chaque passage empêche de prouver la convergence et fait du bruit | La reprise écrit uniquement les brouillons dont le total diffère ; un second passage doit écrire 0 enregistrement |
| 5 | Mineure | Flottants | `sum(quantity * price)` en `Float` : comparer par égalité stricte est fragile | Comparer avec la tolérance des arrondis (`float_compare` / epsilon) pour décider d'écrire |
| 6 | Mineure | Lignes annulées d'un dossier validé | Le total figé d'un validé peut inclure des lignes annulées : c'est normal, il est figé | Aucune reprise sur les validés, y compris ceux dont le total « paraît » faux (dossier 2 : 777,00 conservé) |

Non-dits vérifiés : pas de multi-société ni multi-devise sur `lab.dispatch` (aucun `company_id`
ni `currency_id` dans `business.py`) ; aucun droit à changer (D-12) ; aucun archivage (`active`
absent) ; aucune vue ni écran dans le module — donc rien de visible à documenter côté écran.

## 5. Questions bloquantes
Aucune. D-12 tranche les deux points ouverts (Q1 validés figés, Q2 lignes annulées exclues).

## 6. Hypothèses retenues (à défaut de réponse)
- « Ligne annulée » = `cancelled = True` ; il n'existe pas d'autre marqueur d'annulation dans le modèle.
- Un dossier sans ligne active vaut 0,00 (somme vide), y compris s'il n'a que des lignes annulées.
- La reprise est un script de données joué sur la copie `lab_client`, pas un script de migration
  du module : la release n'est pas livrée, l'humain arbitrera l'industrialisation à la clôture.

## 7. Spécification
### Modèle de données
Inchangé. `snapshot_total` reste un `Float` **stocké et non calculé** (surtout pas de
`compute`/`store=True` : voir §2). Aucun champ ajouté, aucune contrainte ajoutée.

### Comportement
`action_recalculate` sur un recordset quelconque :
1. sélectionne les enregistrements `state == 'draft'` ;
2. pour chacun, écrit `snapshot_total = Σ(quantity × price)` sur les lignes **dont `cancelled` est faux** ;
3. n'écrit rien du tout sur les `state == 'done'` ;
4. ne lève aucune exception sur une sélection mixte, vide, ou entièrement validée ;
5. retourne `True`.

### Interface
Aucune vue dans le module : rien ne change à l'écran.

### Sécurité
Aucun changement de droits (D-12). `ir.model.access.csv` inchangé.

### Reprise de données
Script rejouable sur la copie `lab_client` uniquement : il recalcule les brouillons, n'écrit que
ceux qui divergent, laisse les validés strictement intacts, et affiche les comptages avant/après.
Rejoué immédiatement, il doit écrire **0** enregistrement. Aucune autre base n'est autorisée.

### Hors périmètre
Reconstruire les dossiers validés ; transformer un validé en brouillon ; toucher aux droits ;
livrer ou déployer ; produire guide, captures ou communication (réservés à `/odoo-close`).

## 8. Critères d'acceptation
- [ ] C1 — Étant donné un dossier brouillon avec une ligne active (2 × 10) et une ligne annulée (3 × 30), quand j'appelle `action_recalculate`, alors `snapshot_total` vaut 20,00.
- [ ] C2 — Étant donné un dossier validé de `snapshot_total` 777,00 dont les lignes valent 110,00, quand j'appelle `action_recalculate`, alors `snapshot_total` vaut toujours 777,00.
- [ ] C3 — Étant donné un dossier validé, quand j'appelle `action_recalculate`, alors aucune écriture n'est faite dessus (`write_date` inchangée).
- [ ] C4 — Étant donné une sélection mixte (1 brouillon + 1 validé), quand j'appelle `action_recalculate`, alors le brouillon est recalculé, le validé est inchangé, et aucune exception n'est levée.
- [ ] C5 — Étant donné un dossier brouillon dont toutes les lignes sont annulées, quand j'appelle `action_recalculate`, alors `snapshot_total` vaut 0,00.
- [ ] C6 — Étant donné la copie `lab_client` après une première reprise, quand je rejoue la reprise, alors 0 enregistrement est écrit et aucun total ne change (idempotence).
- [ ] C7 — Étant donné la copie `lab_client`, quand je joue la reprise, alors seuls les brouillons divergents sont écrits ; le dossier validé conserve 777,00.

## 9. Estimation et découpage
Un seul incrément : correction de la méthode + tests + script de reprise. ~1 h.
**Niveau QA** : **renforcé** — la tâche modifie des **données existantes** de la copie client
(reprise des brouillons). QA sur copie `lab_client` obligatoire, immédiatement, release ouverte ou non.

## 10. Ce que l'utilisateur verra
Aucun écran ne change. Le bouton « Recalculer » existant cesse de gonfler le montant avec les
lignes annulées, et cesse de modifier les dossiers validés. Sur la copie, un seul montant bouge :
le dossier brouillon 1 passe de 999,00 à 20,00.
