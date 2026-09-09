# QA exécution finale — reprise 1

Odoo 19.0, lab_rental, Codex rôle testeur.

- `runtime_final.json/log` : `/bridge/labctl qa lab_rental --quick --tags /lab_rental:TestPreparationFees --fresh` : installation neuve OK, 10/10 méthodes, zéro erreur/échec/skip, 11 s.
- `runtime_update.json/log` : même sélection avec `--update` : installation existante/mise à jour OK, 10/10 méthodes, zéro erreur/échec/skip, 4 s.
- Les dix méthodes sont toute la suite actuelle du module ; point de contrôle complet couvert par la même sélection.
- C1–C6 validés : borne inclusive, prêts exclus, zéro et décimales, chaque dépendance, lot et absence de cumul, relecture stockée, refus des négatifs.
- Aucun warning lié au module. Le transport utilise encore `--without-demo=all`, interprété True par Odoo 19.0 ; avertissement d'outillage conservé, sans conséquence sur ces tests qui créent leurs données. Pas de modification du dispositif en lecture seule.

Verdict exécution : VALIDÉ. Première tentative rouge conservée dans runtime.json/log et qa_runtime_attempt1.md.
