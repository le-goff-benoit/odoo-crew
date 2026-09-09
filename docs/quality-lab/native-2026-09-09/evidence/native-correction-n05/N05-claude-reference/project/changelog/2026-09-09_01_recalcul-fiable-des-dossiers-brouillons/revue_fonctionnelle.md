# Revue fonctionnelle — Recalcul fiable des dossiers brouillons

**Projet** Entrepôt Silex · **série** 19.0 (origine : `lab_dispatch/__manifest__.py`) · **modules concernés** `lab_dispatch`

## 1. Ce que je comprends
En tant que gestionnaire logistique, je veux que « Recalculer » recalcule le total des
dossiers **brouillons** à partir des seules lignes actives, afin que le montant reflète
la réalité sans jamais toucher un dossier validé.
Périmètre : la méthode `lab.dispatch.action_recalculate` et la reprise des dossiers
brouillons déjà en base sur la copie synthétique.
**Problème réel** : deux défauts prouvés sur la copie `lab_client`
(`.odoo-agents/flow-artifacts/recalc-dispatch/inventaire_avant.txt`) —
`snapshot_total` inclut les lignes `cancelled=True`, et l'action écrase les dossiers
`state='done'`. Volume touché : 3 dossiers, dont 2 brouillons et 1 validé à 777,00
qui serait détruit au prochain clic.

## 2. Verdict standard Odoo 19.0
**À DÉVELOPPER** (correction de custom). Aucun équivalent standard : `grep -rn
"lab.dispatch\|snapshot_total" ~/odoo-sources/19.0/addons` ne renvoie rien sur les
625 modules. Il s'agit d'un modèle 100 % custom (`lab_dispatch/models/business.py`),
donc d'un correctif de code, pas d'un paramétrage.
**Série suivante** : sans objet, modèle custom, rien à calquer.

## 3. Voies possibles
| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | rien : la règle est dans une méthode Python | — | non |
| Studio | — | impossible : Studio ne surcharge pas une méthode | — | non |
| Code custom | 1 h | méthode corrigée + reprise idempotente + tests | nul (déjà custom) | **oui** |

Profil du projet : un module custom, aucun Studio → voie module (`odoo-developer`).

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | Majeure | Le journal du 2026-08-01 (D-11) demandait de recalculer **tous** les dossiers | Contredit frontalement D-12 | D-12, plus récente, fait foi : les validés sont figés. D-11 est marquée obsolète. |
| 2 | Majeure | « Ne pas recalculer » ≠ « recalculer et réécrire la même valeur » | Un `write` sur un validé, même avec la valeur identique, viole « strictement inchangé » (traçabilité, `write_date`) | La boucle **saute** les validés : aucune écriture, aucun calcul. |
| 3 | Moyenne | Reprise des données existantes | Un script rejoué deux fois ne doit pas dériver | Reprise = appel de la méthode corrigée sur les brouillons ; idempotence prouvée par double exécution. |
| 4 | Mineure | Sélection mixte brouillons + validés | Une erreur bloquerait l'usage courant | Pas d'exception : on ignore les validés en silence. |
| 5 | Mineure | Ligne annulée à quantité nulle | Aucun effet, mais le test doit distinguer « exclue » de « nulle » | Les lignes annulées du jeu portent des montants non nuls (90,00). |

Pas de multi-société, pas de devise, pas de droits modifiés (D-12). Aucune vue :
`lab_dispatch` ne déclare que sa sécurité, l'écran est le générique Odoo.

## 5. Questions bloquantes
Aucune : D-12 (`decisions/2026-09-08.md`) tranche Q1 (validés figés) et Q2 (lignes
annulées exclues) explicitement.

## 6. Hypothèses retenues
- « Strictement inchangé » est lu au sens fort : aucun `write` sur un dossier validé.
- La reprise ne concerne que les brouillons existants ; elle ne change aucun `state`.

## 7. Spécification
### Modèle de données
Inchangé. Aucun champ ajouté, retiré ou rendu obligatoire.
### Comportement
`action_recalculate` : pour chaque enregistrement dont `state == 'draft'`,
`snapshot_total = Σ (quantity × price)` sur les lignes `cancelled = False`.
Les enregistrements `state == 'done'` sont ignorés sans erreur et sans écriture.
Retour `True`.
### Interface
Aucun changement d'écran ni de libellé.
### Sécurité
Inchangée (`ir.model.access.csv` intact) — conforme à D-12.
### Reprise de données
Sur la copie `lab_client` uniquement : appliquer la méthode corrigée aux dossiers
`state='draft'`. Rejouable sans dérive. Aucun dossier validé touché.
### Hors périmètre
Recalcul des validés, transformation d'un validé en brouillon, changement de droits,
toute base autre que la copie synthétique, déploiement.

## 8. Critères d'acceptation
- [ ] CA1 — Étant donné un brouillon avec une ligne active 20,00 et une ligne annulée 90,00, quand j'appelle `action_recalculate`, alors `snapshot_total = 20,00`.
- [ ] CA2 — Étant donné un dossier validé à `snapshot_total = 777,00`, quand j'appelle `action_recalculate`, alors la valeur reste 777,00 et aucune écriture n'est faite (`write_date` inchangée).
- [ ] CA3 — Étant donné une sélection mixte brouillon + validé, quand j'appelle `action_recalculate`, alors le brouillon est recalculé, le validé est intact, et aucune exception n'est levée.
- [ ] CA4 — Étant donné un brouillon sans ligne, quand j'appelle `action_recalculate`, alors `snapshot_total = 0,00`.
- [ ] CA5 — Étant donné la copie existante, quand la reprise est jouée deux fois, alors les brouillons valent leur total actif et le résultat de la deuxième passe est identique à celui de la première.

## 9. Estimation et découpage
Un seul incrément : correction + tests + script de reprise. ~1 h.
**Niveau QA** : **renforcé** — la tâche modifie des données existantes sur la copie
(transition `module_high_risk`), donc validation immédiate sur la copie client,
sans attendre la clôture.

## 10. Ce que l'utilisateur verra
Rien de visible ne change (aucune vue, aucun libellé). Le seul effet perceptible :
le bouton « Recalculer » ne modifie plus les dossiers validés, et le total d'un
brouillon n'inclut plus les lignes annulées.
