# QA copie finale — reprise 1

Odoo 19.0, lab_client entièrement synthétique, Codex rôle testeur.
Autorisation : LAB.md et D-02 ; aucune production ni donnée client réelle.

- Inventaire initial vide, quatre témoins créés sous ancienne formule (seed_before.log).
- Update seul : totaux inchangés 30/40/50/40 (after_update_before_recompute.log).
- Première reprise : totaux 30/52/62/40, mêmes entrées (copy_check_attempt1.log).
- Code final : `copy_final.json/log` lie l'update et les contrôles aux empreintes du module et du script de reprise.
- Update final réussi, deux rejeux supplémentaires du script, chaque fois relus dans un nouveau shell Odoo : 30/52/62/40, noms/jours/tarifs/types inchangés. Idempotence démontrée.
- Quatre témoins supprimés après validation ; copie revenue à zéro location, comme à l'inventaire initial. Module laissé à jour.

Verdict : VALIDÉ, C7 couvert. Aucune anomalie métier ; avertissement CLI du transport consigné en QA générale.
