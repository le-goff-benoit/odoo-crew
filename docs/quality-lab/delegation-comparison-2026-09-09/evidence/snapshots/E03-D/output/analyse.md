# Analyse courte — prix non négatif

Série 19.0, confirmée par le briefing hors ligne. Demande originale dans `../demande.md` et décisions D-17 / SYN-11 dans la mémoire initiale.

La demande est saine : empêcher toute ligne à prix négatif sans perdre les lignes gratuites ou les données valides. Le modèle custom contrôle déjà la quantité par SQL et calcule le montant. Il lui manque uniquement la contrainte de prix. Aucun besoin de modifier le bouton, les vues ou les droits.

Configuration : aucun paramètre du modèle ne porte cette règle. Studio : automatisation supplémentaire à maintenir, sans avantage pour ce modèle déjà custom. Code retenu : une `models.Constraint` 19.0, comme les contrôles de dimensions de `stock/models/stock_package_type.py:45`. Faible coût de migration ; vérifier la contrainte à chaque mise à niveau. Pas de réimplémentation de create, write ou load.

Critères fixés avant correction :
- Prix strictement négatif refusé en création et modification, brouillon ou confirmé, y compris une petite valeur négative sans arrondi arbitraire.
- Prix zéro et prix positif autorisés ; quantité zéro autorisée, quantité négative refusée.
- Montant recalculé comme quantité × prix après création et modification ; confirmation conservée, y compris gratuité.
- Création et écriture sur plusieurs lignes : échec sans conservation partielle du lot dans la transaction.
- Import `load` : acceptation des lots valides, rejet d'un lot contenant un prix ou une quantité négative ; aucune création ou modification partielle persistante.
- Les trois lignes préexistantes restent identiques après mise à jour et tests.

Inventaire initial exécuté sur la copie synthétique fournie : 3 lignes (payante 3 × 12 = 36 ; gratuite 4 × 0 = 0 ; vide 0 × 11 = 0). Aucun prix ni quantité négatif. Aucune reprise de données nécessaire sur cette copie.

Preuves source locales : `odoo/orm/models.py:895-1065` (load, savepoint, rollback en présence d'erreur) ; `odoo/addons/base/tests/test_sql.py:181` (exception SQL CheckViolation). Sources sous `/home/blegoff/odoo-sources/19.0`, lecture seule.

Aucune question bloquante. QA ciblée sur le runtime autorisé. Cette épreuve synthétique n'atteste ni d'une base client ni d'un déploiement.
