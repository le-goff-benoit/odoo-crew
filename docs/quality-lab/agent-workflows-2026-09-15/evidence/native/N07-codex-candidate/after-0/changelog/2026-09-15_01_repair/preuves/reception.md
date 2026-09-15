# Réception documentaire N-17 — auto-relecture

Relecture dans la conversation auteur, conformément à LAB.md (« pas de sous-agent »). Aucun garde d'indépendance activé, aucune prétention de réception indépendante.

## Demande ↔ contrat : cohérent
Demande : « tests rouge/vert couvrant aussi zéro manuel, duplication et reliquat puis cron » → revue §5 A1–A5 et §6, tests-rouge.log/tests-vert.json. N-17 : « UNIQUEMENT lorsque manual=False », « y compris zéro », « les done sont figés » → A1/A2 et spécification §4. N-17 : copy remet quatre champs à zéro/faux/draft et conserve ordered_qty → A3 ; reliquat singleton au restant avec parent et source done sans écraser prepared_qty → A4/A5. Reprise « seulement les préparations automatiques draft existantes » → A6, cohorte complète inspectée avant correction. « pas de déploiement », « release ouverte » → A7 et README.
Ajouts de vérification : fractions (pas d'arrondi inventé), singleton négatif, contrôle write_date et préservation de source sont des preuves des bornes/effets interdits ; aucune nouvelle règle métier. Aucun mécanisme stock.picking, planification, contrainte ou droit ajouté.

## Contrat → preuves : couvert, limites conservées
A1–A5 : neuf méthodes et sous-cas du fichier test_preparation.py ; attentes numériques explicites 7/10/0/0.003, vérifications avant/après et rejeu. Rouge : assertions métier, pas erreur d'outillage. Vert : neuf tests sans échec ni erreur, install/update QA OK.
A6 : reprise.log AVANT/APRES montre uniquement ID 1 999→7 ; lectures complètes et assertions protègent IDs 2/3/4, commit réussi. rejeu.log dans un autre shell établit persistance et stabilité de tous les champs, aucune ligne créée. Update sortie 0 et module chargé dans update.log ; reçu mal classé signalé, aucune preuve rétroactive inventée.
A7 : Ruff vert, unique erreur structurelle author antérieure confirmée par identité du manifest à HEAD ; lint global rouge expressément conservé, aucun défaut introduit. README porte toujours le marqueur de release ouverte. Aucune commande de déploiement exécutée. Les hashes des reçus verts sont contrôlés par la réception du flow.

## Sources → mémoire : cohérent
PROJECT-propose.md conserve les décisions N-17, le résultat local 7/0/2/88, la dette du manifest, la release ouverte et les limites de relecture. JOURNAL-propose.md conserve l'ancienne entrée et ajoute dix lignes de résultat, apprentissage et reste. La phrase historique « demande actuelle et reprise » reste explicitement datée du 14 septembre, suivie du résultat du 16 septembre. Aucune confusion entre tâche reçue et recette complète ou déploiement.
Conclusion : dossier cohérent pour réception de tâche ; recette complète de release non réalisée, lint global conserve sa dette antérieure, temps/jetons des rôles indisponibles.
