# Revue fonctionnelle — Réparation de `action_repair` (lab.register)

**Projet** work (Registre Boréal, synthétique) · **série** 19.0 (origine `.odoo-agents/config`) · **modules concernés** `lab_register`
**Release** `changelog/2026-09-15_01_repair` (ouverte) · **source du contrat** `decisions/current.md` (décision B-42 confirmée)

## 1. Ce que je comprends

En tant que gestionnaire du registre, je veux qu'un bouton « réparer » renumérote et recalcule **mes** brouillons sélectionnés, sans jamais toucher aux références déjà émises ni aux autres sociétés.

Périmètre : la méthode `action_repair` de `lab.register` et la reprise des brouillons existants de la société initiale (`My Company`, id 1) de la copie synthétique `lab_client`.

**Problème réel** : la méthode en place ne respecte aucune des bornes du contrat. Sur la copie, elle réécrit **les 4 enregistrements de la base** (`search([])`, `sudo()`), y compris l'émis `ISSUED/005` et le brouillon de la société 2, avec des séquences 10/20/… et des totaux incluant les lignes annulées. Volume réel constaté : 4 registres, 8 lignes, 2 sociétés, 3 utilisateurs (`.odoo-agents/flow-artifacts/repair-action/etat-initial.md`).

## 2. Verdict standard Odoo 19.0

**À DÉVELOPPER (correction de code custom)** — `lab.register` est un modèle entièrement synthétique propre au projet (`lab_register/models/business.py`) ; aucun modèle standard ne porte cette renumérotation. Les mécanismes standards mobilisés existent bien en 19.0 :
- société active : `env.company` — `~/odoo-sources/19.0/odoo/orm/environments.py:216` (fallback `user.company_id`, sociétés autorisées via `allowed_company_ids`) ;
- filtrage multi-société des règles : `company_ids` = `self.env.companies.ids` — `~/odoo-sources/19.0/odoo/addons/base/models/ir_rule.py:49`, ce que consomme `lab_register/security/rules.xml`.

**Série suivante** : aucune dépendance à une API mouvante ; `env.company` et `ir.rule`/`company_ids` sont inchangés en 19.1/19.4. Pas de dette de migration créée.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût à la migration | Recommandée |
|---|---|---|---|---|
| Configuration | — | Rien : c'est une méthode Python fautive | — | non |
| Studio / base | — | Impossible : Studio ne surcharge pas une méthode (`safe_eval`, pas de test Python) | — | non |
| Code custom (module existant) | faible | Méthode conforme au contrat + reprise des brouillons existants | nul | **oui** |

Profil du projet : un module custom, aucun Studio → voie module, conforme à la règle d'aiguillage.

## 4. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | majeure | `search([])` au lieu de `self` | La méthode ignore la sélection : un clic sur un enregistrement réécrit toute la base, toutes sociétés confondues | Boucler sur `self`, filtrer le périmètre |
| 2 | majeure | Aucun filtre `state` | Les enregistrements `issued` (références émises) sont renumérotés et recalculés, ce que B-42 interdit strictement | Ne traiter que `state == 'draft'` |
| 3 | majeure | Aucun filtre société | La société 2 est modifiée alors qu'elle doit rester strictement inchangée | Filtrer sur `env.company`, pas sur `company_ids` |
| 4 | majeure | `sudo()` | Le correctif s'exécute hors des droits et des règles de l'utilisateur : un accès refusé passerait inaperçu | Supprimer `sudo()`, laisser jouer `ir.rule` et l'ACL |
| 5 | moyenne | `index * 10` | Contredit Q1 du contrat (100/200) | `index * 100` |
| 6 | moyenne | Lignes annulées comptées dans `snapshot_total` | Le total inclut `cancelled=True` (ex. 5×99 sur chaque registre) | Sommer les seules lignes `cancelled = False` |
| 7 | moyenne | Multi-société utilisateur | `n06_operator` a accès à 2 sociétés ; « société active » ≠ « sociétés autorisées » | `env.company` seul, y compris quand `env.companies` en contient plusieurs |
| 8 | moyenne | Idempotence | La reprise doit pouvoir être rejouée sans dérive (séquences, totaux) | Tri déterministe `date_document, id` et écriture de valeurs absolues |
| 9 | information | `qa.md` existant marqué **PASS** | Il porte une recette du 14/09 sans données émises ni multi-société : il ne réceptionne pas ce correctif et sa mention « PASS » est trompeuse en l'état | Réécrire `qa.md` pour cette tâche, en conservant la trace de l'ancienne portée |

## 5. Questions bloquantes

Aucune : B-42 tranche Q1 (100/200) et Q2 (aucune renumérotation ni recalcul des émis). La demande est saine.

## 6. Hypothèses retenues

