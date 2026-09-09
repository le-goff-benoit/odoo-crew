# Exécution locale Odoo 19.0
Votre copie synthétique est prête, avec trois lignes valides. Aucune préparation Docker à refaire.

Runtime : /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py

```bash
python3 /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py --run /tmp/odoo-delegation-comparison-20260909/runs/E03-S test --tags /lab_qualification
python3 /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py --run /tmp/odoo-delegation-comparison-20260909/runs/E03-S inventory
python3 /home/blegoff/.odoo19-agents/benchmarks/delegation_comparison/runtime.py --run /tmp/odoo-delegation-comparison-20260909/runs/E03-S shell --script /chemin/du/script.py
bash /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo-lint.sh /tmp/odoo-delegation-comparison-20260909/runs/E03-S/project/lab_qualification
```

`test` met à jour votre module puis exécute les tests ; il exige les quatre tests initiaux et les nouveaux tests sélectionnés. Une sélection ciblée peut utiliser des options --expect Class.test_method explicites. Logs et noms réels sous runtime-evidence/. Aucune autre base, aucun accès direct Docker requis. Un seul acteur utilise la copie à la fois. Ne lancez pas cleanup ; le banc nettoie après réception. N’écrivez pas runtime.json, le runtime ou les entrées initiales.
