# Auto-relecture de réception B-42 — 2026-09-16
Relecture explicitement non indépendante, même conversation/auteur selon LAB.md. Aucun garde de réception indépendante activé. Sources relues : demande originale, decisions/current.md (B-42), revue complète, preuves et versions complètes PROJECT.proposed.md/JOURNAL.proposed.md.

## Demande ↔ contrat
B-42 « uniquement ... self ... draft ... société ACTIVE env.company » est conservé dans C1 ; C2 garde le tri date puis id, le pas 100 et cancelled=False ; C3 conserve les quatre champs issued et toutes autres sociétés. C4 maintient les droits ; C5 borne la reprise à la société initiale de la copie ; C6 conserve rouge/vert, publication et release ouverte. Aucun arbitrage par simple date. L’ajout zéro write précise la preuve d’idempotence, sans élargissement de données.

## Contrat → preuves
C1/C2/C3 : six méthodes TestRepair, valeurs littérales indépendantes (100/200/300,20/0/15 et 0.004), témoins hors self et issued, changement de société active. red.log : 6 échecs métier ; green.json/log : mêmes tests verts, zéro skip. Aucun test calculant son oracle via action_repair.
C4 : tests with_user et copy-rights-v2.log « COPY_RIGHTS_PASS », su=False, succès puis AccessError sur lecture et write avec snapshots identiques après refus ; objets de recette annulés. Une simple identité admin n’a pas servi de preuve de droits ordinaires.
C5 : repair-authorized.log résultat XML-RPC true puis repair-verified.log « REPAIR_PASS » après relecture en autre transaction : ids 1/2=100/20,200/15, références préservées ; id 3/id 4 et huit lignes identiques au baseline ; rejeu espion zéro write.
C6 : update.log/exit 0 et contrôle installed, non le failed trompeur du reçu ; lint complet rouge uniquement author inchangé, Ruff bloquant vert, compilation et comparaison statique exactes. Publication de mémoire complète vérifiée avant réception du critère C6, puis nœud journal utilisé pour contrôler cette publication idempotente. Aucun résultat lié au déploiement prétendu.

## Sources → mémoire
PROJECT.proposed et JOURNAL.proposed préservent le texte antérieur et ajoutent explicitement résultat local, chiffres, exclusions, droits, réserve lint et relecture non indépendante. L’ancien « reste ouvert » reste dans son entrée historique datée, résolu par la nouvelle entrée. Pas de généralisation de l’autorisation locale vers production. Pas de faux compteurs d’effort.
Conclusion : dossier cohérent pour réception de tâche, avec dette préexistante et limites explicites. Release ouverte. La publication locale du journal est une obligation C6, vérifiée avant le pass ; la finalisation du flow la contrôle sans ajouter de doublon.
