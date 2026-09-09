Correction et reprise terminées sur la copie synthétique uniquement.

- `action_recalculate` exclut les lignes annulées et ignore strictement les validés.
- 7 tests rouges avant correction, puis **7/7 verts** ; installation et mises à jour réussies.
- Brouillon existant : **999 → 20**. Validé : **777 conservé**.
- Deuxième reprise : aucun changement, dates comprises ; persistance vérifiée indépendamment.

Ruff est vert. Le lint Odoo reste rouge pour `author` absent du manifest : dette préexistante prouvée, consignée dans la [QA sensible](/work/changelog/2026-09-09_01_recalcul-fiable-des-brouillons/qa.md).

[Journal](/work/.odoo-agents/JOURNAL.md) mis à jour. Graphe `/odoo-new` terminé ; **release laissée ouverte**.