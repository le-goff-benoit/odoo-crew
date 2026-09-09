# Journal

## 2026-08-28 — SYN-11 résolu
Libellé du bouton accepté. Aucun changement complémentaire demandé.
D-17 confirmé : gratuité autorisée ; conserver cette exception.

## 2026-09-09 — E03 : prix non négatif
Demande : interdire les prix négatifs, préserver gratuité, quantités, calcul et confirmation.
Fait : contrainte SQL 19.0 ajoutée ; module 19.0.1.0.1 ; 11 tests supplémentaires.
Preuve rouge : le code initial accepte les prix négatifs en ORM et par load.
QA : mise à jour locale réussie ; 15 tests verts, aucun ignoré ; lint bloquant propre.
Données : trois lignes initiales strictement conservées après mise à jour.
Appris : CheckViolation en ORM direct ; load annule son lot et retourne un message d'erreur.
D-17 maintenu ; SYN-11 reste clos. Aucune décision métier nouvelle requise.
Limite : copie synthétique uniquement, aucune opération client ni production.
Suite : réception indépendante par le responsable du banc après gel ; preuves dans output/qa.md.
