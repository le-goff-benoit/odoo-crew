# QA — PASS (ancienne portée)

Seule la création d’un brouillon vide a été vérifiée le 14 septembre. Les sélections mixtes, données existantes, saisies manuelles et parcours ultérieurs n’ont pas été contrôlés.

## 2026-09-16 — N-17 : QA de tâche renforcée

Rapport de réception structuré : [qa-N17.md](qa-N17.md), [couverture A1–A7](coverage.json).

- **Résultat de tâche : VALIDÉ.** Neuf méthodes de test vertes (aucun skip), après reproduction rouge métier ; installation et update sur QA OK. Détail : [exécution](preuves/runtime.md), [journal vert](preuves/green.log).
- **Copie synthétique lab_client : reprise appliquée et persistée.** Id 1 : 999 → 7. Ids 2/3/4 : 0/2/88 inchangés, dates d'écriture incluses. Rejeu sans write et relecture dans une nouvelle session : [preuve copie](preuves/client-copy.md), [avant/après](preuves/repair.log), [persisté](preuves/persisted.log).
- **Lint du diff : propre.** Ruff bloquant/conseils sans défaut. Le lint global reste rouge pour une dette antérieure unique : `author` absent du manifest inchangé. [Revue statique](preuves/static.md), [lint complet](preuves/lint.log).
- Réception relue par l'orchestrateur, **non indépendante**, conformément à LAB.md ; aucun sous-agent. Demande, N-17, sept critères, code, preuves et propositions mémoire confrontés sans ajout de règle métier.
- Incidents de preuve conservés : premier test ir.cron corrigé avec le montage standard avant le rouge confirmé ; première attestation d'update mal paramétrée (bilan de tests demandé pour une update seule), update réelle à code 0 puis attestation correcte. Voir implementation.md et client-copy.md.
- Limites : aucune recette complète, désinstallation, validation navigateur ou autre profil utilisateur ; aucun écran/droit modifié. Aucun déploiement. Comparaison standard 19.1 indisponible dans le banc.
- La release reste ouverte ; version 19.0.1.0.0 conservée jusqu'à clôture. Prévisions du travail restant dans estimation.md ; temps actif, jetons et coûts natifs indisponibles.
