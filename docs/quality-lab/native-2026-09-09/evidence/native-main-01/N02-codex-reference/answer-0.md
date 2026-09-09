Correction et reprise locale terminées selon D-12. `/odoo-new` est **VALIDÉ**, release laissée ouverte.

- `action_recalculate` exclut les lignes annulées, traite les brouillons et ignore les validés, y compris en sélection mixte.
- **6 tests rouges avant correction, puis 6/6 verts** ; lint et mises à niveau réussis.
- Copie synthétique : brouillon **999 → 20**, validé **777 inchangé**.
- Reprise idempotente prouvée : **1 écriture au premier passage, 0 au second**, puis relecture indépendante après commit.

[QA sensible et preuves](/work/changelog/2026-09-09_01_recalcul-fiable-des-brouillons/qa.md) · [Journal](/work/.odoo-agents/JOURNAL.md)

La recette complète reste à la clôture. Seule réserve préexistante : manifest sans `author`. Aucun commit ni déploiement effectué.