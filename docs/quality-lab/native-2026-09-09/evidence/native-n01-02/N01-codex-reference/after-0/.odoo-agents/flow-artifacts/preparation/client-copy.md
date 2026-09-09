# QA copie synthétique — VALIDÉ
Série 19.0 ; lab_client ; exclusivement via /bridge/labctl, conformément à LAB.md.
Preuves dans changelog/2026-09-09_01_frais-de-preparation-des-locations/preuves/ : inventory.log, copy_before.log/json, copy-update.log, copy-validation.log, copy-reload.log et les scripts reproductibles.
Inventaire initial : 0 ligne, aucun champ manuel/action serveur/vue sur lab.rental. Quatre essais créés et commités avant modification (IDs 5 à 8), totaux 30/40/50/40.
/bridge/labctl update : succès, module rechargé, contraintes créées, zéro erreur. Les totaux restent 30/40/50/40 comme attendu d'un compute stocké modifié sans migration.
/bridge/labctl shell .../validate_copy.py : migration 19.0.1.0.1 exécutée explicitement deux fois, totaux 30/52/62/40, entrées identiques, assertions SQL et ORM vertes, commit.
/bridge/labctl shell .../verify_copy.py : nouvelle session, les quatre totaux sont persistés et corrects en SQL et ORM. Nettoyage des seuls quatre essais, commit ; copie vide comme avant.
C6 couvert. Autorisation locale issue de LAB.md et D-02 ; aucune production ni décision humaine supplémentaire requise.
Limite explicitée : le déclenchement automatique par changement de version sera contrôlé à la clôture après incrément du manifest. Le code de migration lui-même est exécuté et validé.
