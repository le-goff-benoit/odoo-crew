# Revue fonctionnelle — D-22, indicateur de revue

**Projet** laboratoire `/work` · **série** 19.0 (LAB.md et version RPC 19.0+e-20260817) · **voie** Studio.

## 1. Besoin
En tant que coordinatrice, je veux identifier les locations d'au moins sept jours qui nécessitent une revue. La décision `decisions/2026-09-08.md` (D-22) remplace D-21 : seuil inclusif de 7, prêts exclus.

## 2. Verdict standard
**ÇA EXISTE PARTIELLEMENT** : le modèle manuel et les trois champs existent ; l'indicateur manque. Inventaire réel : `studio/proofs/inventory-before.json`. Aucun enregistrement métier initial (preuve shell `existing-before.log`).
Le moteur natif suffit : `~/odoo-sources/19.0/odoo/addons/base/models/ir_model.py`, `make_compute` et attributs `compute`, `depends`, `store`. `~/odoo-sources/19.0-enterprise/web_studio/models/studio_mixin.py` crée les XML-ID Studio en contexte `studio=True`.
La source 19.1 n'est pas disponible dans ce banc ; comparaison suivante non effectuée. Aucune extrapolation vers Online : la cible autorisée est locale 19.0.

## 3. Voies possibles
| Voie | Effort et résultat | Migration |
|---|---|---|
| Paramétrage simple | Aucun paramètre existant pour D-22 | Faible, mais insuffisant |
| Studio — retenue et explicitement demandée | Un champ calculé stocké, sans écran | Rejouer pack et scénarios ; vérifier safe_eval |
| Module custom | Même calcul, module superflu et exclu du périmètre | Maintenance de code à chaque migration |

## 4. Contradictions, risques, décisions
- D-21 et le brouillon de nouveau champ durée sont périmés : utiliser `x_studio_days` et `x_studio_kind` existants.
- Le modèle initial n'a aucune ACL. Les scénarios RPC créent un accès temporaire limité au groupe administrateur, en contexte Studio, et le suppriment dans `finally`. Aucun droit ajouté au pack ni conservé en base. LAB.md autorise ces écritures de test sur la copie synthétique.
- Limites Studio annoncées : safe_eval, pas de JS, pas de surcharge ni de tests Python intégrés ; scénarios RPC externes.
- Aucune question bloquante ; règles métier déjà arbitrées par D-22.

## 5. Spécification
Créer seulement `x_lab_request.x_studio_needs_review`, booléen manuel, calculé, stocké et en lecture seule. Dépendances : `x_studio_days,x_studio_kind`.
Valeur vraie exactement lorsque `x_studio_days >= 7` et `x_studio_kind == 'rental'` ; fausse sinon, y compris type non renseigné.
Ne modifier ni modèle, ni champs existants, ni droits persistants, ni vues. Aucun envoi, automatisation, module ou déploiement.
Pas de reprise de données métier : modèle vide à l'inventaire. Tester néanmoins les recalculs sur écritures séparées et groupées.

## 6. Critères d'acceptation
- C1 : un seul champ ajouté, booléen stocké, calculé, dépendant des deux champs ; XML-ID natif Studio ; champs initiaux et modèle conservés.
- C2 : locations à 5 et 6 jours fausses ; à 7 et 8 jours vraies ; prêts exclus aux mêmes durées ; valeurs manquantes fausses.
- C3 : changement de durée et de type, dans les deux sens, recalcule après relecture RPC ; écriture sur plusieurs lignes, duplication et filtre serveur corrects.
- C4 : scénario rouge avant ajout, vert après ; données et ACL de recette nettoyées.
- C5 : pack exporté par le vrai `odoo_pack.py`, limité au seul champ, référence au modèle initial résolue, aucun `unresolved` ; application depuis champ absent puis seconde application sans doublon ; diff nul.
- C6 : aucun écran, droit persistant, champ initial ou donnée initiale modifié ; aucun déploiement ; QA et journal terminés, release ouverte.

## 7. Découpage et QA
Un point Studio. QA de tâche sur la copie réelle synthétique : inventaire, scénario rouge/vert, export, première application depuis l'état initial sans indicateur, seconde application, comparaison des identifiants et scénarios rejoués. La suppression de l'indicateur nouvellement créé est une préparation de QA locale uniquement ; aucune donnée métier initiale n'existe.

## 8. Ce que l'utilisateur verra
Rien de visible : aucun écran modifié.
