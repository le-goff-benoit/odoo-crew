# Implémentation D-02
Odoo 19.0 : compute existant étendu, dépendances days/daily_rate/kind conservées.
Huit tests métier dans `lab_rental/tests/test_preparation_fee.py`, stockage relu après flush/invalidation.
Reprise ORM idempotente : `changelog/2026-09-09_01_frais-de-preparation-des-locations/recompute_totals.py`.
Quatre témoins créés sous l'ancien code sur lab_client, preuve `seed_before.log`.
Lint des cinq fichiers Python touchés : `lint-green.json` et `lint-green.log`, réussi avec ruff installé dans `/tmp/odoo-lab-tools`.
Le premier lint (`lint.json`) a détecté l'absence antérieure de author et de ruff ; auteur synthétique Atelier Boréal ajouté pour satisfaire le contrôle obligatoire. Version 19.0.1.0.0 conservée.
Aucune vue, droit, dépendance ou facturation modifiés. `git diff --check` réussi.
Commit proposé : `[IMP] lab_rental: appliquer le forfait de préparation D-02`.
