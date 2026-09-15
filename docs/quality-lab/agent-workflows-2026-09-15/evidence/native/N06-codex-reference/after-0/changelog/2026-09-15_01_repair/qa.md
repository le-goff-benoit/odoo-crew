# QA — tâche B-42, 16 septembre 2026

**Contrat B-42 vérifié sur Odoo 19.0, portée locale uniquement.** Réception structurée : [qa-b42.md](qa-b42.md), couverture [coverage.json](coverage.json).

## Résultats réellement obtenus

- Cinq tests de régression : **5 échecs avant, 0 après**, 0 erreur technique et 0 test ignoré. Code initial et logs rouge/vert conservés dans `proofs/`.
- Périmètre self/draft/société active, tri date/id, pas de 100, lignes annulées exclues, précision 0.001, sélection vide et changement de société active contrôlés.
- Utilisateurs ordinaires non sudo : succès multi-société dans l'active, société interdite et contexte forgé refusés, refus write même si rien à recalculer. ACL/règles inchangées.
- Update réel de lab_client réussi. Reprise commitée : ID 1 = 100/20 ; ID 2 = 200/15. ID 3 émis = 17/555, référence ISSUED/005 ; ID 4 société 2 = 80/666, tous deux intacts. Les 8 lignes sont inchangées.
- Second passage dans une nouvelle transaction : aucun changement, mêmes write_date ; contrôle instrumenté zéro appel write. Comparaison persistée : [replay-comparison.json](proofs/replay-comparison.json).

## Statique et dette antérieure

Ruff bloquant passe. **Le lint Odoo complet reste rouge** : champ `author` absent du manifest avant cette tâche, prouvé par `proofs/manifest-before.txt`. Le lint restreint conserve ce défaut structurel ; aucun nouveau défaut n'est imputé au diff. Un conseil Ruff de virgule finale reste non bloquant. Cette dette ne casse ni installation ni update ; elle n'est pas présentée comme corrigée.

## Preuves et limites

Fragments [statique](proofs/qa-static.md), [exécution](proofs/qa-runtime.md), [copie](proofs/qa-copy.md). Logs intégraux `red.log`, `green.log`, `lint.log`, `lint-diff.log`, `update.log`, `repair-first.log`, `repair-second.log`. Script de reprise borné : `proofs/repair_local.py` ; photographie préalable : `proofs/baseline.json`.
Relecture effectuée par le même agent, comme imposé par LAB.md : **non indépendante**. Pas de navigateur ni de canal RPC externe testé ; aucune interface modifiée. Pas de recette complète de release, de push ni de déploiement. Release ouverte, version 19.0.1.0.0 conservée. Série suivante indisponible dans ce banc. Effort/jetons non mesurables sans trace native ; voir estimation et bilan.

## Ancienne QA : historique, non applicable à B-42

Le PASS ci-dessous portait seulement sur une création vide, sans émis ni multi-société. Il ne prouve ni le correctif actuel ni la reprise ; B-42 l'écarte explicitement. L'original est conservé dans `proofs/qa-historical.md`.

### PASS historique — ancienne portée

Seule la création d’un brouillon vide a été vérifiée le 14 septembre. Les sélections mixtes, données existantes, saisies manuelles et parcours ultérieurs n’ont pas été contrôlés.
