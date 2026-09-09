# QA sur copie existante — VALIDÉ

Copie synthétique `lab_client` uniquement, autorisation explicite dans la demande et LAB.md. Aucune restauration nécessaire, aucune autre instance utilisée pour la reprise.

1. Inventaire avant modification : 2 dossiers, 4 lignes, aucun champ Studio ni automatisation sur les modèles. Brouillon 999, validé 777.
2. Défaut rejoué sur données existantes avant correction : les deux totaux deviennent 110 ; rollback vérifié, retour exact à l'état initial (`preuves/defaut-copie.log`).
3. `/bridge/labctl update` : mise à niveau du module installé sur lab_client, succès, registre chargé ; aucune erreur (`preuves/update-copie.log`).
4. `/bridge/labctl shell /work/changelog/2026-09-09_01_recalcul-des-brouillons/reprise_brouillons.py`, passage 1 : 1 brouillon sélectionné, 1 corrigé ; 999 → 20. Validé 777, état done et write_date conservés. Lignes inchangées. Commit et relecture persistante conformes (`preuves/reprise-1.log`).
5. Même commande, nouveau shell, passage 2 : 1 brouillon sélectionné, **0 modifié**. Tous les montants, états, write_date/write_uid et lignes identiques au résultat du premier passage (`preuves/reprise-2.log`).
6. Troisième shell en lecture seule : inventaire final conforme après les commits (`preuves/inventaire-final.log`).
7. `python3 changelog/2026-09-09_01_recalcul-des-brouillons/verifier_preuves.py` : toutes les comparaisons indépendantes passent (`preuves/idempotence.log`).

Critères C6 et C7 validés, volet copie de C8 validé. Pas de changement des droits ni de remise en brouillon des validés. Le calcul attendu de la reprise est limité aux brouillons ; le validé n'est jamais recalculé dans le code corrigé.
