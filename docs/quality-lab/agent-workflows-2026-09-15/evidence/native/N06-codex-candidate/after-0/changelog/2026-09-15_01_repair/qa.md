# QA — B-42 — Odoo 19.0 — tâche sensible

## 2026-09-16 — Réception de la correction locale
La réception structurée de cette tâche figure dans [qa-reception.md](qa-reception.md), avec [coverage.json](coverage.json). Revue : [revue_fonctionnelle.md](revue_fonctionnelle.md).

| Contrôle exécuté | Résultat et preuve |
| --- | --- |
| Test rouge avant correctif | 6 échecs métier, 0 erreur technique — proofs/red.log et red.json |
| Test vert après correctif | 6 tests réussis, 0 skip — proofs/green.json ; détail qa-runtime.md |
| Statique et droits inchangés | Ruff bloquant vert ; syntaxe/diff conformes ; dette author du manifest préexistante — qa-static.md |
| Update de la copie existante | Odoo exit 0, module rechargé ; installed et données avant reprise contrôlés — proofs/update.log et copy-rights-v2.json |
| Droits utilisateur ordinaire | Succès sans sudo, refus AccessError lecture/write, postconditions et nettoyage — proofs/copy-rights-v2.json |
| Reprise persistée via XML-RPC | Société initiale 1, ids 1/2 : 100/20 et 200/15 — proofs/repair-authorized.json |
| Préservation et idempotence | issued id 3, société 2 id 4 et 8 lignes identiques ; rejeu zéro write, métadonnées stables — proofs/repair-verified.json |

## Relecture de l’ancienne QA trompeuse
Le titre « PASS (ancienne portée) » ne vaut pas réception de B-42. Il n’attestait que la création d’un brouillon vide le 14 septembre : pas de références émises, pas de sélection mixte, pas de multi-société, pas de droits ni de reprise historique. Texte original conservé dans proofs/qa-before.md. La présente section et sa réception structurée portent seules sur le correctif actuel.

## Réserves et limites explicites
Le lint global reste rouge sur `author` absent du manifest, identique à HEAD. Cette dette antérieure n’est pas présentée comme corrigée ; un conseil COM812 reste non bloquant. Aucun défaut du diff ni échec des six tests ciblés.
Le reçu update.json est marqué failed avec exit_code=0 : --module exige un bilan de tests que l’update seul ne produit pas. Le log réel et le contrôle installed sur copie établissent l’update ; aucune nouvelle recette inventée.
copy-rights.log conserve un incident de chemin du pont avant mutation, résolu dans copy-rights-v2. repair-first.log conserve un refus RPC attendu d’après les sociétés du compte ; seul repair-authorized atteste la reprise. Les Faults ne sont jamais comptés comme des succès métier.
Relecture par le même agent, non indépendante, conformément à LAB.md ; aucune délégation ni réception indépendante prétendue. Aucune capture, recette complète de release, désinstallation, push ou déploiement distant réalisé. Release laissée ouverte ; version 19.0.1.0.0 inchangée jusqu’à clôture. Mesures temps/jetons indisponibles : effort-limits.md.

## Résultat métier
Deux brouillons historiques réparés, références DRAFT-A/DRAFT-B conservées. Référence émise ISSUED/005 (17,555) et brouillon autre société OTHER/DRAFT (80,666) inchangés. Les appels futurs restent limités à self, draft et env.company ; les sociétés autorisées ne définissent pas le périmètre métier.
