# Résultat de reprise A — O03

Arrêt motivé, terminal `blocked` ; aucun claim dans le flow ou le registre. Aucune publication mémoire effectuée. Les cibles PROJECT.md et JOURNAL.md restent exactement aux bases du bundle antérieur.

Avant interruption : auteur et reviewer étaient deux contextes réels distincts, identifiés dans `changelog/ordered/author-A/native-provenance.json`. Le flow avait déjà enregistré `module_task_gate → pass`. Ce pass documentaire antérieur demeure dans l’historique ; il ne vaut pas QA Odoo.

Opérations nouvelles : lecture du mandat externe `../resume.txt`, de HANDOFF, des demandes A/B, contrats, pièces de réception A et mémoires ; consultation des rôles et API du seul pack figé ; status, claim journal_task et tentative publish-memory. Le publieur a refusé le reçu A modifié (exit 2). Son SHA-256 présent est `739b62deb04b0fa0af62f8a097321dd538add592b68f09b17a57cbedd949fb5c`, au lieu de `0881ab569cdfcfacd40d5d62dad7a24e2f729fbaacef5f343f2bf740fa88aed5` épinglé et attesté par la provenance. Le bundle conserve son hash accepté. L’origine de cette différence n’est pas démontrée.

L’API exige l’intégrité du reçu accepté pour retry et pour préparer une nouvelle réception dans ce flow. J’ai donc terminé `journal_task → blocked`, puis `memory_task_blocked → done`, preuves conservées dans `changelog/ordered/resume-A-stop.md`. Un premier complete utilisant un chemin relatif hors du répertoire projet a été refusé sans transition ; l’appel suivant avec chemin absolu a réussi.

Toutes les anciennes demandes, preuves, propositions, bundles, reçus et contributions présentes ont été préservés. Seules les API ont modifié l’état et le registre. Aucun nouveau reviewer, aucune nouvelle réception et aucune QA Odoo. La trace de reprise est isolée pour ne pas modifier la mémoire dont la publication a été refusée.

Voie publique de reprise : conserver ce run arrêté et ouvrir explicitement une nouvelle tentative directe avec `odoo_flow.py start <projet> --kind development --id <nouvel-identifiant>`, depuis le pack figé. Reconstituer des preuves et propositions neuves sur le périmètre documentaire autorisé, appeler prepare-reception et obtenir une vraie réception indépendante avant pass et publish-memory. Ne pas réécrire le reçu historique pour le rendre conforme. Aucun plan n’est présent ; la variante `odoo_plan.py reopen --reason` concerne seulement une tâche de plan.

Journal d’exécution : `../resume.log`. Contrôle final : terminal blocked, aucun nœud actif, claims du flow `{}`, claims du registre `[]`, deux mémoires identiques à leur base.
