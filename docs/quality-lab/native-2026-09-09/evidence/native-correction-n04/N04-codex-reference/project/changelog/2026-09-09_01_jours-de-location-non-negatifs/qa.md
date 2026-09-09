## 2026-09-09 — D-31 — mode tâche renforcée

**Série** 19.0 (manifest) · **module** lab_rental · **copie** lab_client.

### Verdict
**VALIDÉ SOUS RÉSERVE** de la dette antérieure du manifest : tous les critères D-31 sont satisfaits ; aucune anomalie introduite. Le lint global reste rouge sur `author` absent du manifest inchangé, erreur reproduite sur la référence Git d4f00bfbaa29ce6b8c47939859d4a20b52c60390. Ce défaut hors périmètre est conservé, conformément à la règle de QA des tâches ; aucune prétention de lint entièrement vert.

### Résultats
Preuves et scripts : [.odoo-agents/flow-artifacts/days-nonnegative](../../.odoo-agents/flow-artifacts/days-nonnegative/).

| Contrôle | Résultat | Preuve |
|---|---|---|
| Lint natif --changed | Ruff vert, aucun conseil ; 1 erreur Odoo préexistante : author absent | lint.json/log, baseline-lint.log |
| Compilation et diff | OK ; calcul identique par comparaison AST ; écrans, droits et version inchangés | Relecture du diff et compileall |
| Test rouge avant correction | Create/write négatifs acceptés, 4 sous-tests en échec (rental/loan) | red.json/log |
| Installation / update QA + tests ciblés | OK, 4 méthodes, 0 échec, 0 erreur, 0 ignoré ; 6 s | green.json/log |
| Update copie lab_client | OK, environ 4 s | update.json/log |
| Scénarios copie | OK, contrainte réellement présente et validée, témoin conservé et nettoyage commité | client.json/log, client-scenario.py, seed.log |

### Couverture des critères
| Critère | Preuve | État |
|---|---|---|
| C1 création négative refusée sans résidu | test_negative_days_create + scénario copie | OK |
| C2 rejet write conserve nom/jours/tarif/total et autorise ensuite une écriture valide | test_negative_days_write_preserves_rental + scénario copie, relecture après invalidation du cache | OK |
| C3 zéro explicite, implicite et en modification valide, total nul | test_zero_days + scénario copie | OK |
| C4 jours × tarif inchangé pour rental/loan, tarifs nul et négatif autorisés | test_total_calculation_unchanged + comparaison du calcul avec HEAD | OK |
| C5 installation/tests, update copie et CHECK validé | green, update, client ; catalogue PostgreSQL | OK |

### Réserves et limites
- Dette antérieure : `lab_rental/__manifest__.py:1`, clé author absente. Reproduite avec le lint sur une extraction de la référence Git ; pas de changement métier nécessaire, auteur à renseigner lors d'une tâche dédiée.
- Avertissements d'outillage préexistants : `--without-demo=all` interprété True, http-interface implicite. Aucun warning de vue, aucune erreur runtime.
- Aucun contrôle obligatoire D-31 manquant. Recette complète de clôture (désinstallation, tours/navigateur, documents client) non exécutée : release ouverte, aucun écran modifié.
- Le relevé réel était vide malgré la description générale du laboratoire : un témoin synthétique a donc été ajouté avant update, contrôlé puis supprimé. Pas de reprise de données.
- Pas de reprise QA requise : le rouge initial est la preuve du défaut avant correction, la seule anomalie statique restante est antérieure.

### Appris
En 19.0, tester la contrainte SQL avec CheckViolation et flush explicite ; le rollback géré par assertRaises Odoo permet de relire la location valide après rejet. Sur copie, vérifier aussi convalidated pour éviter de confondre un update réussi avec une contrainte effectivement installée.
