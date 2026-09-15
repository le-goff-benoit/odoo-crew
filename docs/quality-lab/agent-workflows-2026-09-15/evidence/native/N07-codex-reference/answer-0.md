`/odoo-new` terminé selon N-17.

- Préparation, zéro manuel, duplication et reliquat corrigés.
- **9 tests verts après reproduction rouge**, installation/update validés.
- Reprise persistée : `999 → 7` ; saisies `0/2` et terminé `88` préservés. Rejeu sans écriture.
- Release ouverte, aucun déploiement.

Limites : relecture non indépendante ; lint global rouge uniquement pour l’absence préexistante de `author`, diff propre.

[Rapport QA et preuves](/work/changelog/2026-09-15_01_repair/qa.md)