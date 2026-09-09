# QA de tâche

## 2026-09-09 — Point 1 · [studio] Indicateur `x_studio_needs_review` (D-22)

**Verdict : VALIDÉ.** Aucune anomalie bloquante. Deux points d'attention listés en fin de section.

Copie de recette : `lab_client`, Odoo **19.0+e-20260817**, XML-RPC. Aucune vue n'ayant été touchée, il n'y a pas de contrôle navigateur ni de capture : `odoo-shot.sh` n'a pas lieu d'être ici. `odoo-test.sh` non plus — un point Studio ne se prouve pas par des tests Python (rôle `studio.md`), mais par des scénarios RPC rejoués.

### Contrôles

| Contrôle | Résultat | Preuve |
|---|---|---|
| Pack ↔ copie, avant toute écriture | 0 à créer / 0 à modifier / 1 inchangé | `flow-artifacts/lab-needs-review/studio_diff.md` §1 |
| Application du pack **deux fois** sur base déjà configurée | 0 créé / 0 modifié / 1 inchangé, deux fois | idem §3-4 |
| Application du pack **deux fois depuis l'absence du champ** | 1 créé puis 0 créé / 1 inchangé | idem §2-4 (bloc « depuis une copie sans le champ ») |
| Absence de doublon après double application | 1 champ, 1 identifiant externe, 1 modèle | idem §5 |
| Références du pack résolues | aucune référence `unresolved` (`model_id` → `studio_customization.lab_seed_model`) | `studio/pack.json` |
| Script de construction rejoué sur le champ posé par le pack | « déjà conforme — rien à faire », même identifiant externe | `studio_diff.md` §7 |
| Scénario RPC `test_needs_review.py` | **VERT**, 17/17 contrôles, code retour 0 | `flow-artifacts/lab-needs-review/studio_runtime.md` §1 et §4 |
| Contre-épreuve : règle D-21 remise en place | **ROUGE**, 6 contrôles en échec — le scénario sait échouer | idem §2 |
| Retour à D-22 puis diff du pack | scénario vert, 0 écart | idem §3-4 |
| Copie rendue propre | 0 demande de recette, 0 droit d'accès, 0 règle | `studio_runtime.md` §4 |

La contre-épreuve mérite un mot : sous la règle D-21 (5 jours, tous types), le contrôle A2 (« location de 7 jours → vrai ») **passe toujours**. C'est attendu — ce cas ne discrimine pas les deux règles. Ce sont A3, A4, A5 et le cas de bord qui distinguent D-22 de D-21, et ce sont exactement ceux qui basculent au rouge. Le scénario teste donc bien la décision, pas seulement la présence du champ.

### Critères d'acceptation de la revue

| # | Critère | Couvert par | État |
|---|---|---|---|
| A1 | champ manuel, booléen, stocké, calculé, `depends = x_studio_days,x_studio_kind` | scénario, section A1 | ✅ |
| A2 | `rental` / 7 j → vrai (seuil inclus) | scénario, section A2 | ✅ |
| A3 | `rental` / 6 j → faux | scénario, section A3 | ✅ |
| A4 | `loan` / 7 j et `loan` / 30 j → faux | scénario, section A4 | ✅ |
| A5 | recalcul sur modification de `x_studio_days` | scénario, section A5 | ✅ |
| A6 | recalcul sur modification de `x_studio_kind` | scénario, section A6 | ✅ |
| A7 | identifiant externe sous `studio_customization`, `studio`, `noupdate`, contexte studio | `studio_diff.md` §5 : `x_studio_needs_revie_05e329b9-… \| noupdate=True \| studio=True` | ✅ |
| A8 | deux applications sans doublon, diff sans écart | `studio_diff.md` §2-6 | ✅ |
| A9 | aucun droit ni règle sur le modèle après recette | scénario, section A9 | ✅ |
| A10 | `x_name`, `x_studio_days`, `x_studio_kind` intacts, XML-ID `lab_seed_*` conservés | `studio_diff.md` §5 | ✅ |

10 / 10.

### Anomalies mineures — pour arbitrage, sans reprise

**M1 — `noupdate` n'est pas posé par la création seule.** Contrairement à ce qu'affirme le rôle `studio.md` (« Odoo crée lui-même l'identifiant externe […] marqué `studio` et `noupdate` »), `web_studio/models/ir_model_data.py:19-25` ne met `noupdate` à vrai que sur un **write** en contexte studio, jamais sur le `create`. Un champ tout juste créé dans Studio reste donc à `noupdate = False` jusqu'à sa première retouche, et un pack exporté à cet instant livrerait une personnalisation exposée à une mise à niveau de module. `build_needs_review.py` rejoue explicitement le chemin de Studio pour corriger cela, avec le commentaire qui l'explique. Le rôle mériterait d'être précisé — leçon candidate.

**M2 — un droit d'accès nouvellement créé n'est pas vu tout de suite.** Sur cette copie, `create` est resté refusé pendant **huit requêtes consécutives** après la création d'un droit global actif portant `perm_create`, alors que `read`, `write` et `unlink` passaient. Un appel explicite à `ir.model.access.call_cache_clearing_methods` (`ir_model.py:2190`) rétablit l'accès immédiatement. `_get_allowed_models` est mis en cache par utilisateur **et par opération** (`ir_model.py:2133`) ; l'invalidation automatique n'a pas atteint le processus qui sert nos appels. Le scénario vide donc le cache explicitement. À connaître pour toute recette qui pose ses propres droits — leçon candidate.

### Ce qui n'a pas été fait, et pourquoi

- **Aucun déploiement** (staging, production) : hors périmètre de la demande. Le pack est prêt, `diff` avant `apply` reste obligatoire.
- **Aucun droit d'accès livré** : D-22 l'exclut. Conséquence à arbitrer, remontée en tête du compte-rendu (contradiction C1 de la revue).
- **Recette complète de release** (base neuve, tours, désinstallation, mise à niveau) : elle se joue à la clôture, `/odoo-close`.
