# 2026-09-09 — Jours non négatifs — QA de tâche renforcée

**Module** lab_rental · **série** 19.0 (manifest) · **contrat** D-31, Luc Roy, [décision](../../decisions/2026-09-08.md).

## Verdict
**VALIDÉ SOUS RÉSERVE** — tous les critères métier satisfaits, zéro régression constatée. Le lint global reste en échec pour la clé `author` absente du manifest inchangé ; dette antérieure prouvée, hors périmètre de D-31. Aucun contrôle obligatoire omis.

## Résultats
Les [preuves exécutables et journaux complets](../../.odoo-agents/flow-artifacts/days-nonnegative/) sont conservés dans le projet.

| Contrôle | Résultat | Preuve |
|---|---|---|
| Relecture diff / git diff --check | Conforme / code 0 | qa-static.md |
| Ruff bloquant et conseils, configuration 19.0 | Vert, 4 fichiers | lint.log |
| Lint --changed global | **Code 1**, uniquement author absent | lint.log ; lint-baseline.log reproduit depuis HEAD d4f00bf |
| Contre-épreuve avant contrainte | 4 sous-cas négatifs rouges, CheckViolation non levée | tests-red.log |
| Installation/mise à jour QA et tests ciblés finaux | OK, **4/4**, 0 erreur, 0 skip, 7 s | tests-final.log ; qa-runtime.md |
| Mise à niveau lab_client | OK, registre chargé en 4.955 s | copy-update.log |
| Contrainte PostgreSQL | lab_rental_days_nonnegative, CHECK ((days >= 0)), validée | copy-check.log |
| Donnée créée avant update | 3 jours, 12.5, total 37.5 conservés après update et rejet | copy-seed.log ; copy-check.log |
| Nettoyage et relecture nouvelle session | 0 location, CHECK toujours validé | inventory-after.log ; qa-client.md |

## Critères d'acceptation
| Critère | Couverture | État |
|---|---|---|
| C1 : création négative refusée, aucune ligne résiduelle | test_negative_days_create_rejected + copie | PASS |
| C2 : write négatif refusé, jours/tarif/total préservés, nouvelle écriture valide | test_negative_days_write_preserves_valid_rental + copie | PASS |
| C3 : zéro en création et modification, total nul | test_zero_days_create_and_write_allowed + copie | PASS |
| C4 : calcul et tarifs inchangés, location et prêt | test_total_and_daily_rate_rules_unchanged + copie | PASS |
| C5 : install/update, contrainte validée, copie nettoyée | QA runtime + catalogue SQL + nouvel inventaire | PASS |

## Réserves antérieures et outillage
- `lab_rental/__manifest__.py:1` : author absent dès la base de release ; lint le remonte même en --changed sur fichiers Python. Aucun auteur inventé, manifest inchangé. Les warnings Odoo correspondants sont également antérieurs. Pas de défaut introduit ni de reprise de code requise.
- Pont d'update : avertissement `--without-demo all`, interprété True par Odoo 19.0 ; hors dépôt modifiable. Aucun effet sur la validation de D-31.
- Ruff initialement absent a été installé dans un environnement temporaire de /work pour exécuter effectivement ce contrôle.

## Non exécuté
Comparaison aux sources 19.1 impossible (absentes). Recette complète de clôture, désinstallation, navigateur et captures non exécutés : tâche sans écran/droit, release laissée ouverte comme demandé. Aucun engagement de livraison ni déploiement production.

## Appris
Le shell ORM remonte CheckViolation, et le flush doit être dans le savepoint protégé. Un update réussi doit être complété par une vérification du CHECK validé en catalogue. D-31 remplace la tolérance historique et ne restreint pas les tarifs.
