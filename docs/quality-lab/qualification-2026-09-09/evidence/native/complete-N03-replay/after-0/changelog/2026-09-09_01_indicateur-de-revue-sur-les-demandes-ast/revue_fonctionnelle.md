# Revue fonctionnelle — Indicateur de revue sur les demandes Aster

**Projet** work (Association Aster) · **série** 19.0 (origine : défaut `.odoo-agents/config`)
**Base de travail** copie synthétique locale `lab_client` · **Analyste** claude-odoo-analyst · **Date** 2026-09-09

## Demande

Ajouter sur le modèle existant `x_lab_request` un unique indicateur booléen **stocké**
`x_studio_needs_review`, calculé selon la décision **D-22**. Aucun écran modifié dans
cette tâche. Pas de module custom, pas de déploiement.

## Ce qui existe déjà (relevé en base, XML-RPC sur `lab_client`)

| Objet | État | XML-ID |
|---|---|---|
| Modèle `x_lab_request` « Demande Aster » (`manual`) | existe | `studio_customization.lab_seed_model` |
| `x_name` (char) | existe | `studio_customization.lab_seed_x_name` |
| `x_studio_days` (integer) | existe | `studio_customization.lab_seed_x_studio_days` |
| `x_studio_kind` (selection : `rental` « Location », `loan` « Prêt ») | existe | `studio_customization.lab_seed_x_studio_kind` |
| Droit d'accès du modèle | existe | `studio_customization.lab_seed_access` |
| Vues du modèle | **aucune** (`ir.ui.view` sur `x_lab_request` : 0) | — |
| Enregistrements | **aucun** (`x_lab_request` : 0 ligne) | — |
| `x_studio_needs_review` | **absent** | — |

Conséquences retenues : les champs existants sont réutilisés tels quels — ni renommés,
ni recréés, ni dupliqués. Aucune vue n'existe, donc aucune vue n'est à modifier ni à
capturer : le périmètre « aucun écran » est cohérent avec la base.

## Verdict standard

**ÇA N'EXISTE PAS.** `x_lab_request` est un modèle manuel propre au client ; aucun
module standard 19.0 ne porte cette notion de « revue requise ». Un champ calculé stocké
est la forme adéquate — il est filtrable et groupable, contrairement à un calculé non
stocké. **Spec saine → on continue.**

## Règle métier retenue (D-22, `decisions/2026-09-08.md`)

`x_studio_needs_review = (x_studio_days >= 7) ET (x_studio_kind == 'rental')`

- Seuil **7 inclus** (Q1) : 7 jours déclenche la revue, 6 non.
- Prêts **exclus** (Q2) : `loan` ne déclenche jamais la revue, quelle que soit la durée.
- **D-22 remplace D-21** (5 jours, tous types), encore présente dans le journal au
  2026-08-01. La règle des 5 jours ne doit pas être implémentée.
- Le brouillon de conception initial demandait un **nouveau champ durée** : écarté,
  `x_studio_days` existe (piège déjà consigné au journal).

## Contradictions et hypothèses (non bloquantes, tranchées ici)

1. **`x_studio_kind` vide** — la sélection n'a pas de valeur par défaut et le champ est
   facultatif. Hypothèse retenue : une valeur vide n'est pas `rental`, donc **pas de
   revue**. Conforme à l'esprit de D-22 (la revue est réservée aux locations avérées).
2. **`x_studio_days` vide ou négatif** — `0`/`False` < 7, donc **pas de revue**. Aucune
   validation de saisie n'est ajoutée : D-22 ne la demande pas.
3. **Indicateur invisible** — sans vue et sans écran modifié, le champ n'est lisible que
   par RPC, filtre ou export. C'est le périmètre demandé ; l'exposition à l'écran est une
   tâche ultérieure, pas un manque de celle-ci.
4. **Pas d'automatisation, pas de droits** — D-22 exclut explicitement l'envoi automatique
   et tout changement de droits. Hors périmètre.
5. **Recalcul de l'existant** — un champ calculé stocké est calculé par Odoo à la création
   du champ. Il y a 0 enregistrement aujourd'hui : rien à reprendre. Si la production en
   contient, l'application du pack les calculera de la même façon.

Aucune question bloquante.

## Voies possibles

| Voie | Évaluation |
|---|---|
| **Studio / configuration en base** | **Retenue.** Le projet n'a aucun module custom, la personnalisation existante est déjà `studio_customization`, et la configuration est représentative d'Odoo Online. Voie demandée explicitement par l'humain. |
| Module custom (`odoo-developer`) | Écartée : introduirait une deuxième voie sur la même fonction et n'est pas déployable sur le profil visé. Explicitement exclu par la demande. |

### Limites de Studio applicables ici (annoncées avant de faire)

- Le code du calcul tourne dans `safe_eval` : pas d'import, pas de `env.cr`. La règle
  D-22 tient en une expression, la limite n'est pas contraignante.
- Pas de test Python : la preuve est un **scénario RPC rejouable** sur la copie.
- Le champ calculé stocké doit déclarer ses `depends` (`x_studio_days,x_studio_kind`)
  pour être recalculé à chaque modification de l'un des deux.
- Rien n'est reproductible sans **pack versionné** : c'est le livrable de la tâche.

## Périmètre

**Dedans** : création du seul champ `x_studio_needs_review` (booléen, stocké, calculé,
lecture seule), en contexte `studio=True`, sur `x_lab_request` ; pack versionné ;
scénarios RPC.

**Dehors** : toute vue, tout menu, toute automatisation, tout droit, tout module Python,
tout déploiement staging ou production, toute reprise de données.

## Critères d'acceptation

- [ ] C1 — Le champ `x_studio_needs_review` existe sur `x_lab_request` : type booléen, `store = True`, `compute` renseigné, `depends = x_studio_days,x_studio_kind`, `readonly = True`, état `manual`.
- [ ] C2 — Une location de 7 jours (`x_studio_kind = 'rental'`, `x_studio_days = 7`) donne `x_studio_needs_review = True` après relecture serveur (seuil inclus).
- [ ] C3 — Une location de 6 jours donne `False` ; une location de 30 jours donne `True`.
- [ ] C4 — Un prêt (`loan`) donne `False` à 7 jours comme à 30 jours.
- [ ] C5 — Un genre vide et une durée nulle ou négative donnent `False` (pas d'erreur).
- [ ] C6 — Le recalcul suit la modification : passer une demande de 6 à 7 jours la fait basculer à `True` ; repasser `rental` en `loan` la fait revenir à `False`.
- [ ] C7 — Les champs existants `x_name`, `x_studio_days`, `x_studio_kind` sont inchangés (mêmes ids, mêmes XML-ID `lab_seed_*`) et aucun doublon n'a été créé.
- [ ] C8 — Le script de construction est idempotent : deux applications successives laissent exactement un champ `x_studio_needs_review` et un seul XML-ID.
- [ ] C9 — Le pack `pack.json` est exporté, `odoo_pack.py diff` ne rapporte aucun écart sur la copie, et il ne contient aucune référence `unresolved`.
- [ ] C10 — Le XML-ID créé est relevé dans `created.txt`, sous `studio_customization`, marqué Studio.

## Ce que l'utilisateur verra

**Rien à l'écran.** Aucune vue n'existe sur ce modèle et aucune n'est modifiée. L'indicateur
est exploitable par filtre, regroupement, export ou RPC. Si la release doit un jour l'afficher,
c'est une tâche distincte à cadrer — à noter pour `/odoo-close` : pas de capture à produire
pour ce point.
