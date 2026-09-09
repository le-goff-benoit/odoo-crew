# Journal

## 2026-08-28 — SYN-11 résolu
Libellé du bouton accepté. Aucun changement complémentaire demandé.
D-17 confirmé : gratuité autorisée ; conserver cette exception.

## 2026-09-09 — SYN-42, diagnostic support synthétique
Classement : bug custom ; prix absent des dépendances du montant stocké.
Preuves : code Odoo 19.0 local et trace synthétique ; L7 reste à 30 au lieu de 36.
Impact démontré : une ligne, écart 6 ; volume réel et version déployée inconnus.
Contournement : contrôle manuel quantité × prix avant utilisation ; aucune réparation.
D-17 conservée : gratuité permise même confirmée ; SYN-11 reste clos.
Test rouge proposé dans output/diagnostic.md, non exécuté ; aucune exécution Odoo.
Suite : développeur/support reproduisent sur copie avant correction ; analyste si reprise de données.
Appris : un champ stocké doit déclarer chaque entrée lue ; vérifier prix seul après flush/relecture.
Aucun module ni mémoire initiale modifié ; livrables proposés dans output/.
