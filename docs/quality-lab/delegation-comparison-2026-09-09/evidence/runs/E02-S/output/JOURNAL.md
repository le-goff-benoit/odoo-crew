# Journal

## 2026-08-28 — SYN-11 résolu
Libellé du bouton accepté. Aucun changement complémentaire demandé.
D-17 confirmé : gratuité autorisée ; conserver cette exception.

## 2026-09-09 — SYN-42 : diagnostic support
Classement : bug custom ; dépendance unit_price manquante dans le calcul stocké amount.
Preuves : code local 19.0, mécanisme ORM lu dans les sources et trace synthétique fournie.
Impact démontré : une ligne synthétique à 30 au lieu de 36 ; impact client inconnu.
Contournement : contrôle quantité × prix et mise à l'écart des montants incohérents.
D-17 conservé : prix zéro et confirmation des lignes gratuites autorisés ; SYN-11 reste clos.
Test rouge proposé, non exécuté ; développeur chargé de la reproduction locale avant correction.
Anciennes données : analyse distincte avant réparation ; aucun recalcul autorisé en production.
Aucun module modifié, test Odoo exécuté ou accès client effectué.
Appris : un calcul stocké doit déclarer tous ses champs sources ; tester le prix seul après flush/relecture.
Détail : output/diagnostic.md ; compte rendu : output/result.md.
