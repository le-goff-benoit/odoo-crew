# Journal documentaire
Initialisation du dossier.

## 2026-09-09 — Conservation de la décision A reçue
Décision conservée : afficher la référence dossier dans la fiche interne ; ne pas ajouter de tri automatique.

## 2026-09-09 — Demande B
Demande : conserver la priorité manuelle du tableau de suivi ; ne pas ajouter de tri automatique.
Fait : décision consignée dans les propositions mémoire ; contenu documentaire vérifié.
Verdict : contrôle documentaire B réussi ; documentary/B/priority.txt contient exactement `priority=manual`.
Preuve : changelog/ordered/reception-B/evidence-B.json.
Portée : uniquement documentary/B/priority.txt, fichier synthétique ; aucun contrôle Odoo.
Appris : la demande B conserve la priorité manuelle et n’autorise aucun tri automatique.

## 2026-09-09 — Reprise mémoire A après réception acquise
Demande : afficher la référence dossier dans la fiche interne ; ne pas ajouter de tri automatique.
Verdict acquis avant interruption : contrôle documentaire A réussi ; documentary/A/reference.txt contient exactement `reference_dossier=visible` suivi d’un saut de ligne.
Preuves : changelog/ordered/reception-A/evidence-A.json et qa-A.md ; reçu indépendant review-A.json accepté par module_task_gate avant cette reprise.
Portée : uniquement documentary/A/reference.txt, fichier synthétique ; aucun test Odoo ni validation navigateur.
Fait nouveau : publication initiale refusée par API car B a publié sa mémoire ; nouveaux drafts préparés depuis ces bases en conservant intégralement décisions et succès B.
Appris : la présence de la décision A seule ne transmet pas le résultat documentaire A déjà reçu.
Reste ouvert au moment de cette proposition : nouvelle réception indépendante de la fusion, publication par API puis terminaison du flow A.
