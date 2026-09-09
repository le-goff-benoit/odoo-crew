# Analyse fonctionnelle — quantités non négatives

Projet synthétique E01 · Odoo 19.0 · module `lab_qualification` 19.0.1.0.0.

## Besoin et verdict
En tant qu'utilisateur, je veux empêcher l'enregistrement de quantités négatives, en saisie et à l'import, tout en conservant les lignes à zéro comme brouillons et en évitant un contrôle en double.

**ÇA EXISTE dans le module fourni. Aucun développement supplémentaire justifié.**
Le besoin est sain. Aucun incident concret, volume ou fréquence d'erreur n'est fourni.

`project/lab_qualification/models.py:16` déclare `_quantity_nonnegative = models.Constraint("CHECK(quantity >= 0)", ...)`. La borne est inclusive : une quantité de -1 est interdite, 0 et 1 sont acceptées par cette règle. Le champ est entier (`models.py:9`). La contrainte ne dépend ni de l'état, ni de l'utilisateur : elle couvre création et modification des lignes, y compris confirmées. Elle ne rend pas obligatoire une quantité strictement positive à la confirmation.

Il s'agit d'une règle métier custom déjà écrite, utilisant le mécanisme standard de contrainte SQL Odoo 19.0. Ce n'est pas une simple validation du formulaire. Le fichier `__init__.py` importe `models` et le manifest est installable dans la série 19.0 ; ceci établit le câblage source, pas l'installation effective.

## Preuves consultées
- Briefing exécuté avant la lecture du code : `python3 /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo_briefing.py /tmp/odoo-delegation-comparison-20260909/runs/E01-D/project --offline` ; série 19.0, aucune instance déclarée, aucune release ouverte.
- Demande originale : `../demande.md` ; décisions D-17 et SYN-11 : `../project/.odoo-agents/PROJECT.md` et journal initial.
- Module complet lu : `../project/lab_qualification/models.py`, `__init__.py`, `__manifest__.py`, `views/quantity.xml`, `security/ir.model.access.csv`.
- Pièce synthétique : `../pieces/constraint-source.md`. Elle ne prouve pas l'état d'une base client.
- Source framework locale effectivement lue : `/home/blegoff/odoo-sources/19.0/odoo/orm/table_objects.py:79` ; `Constraint` représente une contrainte SQL de table. `apply_to_database` compare la définition et programme son ajout en base.
- Parcours d'import effectivement lu : `/home/blegoff/odoo-sources/19.0/addons/base_import/models/base_import.py:1495` appelle `model.load`. `/home/blegoff/odoo-sources/19.0/odoo/orm/models.py:895` charge les lignes via `_load_records` ; `_load_records_write` et `_load_records_create` (lignes 5083 et 5100) appellent `write` et `create`. Ces écritures restent soumises à la contrainte SQL installée.

Conclusion sur les imports déduite de ces sources : aucune validation spécifique à l'import n'est nécessaire. Aucun lancement d'Odoo, test dynamique, installation, mise à jour ou accès client n'a été effectué.

## Choix et limites
Conserver le contrôle existant. Ajouter une automatisation Studio ou un second contrôle custom ferait doublon et créerait de la maintenance à la migration. Aucun paramètre supplémentaire n'est requis dans les sources fournies. La série suivante n'a pas été examinée : aucun delta de développement n'est proposé.

La présence de la déclaration dans le code ne garantit pas que la version correspondante du module ou la contrainte soit installée sur une base client. La présence de données anciennes négatives n'est pas connue. Aucune reprise de données ni correction d'installation n'est prescrite sans constat.

D-17 reste acquise : un prix nul est permis pour les lignes gratuites, même confirmées. La quantité ne doit pas être confondue avec le prix. SYN-11 reste résolu : aucun changement de libellé de bouton. Aucun changement de droits ou d'interface. Aucun blocage métier ni arbitrage humain nécessaire pour conclure cette analyse.

## Critères pour une vérification ultérieure sur copie locale
Ces critères viennent de la demande et des décisions initiales ; ils ne sont pas des tests exécutés.

| Référence | Situation | Résultat attendu |
|---|---|---|
| Demande : négatif interdit | Créer une ligne de quantité -1 ; modifier une ligne existante vers -1 | Enregistrement refusé, aucune quantité négative persistée |
| Demande : imports inclus | Importer une nouvelle ligne à -1 ; mettre à jour une ligne vers -1 par import | Erreur de validation, aucune quantité négative persistée |
| Demande : zéro autorisé | Créer, modifier et importer une ligne brouillon à quantité 0 | Ligne autorisée par le contrôle de quantité |
| Borne de la règle | Créer ou importer une ligne à quantité 1 | Ligne autorisée par le contrôle de quantité |
| D-17 | Ligne gratuite avec quantité 1 et prix 0, puis confirmation | Prix nul conservé et confirmation permise |
| SYN-11 | Consulter le bouton existant | Libellé conservé |

Suite recommandée : le responsable technique vérifiera la version installée et la présence de la contrainte, puis ces cas sur une copie locale si une assurance sur le déploiement client est requise. Si une anomalie apparaît, ouvrir un diagnostic ciblé avant de décider d'un correctif. Ne pas ouvrir de développement en double sur la seule demande actuelle.
