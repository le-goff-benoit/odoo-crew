# N07 — réception indépendante Codex référence

**Verdict : accepted_with_reservations.** Aucun critère critique manquant. Revue du contrat figé et de cette seule variante, sans correction ni réexécution Odoo.

## Critères

- **C1 reçu** : N-17 respectée, distinction avec stock.picking et portée de l’ancienne QA conservées (`after-0/changelog/2026-09-15_01_repair/revue_fonctionnelle.md:9`, `qa.md:1`).
- **D1 reçu** : zéro/partiel manuels et done conservés ; remise à zéro de copy ; reliquat positif lié à la source puis cron ; source figée sans écraser sa quantité ; absence de création sans solde ; bornage négatif et rejeu idempotent. Code lu, neuf méthodes de test et douze invariants oracle concordent (`models/business.py:17–50`, `tests/test_preparation.py:10–121`, `oracle.log:15`).
- **Q1 reçu** : rouge métier puis vert sur les mêmes tests ; update effective de lab_client, 999→7, exclusions 0/2/88 intactes avec métadonnées, rejeu sans write, commit et lecture dans une nouvelle session (`bridge-002.log:160`, `bridge-004.log:51`, `bridge-007.log:15–18`, `bridge-008.log:15`).
- **R1 reçu avec réserve de formulation** : revue, QA sensible et mémoire complètes ; limites et absence de déploiement explicites. Ancienne mémoire conservée.

## Réserves

1. **Portée installation** : le vert final est un **-u**, pas une installation fraîche verte du correctif (`bridge-004.log:6`). Le résumé du pont `install=ok update=ok` est repris sans nuance (`preuves/runtime.md:5`, `answer-0.md:4`). L’installation initiale portait le code fautif et le rouge. Q1 figé demande bien rouge/vert et update copie, tous deux présents ; cette réserve n’ajoute pas une recette obligatoire.
2. **Dette préexistante déclarée** : lint global rouge uniquement pour `author` manquant dans le manifest initial inchangé ; Ruff et diff propres (`bridge-003.log:11`, `preuves/static.md:4–8`).

## Reprises et temps évitable

- **001→002 utile après erreur de préparation** : le test ir.cron initial provoquait une ForeignKeyViolation faute de montage transactionnel ; correction avec enter_registry_test_mode avant modification métier. Le premier appel de 17,17 s établissait aussi huit défauts métier et initialisait QA : ne pas compter tout ce temps comme gaspillage. Le rouge confirmé a neuf échecs d’assertion, zéro erreur technique.
- **002→004 utile** : correction métier puis vert, tests identiques.
- **004→005 utile** : bases et buts différents, QA puis update copie.
- **005→006 évitable au niveau runtime : 4,53 s**. Même base, commande et empreintes ; le premier runtime réussissait déjà. Seul le collecteur était mal paramétré avec `--module`, qui exige un bilan de tests inexistant pour update. Rejeu pour corriger l’attestation, sans couverture supplémentaire (`raw-0.jsonl:89,95,97`, `preuves/update.json:45`, `preuves/update-confirmed.json:45`).
- **007→008 utile** : réparation/commit puis preuve de persistance dans une autre session.

Adaptation locale proposée : bon mode de collecteur dès le premier update, distinguer commande effective -i/-u du résumé ; reprendre le montage standard ir.cron 19.0 pour ce test. Pas de généralisation de comportement métier ni de recette supplémentaire.

## Intégrité et durée

75 empreintes after-0, neuf logs bridge, références de couverture et journaux de preuve concordent. Les sources du dernier vert correspondent exactement au module final. Archives intactes, aucune autre variante lue, aucun Odoo réexécuté.

Début UTC : 2026-09-15T22:47:53.471934+00:00. Fin UTC : 2026-09-15T22:52:12.424889+00:00. **Revue active : 258.953 s** (durée continue, sans attente passive).

Racine des citations : `/tmp/crew-agent-workflows-20260916-v2/N07-codex-reference` ; les chemins `preuves/`, `qa.md`, `models/`, `tests/` sont relatifs respectivement à la release dans after-0 ou au module lab_preparation.
