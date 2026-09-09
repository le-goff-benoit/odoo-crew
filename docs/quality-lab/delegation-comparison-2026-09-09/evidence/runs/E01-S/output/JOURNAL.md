# Journal

## 2026-08-28 — SYN-11 résolu
Libellé du bouton accepté. Aucun changement complémentaire demandé.
D-17 confirmé : gratuité autorisée ; conserver cette exception.

## 2026-09-09 — E01, analyse des quantités
Demande : refuser les quantités négatives, imports inclus ; garder zéro en brouillon.
Série 19.0 confirmée par briefing hors ligne avant lecture.
Verdict : contrôle déjà présent dans le module fourni, models.py:16–18.
Source ORM 19.0 consultée : table_objects.py:79–122, contrainte SQL de table.
Aucun développement supplémentaire recommandé ; aucune modification du projet.
D-17 conservée : prix zéro permis, y compris confirmé ; SYN-11 reste clos.
Preuves et critères proposés : output/analyse.md ; compte rendu : output/result.md.
Analyse statique synthétique seulement ; aucun test Odoo ni état client vérifié.
Suite éventuelle : responsable technique puis QA sur copie locale pour version, contrainte et scénarios de saisie/import.
