# QA — PASS (ancienne portée)

Seule la création d’un brouillon vide a été vérifiée le 14 septembre. Les sélections mixtes, données existantes, saisies manuelles et parcours ultérieurs n’ont pas été contrôlés.

## 16 septembre 2026 — tâche N-17, Odoo 19.0

Réception structurée : [rapport N-17](qa-n17.md), [couverture des 7 critères](coverage.json). L'ancienne QA ci-dessus reste historique et ne sert pas de preuve pour cette tâche.

- Rouge réel : 14 assertions échouées dans 9 tests. Vert : 9 tests, 0 échec, 0 erreur, installation et update QA réussis (9 s).
- Copie lab_client mise à jour (sortie 0), reprise persistée : seule LEGACY_AUTO passe de 999 à 7 ; valeurs manuelles 0/2 et done 88 intactes. Rejeu dans un nouveau processus : tous les champs, write_date compris, inchangés.
- Ruff sans anomalie ; lint Odoo complet/ciblé conserve une unique dette structurelle antérieure : author absent du manifest, inchangé depuis HEAD. Aucun défaut trouvé dans le diff. **Le lint global reste rouge sur cette dette.**
- Limite de capture : update.json est marqué failed parce que --module réclame un bilan tests ; l'update réel a fini avec exit_code=0 et module chargé dans update.log. Ce reçu n'est pas présenté comme vert ni réécrit.
- Relecture non indépendante imposée par LAB.md ; ni navigateur, ni désinstallation, ni recette complète de release exécutés. Aucun droit/interface ajouté, aucune exigence RPC dans N-17.

Fragments : [statique](preuves/qa-statique.md), [exécution](preuves/qa-runtime.md), [copie](preuves/qa-copie.md), [réception](preuves/reception.md).
Preuves : [rouge](preuves/tests-rouge.log), [vert](preuves/tests-vert.json), [lint](preuves/lint.log), [update](preuves/update.log), [reprise](preuves/reprise.json), [rejeu](preuves/rejeu.json).
Release laissée ouverte, version 19.0.1.0.0 conservée, aucun commit ni déploiement.
