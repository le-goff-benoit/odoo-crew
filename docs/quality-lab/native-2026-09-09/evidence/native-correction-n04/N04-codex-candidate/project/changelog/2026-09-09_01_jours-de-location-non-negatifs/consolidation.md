# Consolidation de tâche D-31
Source actuelle : decisions/2026-09-08.md, Luc Roy ; remplace la tolérance historique du 2026-08-01 dans JOURNAL.md. Aucun arbitrage restant sur borne ou technologie.
Réalisation : contrainte SQL native 19.0 days >= 0, aucune modification de daily_rate ni du calcul. C1-C5 reliés à D-31 dans revue_fonctionnelle.md et vérifiés dans qa.md.
Mémoire intégrée à PROJECT.md : décision durable, contrôle catalogue SQL, rollback/relecture, réserve author antérieure ; entrée JOURNAL.md datée du 2026-09-09.
Preuves nouvelles : tests négatifs rouges sur code d'origine, tests finaux verts, copie et nettoyage. L'historique permissif n'est plus une preuve du contrat courant.
Aucune leçon nouvelle à promouvoir : CheckViolation et QA des contraintes déjà couverts par le dispositif. Anomalie d'outillage locale documentée : author hors diff néanmoins signalé par le lint ciblé.
Release maintenue ouverte, aucune documentation client ni capture produite.
