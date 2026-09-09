# Résultat de reprise O01

Publication cohérente obtenue. Les API `status` confirment A et B TERMINÉS, sans nœud actif ni claim conservé. La release reste ouverte.

Avant interruption, A avait un contrôle documentaire réussi et un reçu indépendant accepté par `module_task_gate`. B a ensuite publié sa mémoire et terminé son flow. Les traces natives antérieures restent dans `reception-A/native-provenance.json` et `reception-B/native-provenance.json` ; elles ne sont pas des opérations nouvelles de cette reprise.

Opérations nouvelles : le publieur a refusé A sur la base mémoire modifiée ; ce refus a conduit via API à `journal_task retry`, puis `reception_recovery_gate`. De nouveaux drafts ont conservé intégralement la mémoire B et ajouté explicitement le succès documentaire A déjà acquis, son fichier, ses preuves et ses limites. Sources, contrat, preuves et périmètre A sont identiques à l’ancien bundle. Le contexte neuf `/root/o01_resume/review_recovery` (`fork_turns=none`) a rendu une réception indépendante PASS. L’API a accepté cette réception, publié les octets exacts des deux drafts, terminé le journal puis `task_done`.

Les deux mémoires transmettent désormais les décisions A/B et les résultats réussis A/B, sans réduire le résultat A à la conservation de sa décision. Les 29 anciennes pièces contrôlées sont inchangées. Aucun état, registre ou plan n’a été édité directement ; aucune QA Odoo ou navigateur n’a été exécutée.

Preuves de reprise : `changelog/ordered/reception-A-resume/` contient le refus initial, le nouveau bundle, les bases figées, les drafts, le reçu indépendant, sa provenance, la publication et sa vérification. Commandes et sorties humaines : `../resume.log`.

Incident de périmètre consigné : une recherche initiale `rg --files` trop large dans `reference/docs` a listé des chemins historiques quality-lab ; aucun contenu de ces fichiers n’a été lu. Les lectures suivantes ont été ciblées sur la documentation publique et le seul projet O01. Un premier `complete` avec preuve relative a été refusé comme introuvable ; la même preuve absolue a été acceptée, sans édition d’état.

Aucun blocage restant ni action humaine requise pour cette reprise documentaire.