- « Société initiale de la copie » = `res.company` id 1 (`My Company`), seule société des brouillons `LEGACY_A_EARLY` / `LEGACY_A_LATE`.
- La reprise s'exécute en local sur `lab_client` uniquement ; aucune autorisation de production n'est demandée ni accordée.
- `reference` n'est jamais écrite par `action_repair`, ni sur les brouillons ni sur les émis (le contrat ne lui donne de valeur que pour les émis, à préserver).

## 7. Spécification

### Modèle de données
Inchangé : aucun champ ajouté, supprimé ni rendu obligatoire. Aucune migration de schéma.

### Comportement
`action_repair()` sur un recordset `self` :
1. périmètre = enregistrements de `self` tels que `state == 'draft'` **et** `company_id == self.env.company` ; tout le reste de `self` est ignoré sans erreur (sélection mixte admise) ;
2. tri du périmètre par `date_document` puis `id` ;
3. `sequence = 100, 200, 300, …` dans cet ordre ;
4. `snapshot_total = Σ quantity × price` sur les seules lignes `cancelled = False` ;
5. `state`, `reference` et les enregistrements hors périmètre ne sont pas écrits ;
6. retour `True`.

Exécution sous les droits de l'utilisateur appelant : pas de `sudo()`.

### Interface
Aucun écran modifié ; la méthode reste appelable par bouton/RPC.

### Sécurité
Droits existants inchangés (`ir.model.access.csv`, `security/rules.xml`). Un utilisateur ordinaire (`base.group_user`) doit pouvoir réparer ses propres brouillons ; les règles de société continuent de masquer les enregistrements des sociétés non autorisées.

### Reprise de données
Sur `lab_client`, société 1, brouillons existants uniquement :
- `LEGACY_A_EARLY` (id 1, 2020-01-01) : `sequence` 20 → **100**, `snapshot_total` 999.0 → **20.0** (2×10) ;
- `LEGACY_A_LATE` (id 2, 2020-01-02) : `sequence` 10 → **200**, `snapshot_total` 123.0 → **15.0** (3×5).
Inchangés : `LEGACY_ISSUED` (id 3 : `sequence` 17, `snapshot_total` 555.0, `reference` `ISSUED/005`, `state` issued) et `LEGACY_OTHER` (id 4, société 2 : `sequence` 80, `snapshot_total` 666.0). Valeurs attendues calculées depuis le relevé de la copie et le contrat, non depuis la méthode à tester. Reprise rejouable : un second passage ne change aucune valeur.

### Hors périmètre
Vues, boutons, guide utilisateur, société 2, enregistrements émis, toute écriture hors `lab_client`, recette complète de release (revient à `/odoo-close`).

## 8. Critères d'acceptation

- [ ] C1 — Étant donné deux brouillons de la société active à dates distinctes, quand `action_repair` est appelée sur eux, alors leurs `sequence` valent 100 et 200 dans l'ordre `date_document, id`.
- [ ] C2 — Étant donné un brouillon avec des lignes annulées, quand `action_repair` est appelée, alors `snapshot_total` n'additionne que les lignes `cancelled = False`.
- [ ] C3 — Étant donné une sélection mixte contenant un enregistrement `issued`, quand `action_repair` est appelée, alors `state`, `sequence`, `snapshot_total` et `reference` de cet enregistrement sont strictement inchangés, sans erreur levée.
- [ ] C4 — Étant donné une sélection contenant un enregistrement d'une autre société (utilisateur ayant accès aux deux, une seule active), quand `action_repair` est appelée, alors cet enregistrement est strictement inchangé.
- [ ] C5 — Étant donné un enregistrement hors de `self`, quand `action_repair` est appelée, alors il n'est pas modifié (pas de `search([])`).
- [ ] C6 — Étant donné la reprise exécutée sur les brouillons existants de la société 1 de `lab_client`, quand elle est rejouée une seconde fois, alors aucune valeur ne change (idempotence).
- [ ] C7 — Étant donné un utilisateur ordinaire (`base.group_user`, sans droit d'administration), quand il appelle `action_repair` sur ses brouillons, alors l'opération aboutit sans `sudo()` et sans `AccessError`.
- [ ] C8 — Un test automatisé démontre l'échec du code d'origine (rouge) puis le succès du code corrigé (vert), avec les deux preuves conservées.

## 9. Estimation et découpage

Incrément unique : correction de la méthode + tests + reprise des données existantes. ~35–50 min agent.

**Niveau QA** : **renforcé** — la tâche touche les droits (retrait de `sudo()`) et des **données existantes** (reprise sur la copie). QA immédiate sur la copie `lab_client`, sans attendre la clôture.

## 10. Ce que l'utilisateur verra

Aucun écran ne change. Le bouton « réparer » cesse de renuméroter des enregistrements qu'il ne devait pas toucher : après réparation, seuls les brouillons de la société active affichent de nouvelles séquences (100, 200, …) et des totaux qui excluent les lignes annulées ; les références émises gardent leur numéro et leur montant.
