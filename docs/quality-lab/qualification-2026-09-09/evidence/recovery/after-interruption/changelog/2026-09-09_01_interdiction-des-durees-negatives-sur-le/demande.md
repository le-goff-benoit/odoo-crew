# Demande

<!-- Copier chaque demande telle quelle, datée. Ne pas reformuler. -->

Applique /odoo-new sur lab_rental : interdire les jours négatifs par une contrainte SQL Odoo, en conservant les jours nuls valides et le calcul du total existant. Écris les tests de création et modification refusées, y compris la conservation d'une location valide après rejet. Le contrat est entièrement arbitré dans decisions/2026-09-08.md. Effectue la QA de tâche sur la copie et le journal, release ouverte. Aucun écran ni droit à modifier.


## Décision D-31 (decisions/2026-09-08.md, versée telle quelle)

D-31 actée par Luc Roy, responsable fictif : lab.rental.days >= 0, contrainte SQL explicitement demandée. Zéro autorisé. daily_rate et amount_total ne changent pas de règle (jours × tarif). Les seuls enregistrements de la copie sont synthétiques. Q1 borne zéro : inclus ; Q2 type de contrainte : SQL. Aucune facturation ni mise en production.


Extension synthétique fixée avant cette qualification de reprise : A8 obligatoire : le rejet d’une création avec days=-1 doit être constaté via le vrai XML-RPC et retourner le message « Le nombre de jours doit être positif ou nul. ». Vérifie la conservation des données après rejet. Le code sans appel RPC ne satisfait pas A8.
