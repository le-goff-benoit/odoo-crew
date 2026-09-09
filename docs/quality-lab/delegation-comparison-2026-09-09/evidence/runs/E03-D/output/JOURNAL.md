# Journal

## 2026-08-28 — SYN-11 résolu
Libellé du bouton accepté. Aucun changement complémentaire demandé.
D-17 confirmé : gratuité autorisée ; conserver cette exception.

## 2026-09-09 — E03 : interdire les prix négatifs
Demande : contrôler prix et quantité sur saisie, import et lots sans perdre les lignes valides.
Fait : contrainte SQL 19.0, version 19.0.1.0.1 et dix nouveaux tests ; bouton conservé.
Verdict : QA ciblée locale validée, 14 tests réussis et lint bloquant sans erreur.
Preuve : tests rouges avant correctif ; tests verts après mise à jour ; trois lignes initiales inchangées.
D-17 conservée : prix zéro autorisé, y compris confirmé ; SYN-11 reste résolu.
Appris : load annule son lot en erreur ; les écritures ORM différées doivent être flushées dans le savepoint du test.
Limites : copie synthétique exclusivement ; aucune production ni recette navigateur exécutée.
Suite : réception indépendante par le banc ; dossier de preuve dans output/qa.md.
