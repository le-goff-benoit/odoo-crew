# QA exécution renforcée — VALIDÉ

19.0 (manifest), lab_dispatch, mode tâche.

- Rouge : code initial conservé dans `preuves/business-original.py` ; 6 échecs, 0 erreur sur 7 tests. Les échecs portent sur les lignes annulées, les snapshots validés, la sélection mixte et le rejeu. `preuves/test-rouge.log`.
- Vert ciblé : mise à jour du code corrigé, 7/7, 0 erreur, 0 ignoré ; 6 s (`preuves/test-vert.log`).
- Contrôle installation du code final sur base neuve, mise à jour et tests : `/bridge/labctl qa lab_dispatch --fresh --no-template --update --tags /lab_dispatch:TestRecalculate`. Résultat réel dans `preuves/qa-install-update.log` : installation OK, update OK, 7/7, 0 échec, 0 erreur, 0 ignoré.
- Les sept tests ciblés constituent toute la suite Python actuelle du module ; pas de tour ni vue dans ce module.
- Les tests utilisent le BaseCommon 19.0 (utilisateur interne, sans sudo dans l'action). Aucun groupe ajouté ; pas de modification du périmètre des droits.
- Avertissements préexistants : manifest sans auteur ; avertissements d'options du lanceur (`without-demo=all`, http-interface). Pas de warning de vue.
- C1–C5 et volet install/update/tests de C8 couverts. C6–C7 attendent la copie existante.
