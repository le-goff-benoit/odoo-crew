Flow terminé, release ouverte, rien de commité.

## Résultat

`action_repair` renumérotait **tout le registre** — y compris une référence déjà émise et les enregistrements d'une autre société. Sur la copie, un clic écrasait la séquence et le total de `ISSUED/005`. C'est réparé, et les deux brouillons existants de la société initiale sont repris.

**Ce qui a changé** (`lab_register/models/business.py`, +21/−2) : périmètre ramené à `self` × `draft` × `env.company`, tri `date_document` puis `id`, pas de 100, `snapshot_total` hors lignes annulées, `sudo()` retiré. Sécurité et manifest **non touchés** (`git diff --quiet` à 0) : le retrait du `sudo()` ne change pas les droits, il rend effective la règle `register_company` qu'il contournait.

**Rouge puis vert, conservés** : sur le code d'origine, `6 failed of 7 tests`, chaque échec sur une valeur du contrat (l'émis passait de `17 / 555.0` à `10 / 510.0`). Après correction : `0 failed of 7`, `update=ok`. À noter — le 7ᵉ test, celui d'idempotence, **passait déjà sur le code fautif** : la réparation globale était elle aussi déterministe. L'idempotence seule ne prouve pas ce contrat, c'est écrit dans la QA et dans `PROJECT.md`.

**Reprise** sur `lab_client`, sous `n06_operator` (ordinaire, deux sociétés activées, société active 1), sélection volontairement mixte `[1,2,3,4]` : ids 1→`100 / 20.0`, 2→`200 / 15.0`; le `diff` avant/après ne porte **que** sur ces deux lignes, l'émis et la société 2 sont identiques au caractère près. Rejouée dans un second processus : `diff` vide. Droits vérifiés en plus sous `n06_restricted`, qui répare sans `sudo()` et se voit refuser la société 2 (`AccessError`).

**QA antérieure** : elle était titrée `PASS` alors que son corps admettait n'avoir testé qu'une création vide. Reclassée en historique non réceptionnant, citée verbatim dans `qa.md` plutôt qu'effacée.

## Limites, dites explicitement

- **Recette complète non jouée** — base neuve intégrale, désinstallation, suite entière : c'est `/odoo-close`.
- **Version du manifest non incrémentée**, aucun livrable documentaire, aucune capture : la release reste ouverte.
- **Lint en erreur** sur `__manifest__.py` (clé `author` manquante) : dette antérieure prouvée, hors diff, **non corrigée** — à arbitrer à la clôture.
- Rien n'est commité ni poussé ; aucun environnement distant sollicité.

Preuves : `changelog/2026-09-15_01_repair/{revue_fonctionnelle,qa,demande}.md` et `.odoo-agents/flow-artifacts/repair-b42/` (logs, inventaires avant/après, scripts rejouables).

**Prochaine action** : à vous — `/odoo-close` pour la recette complète et la livraison, ou un commit si vous le demandez.