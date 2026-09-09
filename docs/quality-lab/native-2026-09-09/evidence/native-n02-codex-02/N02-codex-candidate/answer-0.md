Corrigé et validé selon D-12 sur Odoo 19.0.

- `action_recalculate` exclut les lignes annulées et ignore les validés, même en sélection mixte.
- Test rouge reproduit, puis **6/6 tests verts** ; lint, installation et mise à niveau réussis.
- Reprise sur `lab_client` : brouillon **999 → 20**, validé **777 inchangé**.
- Second passage : **zéro modification**, dates comprises.

[QA et preuves](/work/changelog/2026-09-09_01_recalcul-des-brouillons-d12/qa.md) · [Journal](/work/.odoo-agents/JOURNAL.md)

Graphe terminé ; release laissée **ouverte**, 1/1 point réalisé. Recette complète réservée à `/odoo-close`. Aucun déploiement.