# Fragment QA d'exécution renforcée — lab_dispatch (base QA `lab_qa`)

| Contrôle | Commande | Résultat |
|---|---|---|
| Test **rouge** avant correction | `labctl qa lab_dispatch --quick --tags /lab_dispatch:TestLabDispatchRecalculate` | ❌ **5 échecs / 6** — `110.0 != 20.0` (lignes annulées incluses), `110.0 != 777.0` (validé écrasé), `90.0 != 0.0`, `(110.0, 20.0) != (20.0, 777.0)` · `preuves/test_rouge_avant_correction.log` |
| Installation base neuve + tests ciblés | `… --quick --fresh --tags …` | ✅ install=ok · **6/6 tests** · 0 ERROR · 0 WARNING lié au module · ⏱ 14s · `preuves/test_vert_apres_correction.log` |
| Mise à jour sur base chaude + tests | `… --quick --update --tags …` | ✅ update=ok · **6/6 tests** · 0 ERROR · ⏱ 4s · `preuves/test_update_base_chaude.log` |

Le rouge initial porte sur le code d'origine avec les tests définitifs : le test
de non-régression a réellement échoué avant la correction.

## Verdict de voie
**VERT** — installation, mise à jour et tests ciblés tous verts.
