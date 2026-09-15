# Revue fonctionnelle — N-17 préparation

Projet Atelier Nacre, série 19.0 (.odoo-agents/config), module lab_preparation.

## 1. Ce que je comprends
En tant qu'utilisateur interne, je veux préparer le solde automatique sans perdre mes saisies explicites, et distinguer nouvelle demande et reliquat.
Le code courant écrase toutes les quantités au cron, traite zéro comme automatique et copie les valeurs historiques dans le reliquat.

## 2. Verdict standard
À DÉVELOPPER dans le module existant. N-17 exclut stock.picking.
L'ORM 19.0 fournit copy/copy_data (odoo/orm/models.py:5404,5528), mais copie par défaut les champs simples : les règles N-17 restent propres à lab.preparation. Aucun lab.preparation trouvé dans les addons standard 19.0. La série suivante 19.1 n'est pas disponible dans ce banc ; comparaison non exécutée.
Copie lab_client inventoriée : aucun champ Studio, action serveur ou ir.cron sur ce modèle (preuves/inventory.log). Il existe une méthode cron à corriger ; aucune planification supplémentaire demandée.

## 3. Voies possibles
- Configuration : ne corrige pas les méthodes existantes ; faible maintenance mais besoin non couvert.
- Studio : ne surcharge pas copy et ne livre pas ces tests Python ; doublerait le module, maintenance inutile.
- Module : correctif local minimal, tests ORM et reprise explicite ; revalidation de ces règles à chaque migration. Voie retenue.

## 4. Cohorte et risques
Données synthétiques existantes, acteur shell Odoo de lab_client :
- id 1 LEGACY_AUTO : draft automatique, commandé 10, livré 3, préparé 999 ; attendu 7.
- id 2 LEGACY_MANUAL_ZERO : draft manuel préparé 0 ; contre-exemple à « zéro = non saisi ».
- id 3 LEGACY_MANUAL_PARTIAL : draft manuel préparé 2 malgré un solde de 7 ; garder 2.
- id 4 LEGACY_DONE : done automatique préparé 88 ; garder 88 malgré un solde de 6.
QA renforcée immédiate car reprise des données existantes. Aucun changement de droits, schéma ou dépendance. Modèle sans société ; pas de règle multi-société inventée.

## 5. Questions bloquantes
Aucune : décisions/current.md contient la décision confirmée N-17.

## 6. Hypothèses et choix techniques
Idempotence prouvée sur les valeurs et, pour le cron sans différence, absence de write. Pas d'arrondi ajouté.
Aucun planning cron n'est créé. La méthode est exercée directement, puis par un ir.cron temporaire dans un test transactionnel.

## 7. Spécification
N-17 est la source exclusive des valeurs attendues. Champs existants conservés.
Cron : seulement draft et manual=False, prepared_qty=max(ordered_qty-delivered_qty,0).
Saisie : action_set_manual(quantity) conserve la signature existante, écrit prepared_qty=quantity et manual=True, zéro inclus.
Duplication : nouvelle demande conservant ordered_qty ; delivered_qty=prepared_qty=0, manual=False, state=draft.
Reliquat singleton : si ordered_qty-delivered_qty>0, nouveau draft pour ce reste, delivered_qty=prepared_qty=0, manual=False, parent_id=source ; source done, prepared_qty conservée. Sinon recordset vide et aucune création ; source inchangée.
Reprise : invoquer la méthode corrigée sur la copie puis relire et rejouer. Conserver un état avant/après pour tous les enregistrements.
Hors périmètre : déploiement, recette complète, clôture, vues, nouvelle politique de saisie ou de droits, planification permanente.

## 8. Critères d'acceptation
- [ ] **A1** — N-17 : le cron calcule le solde positif ou zéro seulement pour les drafts automatiques ; conserve intégralement les drafts manuels (zéro inclus) et les done ; rejeu idempotent.
- [ ] **A2** — N-17 : action_set_manual conserve exactement une quantité explicite, dont zéro, avec manual=True ; cron ultérieur conserve cette saisie sur une sélection mixte.
- [ ] **A3** — N-17 : copy() conserve ordered_qty et réinitialise delivered_qty=0, prepared_qty=0, manual=False, state=draft ; un cron ultérieur prépare toute cette nouvelle demande sans altérer la source done.
- [ ] **A4** — N-17 : action_remainder singleton avec reste positif crée un seul draft pour ce reste, delivered_qty=prepared_qty=0, manual=False, parent_id=source ; source done conserve prepared_qty ; cron puis rejeu préparent le reliquat et préservent la source.
- [ ] **A5** — N-17 : sans reste positif (égalité ou dépassement), action_remainder retourne un recordset vide sans création ; l'appel non singleton échoue avant toute mutation.
- [ ] **A6** — Demande et N-17 : reprise des drafts automatiques existants de lab_client uniquement ; id 1 passe de 999 à 7, ids 2/3/4 restent respectivement à 0/2/88 avec tous leurs champs conservés ; rejeu stable et relecture persistée.
- [ ] **A7** — Demande : tests rouges sur code initial puis verts sur correctif, couvrant zéro manuel, duplication, reliquat puis cron ; installation/tests ciblés, lint du diff et update sur copie existante réussis.

## 9. Découpage et estimation
Analyse puis tests rouges, correctif, QA ciblée et update, reprise contrôlée, réception et mémoire.
Prévision du travail restant : développement 4–8–14 min, QA 4–7–12 min, consolidation 2–4–7 min ; jugement initial sans historique comparable, confiance faible. Analyse déjà commencée sans prévision initiale. Trace native de session non disponible : durées/jetons/coût mesurés indisponibles, non assimilés à zéro.

## 10. Ce que l'utilisateur verra
Aucun écran ajouté ; les méthodes de préparation, duplication et reliquat respectent désormais N-17.
