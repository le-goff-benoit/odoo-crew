# Projet documentaire
Le tableau conserve les décisions explicites.

## Décision A reçue — référence dossier
La référence dossier doit être visible dans la fiche interne. Ne pas ajouter de tri automatique. Cette décision reçue est conservée.

## Décision B — priorité du tableau de suivi
La priorité du tableau de suivi reste manuelle. Ne pas ajouter de tri automatique.
Le contrôle documentaire B a réussi : documentary/B/priority.txt contient exactement `priority=manual`.
Preuve : changelog/ordered/reception-B/evidence-B.json. Portée : uniquement documentary/B/priority.txt, fichier documentaire synthétique ; aucun contrôle Odoo.

## Résultat documentaire A reçu avant interruption
Le contrôle documentaire A a réussi : documentary/A/reference.txt contient exactement `reference_dossier=visible` suivi d’un saut de ligne.
Preuves acquises : changelog/ordered/reception-A/evidence-A.json et qa-A.md ; réception indépendante review-A.json acceptée par module_task_gate avant cette reprise.
Portée : uniquement ce fichier documentaire synthétique ; aucun test Odoo ni validation navigateur. La référence dossier reste visible dans la fiche interne ; ne pas ajouter de tri automatique.
La contribution B publiée, sa priorité manuelle et son résultat documentaire restent conservés ci-dessus.
