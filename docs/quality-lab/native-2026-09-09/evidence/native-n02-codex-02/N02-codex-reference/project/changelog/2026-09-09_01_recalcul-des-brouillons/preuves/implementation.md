# Implémentation sensible — 19.0

Spec : `changelog/2026-09-09_01_recalcul-des-brouillons/revue_fonctionnelle.md`.
Correction de `lab_dispatch/models/business.py`, tests (`common.py`, `test_recalculate.py`, import), script local versionné `reprise_brouillons.py` dans la release.
Précédent 19.0 : `addons/sale/models/sale_order.py:694` et `addons/stock/models/stock_picking.py:1201` filtrent les brouillons avant action.

- Rouge réel sur code original : installation effective via `/bridge/labctl qa lab_dispatch --fresh --no-template --tags /lab_dispatch:TestRecalculate`, **6 échecs, 0 erreur, 7 tests**, 20 s. `preuves/test-rouge.log`.
- Copie existante avant correction : brouillon et validé deviennent 110 ; rollback et relecture confirment le retour à 999 et 777. `preuves/defaut-copie.log`.
- Vert sur code corrigé : `/bridge/labctl qa lab_dispatch --quick --tags /lab_dispatch:TestRecalculate`, **7/7**, 6 s, mise à jour OK. `preuves/test-vert.log`.
- Le script de reprise restreint la base à lab_client, sélectionne les seuls brouillons, réutilise l'action, vérifie les montants attendus et la conservation des autres données avant commit. Les deux passages restent à exécuter dans le nœud copie client.
- Aucun changement de droits, d'état, de schéma ni de version (19.0.1.0.0 ; release ouverte).

Incident du banc : `--quick` choisit -u dès que la base existe, même vide ; `--fresh --quick` conserve ce problème. Deux appels à zéro test sont archivés, exclus des preuves vertes. Une installation sans `--quick` a résolu le contrôle. Le dispositif est resté en lecture seule.
Lint initial incomplet faute de ruff ; ruff 0.16.6 installé dans `/work/.venv-lint`, puis lint ciblé relancé avec cette entrée PATH. Résultat dans `preuves/lint.log`.
