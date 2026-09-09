# QA copie synthétique — VALIDÉ

Copie lab_client, écritures autorisées par LAB.md/D-02, aucune production.
Inventaire initial réel : zéro location et aucune personnalisation concurrente.
Avant changement du code : seed_before_update.py crée trois fixtures et commit ; totaux stockés 30/40/40 (before-update.log).
`/bridge/labctl update` : succès sur module installé (client-update.log). Inventaire après update : toujours 30/40/40, preuve qu'un -u seul ne reprend pas la formule stockée.
`/bridge/labctl shell /work/changelog/2026-09-09_01_frais-de-preparation-d-02/scripts/recompute_lab_totals.py` exécuté deux fois (recompute-first.log, recompute-second.log), succès à chaque fois.
Après chaque reprise, verify_copy.py exécuté dans un processus shell distinct : 30/52/40, mêmes jours/tarifs/types/noms et recherche par total correcte (verify-first.log, verify-second.log).
Nettoyage par cleanup_copy.py : suppression des trois fixtures uniquement, modèle vide comme à l'inventaire initial (cleanup.log), commit confirmé.
C6 couvert : valeurs antérieures, update, reprise stockée et idempotence. C7 respecté.
Le script livré est volontairement limité par garde à lab_client ; aucune autorisation de déploiement implicite. À la clôture, conserver la reprise explicite et prévoir l'incrément de version.
