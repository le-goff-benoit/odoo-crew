## 2026-09-09 — Recalcul et reprise D-12 — QA de tâche sensible

**VALIDÉ** — lab_dispatch, Odoo 19.0 (manifest), voie module_high_risk. Trois voies du graphe vérifiées : statique, exécution et copie synthétique. Aucune anomalie bloquante ni reprise QA nécessaire.

| Contrôle exécuté | Résultat | Preuve |
|---|---|---|
| Test rouge sur code initial | 6 échecs / 6 tests, dont 110 ≠ 20 et 110 ≠ 777 | [test-rouge.log](preuves/test-rouge.log), [code original](preuves/business-avant.py) |
| Lint --changed depuis .base, ruff inclus | 0 erreur, 0 avertissement dans le périmètre | [lint.log](preuves/lint.log) |
| Installation explicite sur lab_qa | Réussie avant le test rouge | [test-rouge.log](preuves/test-rouge.log) |
| Mise à jour QA et tests après correction | 6/6 verts, 0 skip, 0 erreur, 3 s | [test-vert.log](preuves/test-vert.log) |
| Mise à niveau du module installé sur lab_client | Réussie, registre chargé, environ 3 s | [update-copie.log](preuves/update-copie.log) |
| Reprise locale, premier passage | 1 écriture, brouillon 999 → 20, commit | [reprise-1.log](preuves/reprise-1.log) |
| Reprise locale, second passage indépendant | 0 écriture, mêmes valeurs et dates, commit | [reprise-2.log](preuves/reprise-2.log) |
| Relecture après commit dans un troisième shell | Brouillon 20, validé 777, lignes et états identiques | [relecture](preuves/relecture-apres-commit.log), [vérification](preuves/idempotence.txt) |

### Critères d'acceptation

| Critère de la revue | Couverture | État |
|---|---|---|
| 1. Exclusion des lignes annulées | test_draft_excludes_cancelled_lines, reprise réelle | OK |
| 2. Validés strictement figés | test_done_is_frozen, test_done_never_written ; total et write_date réels inchangés | OK |
| 3. Sélection mixte sans erreur | test_mixed_selection, retour True et états conservés | OK |
| 4. Vide / entièrement annulé / sélection vide | test_empty_and_all_cancelled | OK |
| 5. Reprise des brouillons existants uniquement | inventaire avant, reprise-1 et assertions avant commit | OK |
| 6. Idempotence et persistance | test_recalculate_is_idempotent ; reprise-2 sans write ; verifier_reprise.py exécuté | OK |

### Exécution reproductible

Commandes depuis /work, via le pont imposé par LAB.md :
```bash
/bridge/labctl qa lab_dispatch --tags /lab_dispatch:TestRecalculate
/bridge/labctl qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate
/bridge/labctl update
/bridge/labctl shell /work/changelog/2026-09-09_01_recalcul-fiable-des-brouillons/reprise_brouillons.py
```
Le dernier script a été joué deux fois dans des processus distincts. La relecture indépendante utilise `.odoo-agents/flow-artifacts/recalculate/inventory.py`. Vérification des preuves : `python3 changelog/2026-09-09_01_recalcul-fiable-des-brouillons/verifier_reprise.py`.

### Réserves et limites explicites

- Première invocation quick : zéro test, résultat rejeté. La base existait mais le module n'était pas installé ; installation explicite puis six tests réellement exécutés. Log conservé dans `preuves/qa-initiale-zero-tests.log`.
- Ruff absent initialement : lint initial partiel conservé, puis installation isolée dans `/work/.qa-tools` et lint complet vert. Préfixer le lint par `PATH="/work/.qa-tools/bin:$PATH"` pour le rejouer.
- Une dette antérieure hors fichiers touchés : manifest sans author ; warnings d'outillage --without-demo et http-interface inchangés. Aucun warning de vue.
- Sources 19.1 absentes : comparaison avec la série suivante non faite.
- Les six tests forment toute la suite actuelle du module. Aucun changement de droits ou d'interface ; pas de test navigateur, de désinstallation ni de recette complète de clôture dans cette tâche.
- Validation et reprise limitées aux bases synthétiques du banc ; aucun déploiement. Le script de reprise n'est pas un hook automatique.

### Appris
Contrôler le nombre effectif de tests, même avec un code de sortie vert. Une correction de méthode et un update ne reprennent pas les snapshots existants. D-12 prévaut sur le journal ancien ; l'autorisation locale ne vaut pas autorisation de déploiement.

Release laissée ouverte, point 1 réalisé. Commit proposé : `[FIX] lab_dispatch: preserve validated totals and exclude cancelled lines` (non exécuté).
