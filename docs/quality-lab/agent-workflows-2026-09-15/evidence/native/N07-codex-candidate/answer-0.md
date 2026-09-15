`/odoo-new` terminé selon N-17 : préparation périodique, zéro manuel, duplication et reliquat corrigés.

- **9 tests verts**, après reproduction rouge, incluant duplication/reliquat puis cron.
- Copie locale reprise : **999 → 7** ; valeurs protégées **0, 2 et 88** intactes. Rejeu stable.
- Ruff passe ; lint global toujours rouge pour la dette préexistante `author` absent du manifest.
- Journal actualisé, release **ouverte**, aucun déploiement. Relecture non indépendante conformément à `LAB.md`.

[QA et preuves](/work/changelog/2026-09-15_01_repair/qa.md).