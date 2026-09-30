# Décisions remplacées et réception du plan — 17 septembre 2026

Référence : 48ae92fb529eb8fcf37e0cbb7b1c01f57bbe0b6b, arborescence propre avant ce correctif.
Défaut : impact_sources vérifiait les sources de toutes les anciennes décisions acceptées, même explicitement remplacées. Une demande évoluée pouvait rendre impossible la réception malgré une lecture mémoire courante valide.
Cas synthétique figé avant correction : D1 liée à request.md, source révisée puis D2 acceptée remplaçant D1. Rouge : un échec sur deux tests. Correction : considérer les seules décisions courantes pour les impacts, sans effacer les contributions historiques.
Contre-épreuve : une décision actuelle dont la source change reste refusée ; absence de successeur reste refusée également. Les mêmes appels et sources sont conservés avant/après. Aucun cas client dans ce corpus.
Adopté localement dans scripts/odoo_knowledge.py : 38 tests mémoire/plan verts, puis build isolé validant graphe, suite déterministe entière (396 tests, un ignoré) et parité des profils. Logs locaux /tmp/rubix-tool-knowledge-{red,green,build}.log.
Aucune instruction ou profil changé : outil canonique utilisé directement, distribution isolée /tmp/rubix-knowledge-superseded-build ; profils actifs inchangés. Aucun appel LLM de banc, aucun gain de durée/qualité de modèles mesuré, aucun commit/push.
