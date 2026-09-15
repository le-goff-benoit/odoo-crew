# QA — release 2026-09-15_01_repair

**Module** `lab_register` · **série** 19.0 (origine `.odoo-agents/config`) ·
**mode** QA de **tâche**, niveau **renforcé** (droits, multi-société, données
existantes) · **autorisation** locale uniquement.

---

## Relecture de la QA antérieure — elle était trompeuse

Le contenu précédent de ce fichier annonçait **« QA — PASS (ancienne portée) »**
tout en admettant dans son propre corps que *« seule la création d'un brouillon
vide a été vérifiée le 14 septembre »*.

**Ce fichier ne disait pas faux sur ce qu'il avait fait ; il était trompeur sur
ce qu'il valait.** Un titre `PASS` en tête d'un fichier `qa.md` se lit comme une
réception. Ce qui avait été joué ne touchait ni les données existantes, ni les
enregistrements émis, ni le multi-société, ni les droits — c'est-à-dire aucun
des points sur lesquels `action_repair` était fautive.

`decisions/current.md` le tranche explicitement : *« Le qa.md existant porte une
ancienne recette sans données émises ni multi-société ; il ne réceptionne pas ce
correctif. »* Cette ancienne recette est donc **conservée ci-dessous comme
historique, et retirée du rôle de réception**. Elle n'est ni invoquée, ni
prolongée, ni comptée dans la couverture de la présente QA.

> **Historique — 2026-09-14, non réceptionnant.** « QA — PASS (ancienne
> portée). Seule la création d'un brouillon vide a été vérifiée le 14 septembre.
> Les sélections mixtes, données existantes, saisies manuelles et parcours
> ultérieurs n'ont pas été contrôlés. »

Leçon à retenir pour le projet : **un `PASS` dont la portée est écrite en petits
caractères en dessous vaut un `INCOMPLET`.** Portée dans « Pièges connus » de
`PROJECT.md`.

---

## Verdict

**VALIDÉ** pour les points 1 et 2 de la release.

La réception s'appuie sur trois voies exécutées séparément, dont les fragments
complets sont dans `.odoo-agents/flow-artifacts/repair-b42/` :
`module_high_static_qa.md`, `module_high_runtime_qa.md`,
`module_client_copy_qa.md`.

| Voie | Résultat |
|---|---|
| Statique (diff, conformité 19.0, lint ciblé) | conforme — règles bloquantes `All checks passed!` |
| Exécution (install, update, tests ciblés) | conforme — rouge 6/7 puis vert 7/7, `update=ok` |
| Copie `lab_client` (droits, données existantes) | conforme — reprise bornée, idempotente, sous utilisateur ordinaire |

---

## Le test rouge, puis vert

C'est l'exigence centrale de la demande, et elle est tenue par deux exécutions
conservées.

**Rouge, sur le code d'origine** (`test-rouge.log`) :
`RECETTE … tests="6 failed, 0 error(s) of 7 tests" errors=7 failed=6`, sortie 1.

| Test rouge | Attendu (contrat B-42) | Observé avant correction |
|---|---|---|
| `test_renumbers_active_company_drafts_by_date_then_id` | `sequence` 100 | `30` |
| `test_snapshot_total_ignores_cancelled_lines` | `20.0` | `41.0` |
| `test_issued_reference_is_preserved` | `('issued', 17, 555.0, 'ISSUED/005')` | `('issued', 10, 510.0, 'ISSUED/005')` |
| `test_other_company_is_left_untouched` | `('draft', 80, 666.0, …)` | `('draft', 40, 510.0, …)` |
| `test_records_outside_self_are_untouched` | `('draft', 42, 777.0, …)` | `('draft', 20, 1.0, …)` |
| `test_ordinary_user_repairs_with_their_own_rights` | `sequence` 100 | `30` |

**Vert, après correction** (`test-vert.log`) :
`RECETTE … tests="0 failed, 0 error(s) of 7 tests" errors=0 failed=0`, sortie 0.
Chemin de mise à jour également vert (`test-update.log`, `install=ok update=ok`).

**Point à ne pas perdre** : le septième test, `test_repair_is_idempotent`,
**passait déjà sur le code fautif** — la réparation globale d'origine était elle
aussi déterministe. L'idempotence, seule, ne prouve donc pas le contrat ; elle
n'a de valeur que lue avec les six autres. C'est exactement le piège de
l'ancienne QA, en plus petit.

---

## Couverture des critères d'acceptation

Critères repris de `revue_fonctionnelle.md`, sans reformulation ni suppression.

