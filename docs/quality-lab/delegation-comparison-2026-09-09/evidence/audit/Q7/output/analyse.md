# Analyse fonctionnelle — quantités non négatives

Projet synthétique E01 · Odoo 19.0 · module lab_qualification 19.0.1.0.0.

**ÇA EXISTE dans le module fourni. Aucun développement supplémentaire recommandé.**

En tant qu’utilisateur, je veux empêcher l’enregistrement de quantités négatives, en saisie comme en import, tout en conservant les quantités à zéro pour les brouillons. La demande cherche à éviter des données incohérentes et un contrôle développé en double. Aucun incident réel, volume ni fréquence n’est fourni.

## Preuves et portée

- Briefing exécuté avant lecture du module : `python3 /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo_briefing.py /tmp/odoo-delegation-comparison-20260909/runs/E01-S/project --offline`. Série 19.0 confirmée ; aucune instance déclarée, aucune release ouverte.
- [Modèle fourni](../project/lab_qualification/models.py), lignes 16–18 : `_quantity_nonnegative = models.Constraint("CHECK(quantity >= 0)", "Quantity must be nonnegative.")`. La borne inclut zéro et exclut les valeurs négatives. Il n’y a aucune condition de statut ou d’utilisateur.
- [Initialisation](../project/lab_qualification/__init__.py) : le fichier des modèles est importé. Le [manifest](../project/lab_qualification/__manifest__.py) déclare le module installable, version 19.0.1.0.0. La [vue](../project/lab_qualification/views/quantity.xml) et les [accès](../project/lab_qualification/security/ir.model.access.csv) ont été lus ; la protection ne repose pas sur un contrôle d’écran.
- Source locale Odoo effectivement consultée : `/home/blegoff/odoo-sources/19.0/odoo/orm/table_objects.py`, lignes 79–99 et 109–122. `Constraint` porte une contrainte SQL et `apply_to_database` en organise l’ajout à la table. La [pièce fournie](../pieces/constraint-source.md) concorde avec cette source.
- Conséquence technique : **si la contrainte est installée dans la base**, elle s’applique aux écritures de la table, donc aux créations et modifications, y compris celles issues des imports. Il ne s’agit pas d’un simple contrôle au changement d’un champ dans le formulaire.

Cette lecture prouve la couverture dans le code fourni ; elle ne prouve ni la version déployée, ni la présence effective de la contrainte, ni la qualité des données dans une base client. Aucune exécution Odoo ni aucun essai d’import n’a été réalisé. Les pièces sont synthétiques.

## Décision et périmètre

Conserver le contrôle existant. Ajouter une contrainte Python, une automatisation Studio ou un autre contrôle SQL ferait doublon et augmenterait la maintenance à chaque migration sans bénéfice établi. Aucune nouvelle configuration ni reprise de données n’est justifiée par les pièces.

Le contrôle existant accepte aussi zéro sur une ligne confirmée. La demande exige de conserver zéro pour les brouillons, sans demander d’interdiction à la confirmation : ne pas ajouter cette nouvelle règle. D-17 reste acquise : prix zéro autorisé, y compris sur les lignes confirmées. SYN-11 reste clos ; le bouton ne change pas. Aucun changement de droits, de calcul du montant ou de modèle n’est demandé.

Il n’y a pas de question métier bloquante pour conclure à l’absence de développement à ajouter. La série suivante n’est pas consultée : seules les sources 19.0 sont autorisées dans cette épreuve et aucune extension à migrer n’est proposée.

## Critères pour une vérification ultérieure sur copie locale

Ces scénarios sont proposés, **non exécutés**. Ils reprennent la [demande](../demande.md) et les [décisions acquises](../project/.odoo-agents/PROJECT.md).

- Création et modification en saisie avec une quantité négative : enregistrement refusé, valeur négative non persistée.
- Import de création et import de mise à jour avec une quantité négative : ligne invalide refusée, valeur négative non persistée. Aucune atomicité de tout le fichier n’est ajoutée à l’exigence.
- Création, modification et import avec quantité zéro en brouillon : acceptés ; ligne conservée.
- Quantité positive : acceptée dans les mêmes canaux.
- Ligne gratuite avec prix zéro, y compris confirmée : demeure autorisée (D-17).
- Libellé du bouton : inchangé (SYN-11).

Prochaine étape, si une assurance sur l’installation réelle est attendue : le responsable technique vérifie la version du module et la contrainte sur une copie locale, puis la QA exécute les scénarios ci-dessus. En cas d’écart, diagnostiquer d’abord le déploiement ou les données avant d’envisager un correctif. Aucun accès client, flow de livraison ou chantier de développement n’est ouvert pour cette analyse.
