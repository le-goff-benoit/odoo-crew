Réalisé sur `lab_rental` en Odoo 19.0 : contrainte SQL `CHECK(days >= 0)`, zéro autorisé et calcul du total inchangé. Aucun écran ni droit modifié.

- **4/4 tests passent**, notamment la conservation d’une location valide après rejet.
- Mise à niveau et scénarios sur `lab_client` réussis ; contrainte PostgreSQL validée.
- Journal écrit et release laissée ouverte.

**Réserve :** Ruff est vert, mais le lint global reste rouge pour `author` absent du manifest, défaut préexistant prouvé.

Détails : [QA de tâche](/work/changelog/2026-09-09_01_jours-de-location-non-negatifs/qa.md) · [Journal](/work/.odoo-agents/JOURNAL.md).