| Critère | Preuve | État |
|---|---|---|
| C1 — séquences 100 puis 200, ordre `date_document, id` | `test_renumbers_active_company_drafts_by_date_then_id` ; copie : ids 1→100, 2→200 | **satisfait** |
| C2 — `snapshot_total` hors lignes `cancelled` | `test_snapshot_total_ignores_cancelled_lines` ; copie : 20.0 et 15.0 relus | **satisfait** |
| C3 — émis strictement préservé (`state`, `sequence`, `snapshot_total`, `reference`) | `test_issued_reference_is_preserved` ; copie : id 3 identique au caractère près dans le `diff` avant/après | **satisfait** |
| C4 — sélection mixte, autre société ignorée | `test_other_company_is_left_untouched` ; copie : `n06_operator` avec `allowed_company_ids=[1,2]`, id 4 inchangé | **satisfait** |
| C5 — égalité de date départagée par `id` | `test_renumbers_…` (SAME 1 / SAME 2 au 2024-01-10) | **satisfait** |
| C6 — idempotence | `test_repair_is_idempotent` **et** `reprise-passe1/2.txt`, `diff` vide entre deux processus distincts | **satisfait** |
| C7 — utilisateur ordinaire, sans `sudo()` | `test_ordinary_user_repairs_with_their_own_rights` ; copie : `n06_restricted`, `admin=False`, appel abouti | **satisfait** |
| C8 — état de la copie après reprise | `diff inventaire-avant.txt inventaire-apres.txt` : **seules** les lignes des ids 1 et 2 changent | **satisfait** |
| C9 — rouge conservé puis vert | `test-rouge.log` et `test-vert.log` | **satisfait** |

Couvert en plus du contrat : le périmètre `self`
(`test_records_outside_self_are_untouched`) — un brouillon de la bonne société,
absent de la sélection, reste intact.

---

## Reprise des données de la société initiale

Sur `lab_client`, société 1 *My Company*, sous `n06_operator` (ordinaire,
sociétés 1 et 2 activées, société active 1), sélection volontairement mixte
`[1, 2, 3, 4]` :

| id | société | avant | après | attendu |
|---|---|---|---|---|
| 1 | 1 | seq 20 / 999.0 | **seq 100 / 20.0** | oui |
| 2 | 1 | seq 10 / 123.0 | **seq 200 / 15.0** | oui |
| 3 | 1 | issued, seq 17 / 555.0 / ISSUED/005 | **identique** | oui |
| 4 | 2 | seq 80 / 666.0 / OTHER/DRAFT | **identique** | oui |

Rejouée dans un second processus : `diff` des états **vide**.
Canal XML-RPC réel vérifié en plus (`rpc-action_repair.txt` :
`{"transport": "xmlrpc", "outcome": "result", "result": true}`).

---

## Dette antérieure — distinguée, non corrigée

- `lab_register/__manifest__.py` : clé obligatoire **`author` manquante**, le
  lint est en erreur de ce seul fait. `git diff --quiet <base> --
  lab_register/__manifest__.py` retourne 0 : le manifest est identique à la base
  de release, et le message `Missing 'author' key` apparaît déjà dans les logs
  d'avant correction. **Dette antérieure prouvée**, signalée et laissée en
  l'état ; à arbitrer à la clôture.
- Conseil ruff non bloquant `no-space-after-block-comment` : vise le marqueur
  `#=== ACTION METHODS ===#`, qui est la forme du standard de la série
  (`~/odoo-sources/19.0/addons/sale/models/sale_order.py:1045`). Conservé.

Ces deux points n'entrent pas dans le verdict du correctif.

---

## Ce qui n'a pas été contrôlé

Énoncé pour que la clôture sache ce qui reste à jouer — rien de tout cela n'est
présenté comme fait :

- **Recette complète de release** : non jouée, c'est `/odoo-close`. Base neuve
  complète, désinstallation, mise à niveau et suite entière restent à faire.
- **Rendu navigateur et captures** : aucun. Le module ne déclare aucune vue
  (`__manifest__.py` ne charge que la sécurité) ; il n'y a pas d'écran à
  vérifier pour cette tâche.
- **Version du manifest** : **non incrémentée**. La release reste ouverte et
  rien n'est livré ; l'incrément se fait une fois, à la clôture.
- **Livrables documentaires** : aucun guide, aucune communication client — la
  release est ouverte.
- **Aucun environnement distant** : aucun environnement n'est déclaré dans le
  projet, aucun n'a été sollicité. Rien n'a été poussé, ni commité, ni déployé.
- Le passage RPC ne prouve ni un rendu visuel ni les droits d'un autre
  utilisateur que l'appelant ; les droits sont prouvés par les sondes shell sous
  `n06_operator` et `n06_restricted`, pas par le RPC.

---

## Chemins de preuve

Tous sous `.odoo-agents/flow-artifacts/repair-b42/` :
`test-rouge.log`, `test-vert.log`, `test-update.log`,
`test-module-complet.log`, `lint.log`, `update-lab_client.log`,
`inventaire-avant.txt`, `inventaire-apres.txt`, `reprise-passe1.txt`,
`reprise-passe2.txt`, `droits-utilisateur-ordinaire.txt`,
`rpc-action_repair.txt`, les trois fragments de voie, et les scripts rejouables
dans `scripts/`.
