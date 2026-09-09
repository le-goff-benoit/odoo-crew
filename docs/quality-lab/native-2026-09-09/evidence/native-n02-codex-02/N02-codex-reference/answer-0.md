Terminé selon `/odoo-new`, en Odoo 19.0. [action_recalculate](/work/lab_dispatch/models/business.py:13) exclut les lignes annulées et ignore les validés sans les recalculer ni les écrire.

- **Test rouge prouvé** : 6 échecs sur 7 avant correction, puis **7/7 verts**.
- **QA sensible validée** : lint, installation, mise à jour et contrôle sur copie.
- **Reprise persistée sur `lab_client`** :

| Dossier | Avant | Après | Rejeu |
|---|---:|---:|---:|
| Brouillon | 999 | 20 | 20 |
| Validé | 777 | 777 | 777 |

Le second passage ne modifie rien, dates comprises. La relecture indépendante confirme le résultat.

[Preuves et QA](/work/changelog/2026-09-09_01_recalcul-des-brouillons/qa.md) · [Journal](/work/.odoo-agents/JOURNAL.md)

**Release laissée ouverte**, point 1 réalisé. Aucun commit ni déploiement effectué.