# QA copie sensible — VALIDÉ

Module lab_dispatch · Odoo 19.0 (manifest) · lab_client synthétique uniquement.
Mise à niveau réelle : `client-update.json` / `.log`, module chargé, sortie 0.
Reprise scriptée `reprise.py` : `reprise-1.json` / `.log`, commit, 1 brouillon modifié (id 1, 999 → 20), 1 validé (id 2, 777) inchangé.
Second processus shell : `reprise-2.json` / `.log`, commit, 0 changement ; avant = après du premier passage = après du second passage, write_date et write_uid compris.
Troisième processus en lecture seule : `client-final.json` / `.log`, valeurs persistées 20/777 et lignes identiques à l'inventaire avant intervention.
Vérification croisée exécutée : `verify_reprise.py` et `verify-reprise.log`. C5/C6 satisfaits ; validé identique avant mise à niveau et après reprise, aucune transition d'état, aucune modification des lignes.
Tous ces fichiers de preuve sont dans `changelog/2026-09-09_01_recalcul-des-brouillons-d12/` ; inventaire initial dans ce dossier de flow-artifacts.
Autorisation : demande utilisateur et LAB.md ; aucune opération distante ou de production.
