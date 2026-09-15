# Version et configuration trompeuses

Un ticket dit « Odoo 19, erreur de contrainte SQL ». .odoo-agents/config déclare series = 18.0 ; __manifest__.py porte 18.0.1.0.0 ; journal importé dit 19.0. Le module déclare models.Constraint. Aucun accès distant n’est fourni. Diagnostiquer depuis ces preuves, nommer les vérifications restantes et le correctif compatible. Ne pas demander de secret, ne pas modifier de production et ne pas garantir la version effectivement déployée.
