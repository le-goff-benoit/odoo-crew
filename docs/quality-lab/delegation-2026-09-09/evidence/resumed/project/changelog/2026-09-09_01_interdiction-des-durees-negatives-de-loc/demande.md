# Demande

<!-- Copier chaque demande telle quelle, datée. Ne pas reformuler. -->


## 2026-09-09 — Demande (telle quelle)

Applique /odoo-new sur lab_rental : interdire les jours négatifs par une contrainte SQL Odoo, en conservant les jours nuls valides et le calcul du total existant. Écris les tests de création et modification refusées, y compris la conservation d'une location valide après rejet. Le contrat est entièrement arbitré dans decisions/2026-09-08.md. Effectue la QA de tâche sur la copie et le journal, release ouverte. Aucun écran ni droit à modifier.

**Décision de référence** — `decisions/2026-09-08.md` (D-31, Luc Roy) :
lab.rental.days >= 0, contrainte SQL explicitement demandée. Zéro autorisé. daily_rate et amount_total ne changent pas de règle (jours × tarif). Les seuls enregistrements de la copie sont synthétiques. Q1 borne zéro : inclus ; Q2 type de contrainte : SQL. Aucune facturation ni mise en production.
