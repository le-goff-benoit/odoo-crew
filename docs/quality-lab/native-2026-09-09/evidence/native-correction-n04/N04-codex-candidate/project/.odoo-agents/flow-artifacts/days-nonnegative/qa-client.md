# QA copie — lab_client synthétique, Odoo 19.0
Autorisation : LAB.md et demande ; toutes écritures sur copie synthétique permises. État initial inventorié vide (inventory-before.log).
1. `/bridge/labctl shell .../seed_copy.py` : création et commit d'une location temporaire avant update, jours=3, tarif=12.5, total=37.5 (copy-seed.log).
2. `/bridge/labctl update` : code 0, registre chargé en 4.955 s (copy-update.log). Aucun ERROR/CRITICAL. Warnings author antérieur et --without-demo all du pont (Odoo le traite True).
3. `/bridge/labctl shell .../check_copy.py` : PASS (copy-check.log). Valeurs de la location préservées après update ; CHECK ((days >= 0)) réellement installé et convalidated=true dans pg_constraint. Création et modification négatives lèvent CheckViolation sur lab_rental_days_nonnegative ; après chaque rejet la location reste 3/12.5/37.5. Zéro accepté en création et modification, recalcul jours/tarifs vérifié. Suppression des seules données QA puis commit.
4. Inventaire dans un nouveau shell (inventory-after.log) : zéro location, zéro négative, CHECK présent et validé. État métier initial restauré, schéma mis à niveau conservé.
C1-C5 : PASS sur copie. Aucun écran/droit modifié ; ni navigateur ni capture requis pour cette tâche.
