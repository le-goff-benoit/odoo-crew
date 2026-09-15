# Revue fonctionnelle — préparation N-17

Projet Atelier Nacre · Odoo 19.0 (.odoo-agents/config) · module lab_preparation.

## 1. Besoin et décision
En tant qu'utilisateur, je veux préparer le restant automatiquement tout en conservant mes saisies explicites et en repartant d'une demande vierge lors d'une duplication ou d'un reliquat.
Source intégrale : demande.md et decisions/current.md, décision N-17 confirmée. Aucun arbitrage supplémentaire.

## 2. Standard et voies
À DÉVELOPPER dans le module existant : lab.preparation est un modèle synthétique distinct de stock.picking. Recherche du nom dans les sources 19.0 : aucune implémentation standard. L'ORM de odoo/orm/models.py, copy/copy_data, et les champs copy=False de addons/project/models/project_task.py fournissent le mécanisme de duplication, pas les règles N-17.
Série suivante absente du banc (seules 19.0 et 19.0-enterprise disponibles) : comparaison non exécutée.
Configuration : aucun paramètre ne corrige les méthodes fautives ; coût de migration faible mais besoin non couvert.
Studio : ne permet pas la surcharge de copy et des méthodes existantes ; automatisation concurrente fragile à migrer.
Module : correction locale de la logique existante, tests conservés lors des migrations ; voie retenue.

## 3. Cohorte et risques
Inventaire réel lab_client : ID 1 LEGACY_AUTO draft 10 commandés / 3 livrés / 999 préparés / automatique ; ID 2 LEGACY_MANUAL_ZERO draft 10/0/0 manuel ; ID 3 LEGACY_MANUAL_PARTIAL draft 10/3/2 manuel ; ID 4 LEGACY_DONE done 10/4/88 automatique.
Le zéro manuel réfute l'assimilation de zéro à absence de saisie. Les done ne sont pas recalculables. Aucun champ Studio, cron configuré ou action serveur sur ce modèle (preuves/inventaire.log).
Risque élevé : reprise de données existantes, strictement copie synthétique autorisée. Les droits et le schéma métier restent inchangés. Pas de modèle multi-société dans ce laboratoire.

## 4. Spécification et frontières
Appliquer intégralement N-17. action_set_manual(quantity) conserve la signature existante et écrit manual=True même pour zéro. Cron limité aux drafts automatiques : max(commandé-livré, 0). Duplication : ordered_qty conservé, delivered_qty/prepared_qty à zéro, manual=False, state=draft. Reliquat singleton positif : nouveau draft avec quantité restante, champs remis à zéro, parent source ; source done avec préparation conservée. Reste nul ou négatif : recordset vide, aucune création ni modification de source. Aucun comportement supplémentaire (pas de contrainte de quantité, de blocage sur done, de planification cron ni de changement de droits).
Reprise : exécuter le cron corrigé sur la copie existante après update ; vérifier tous les champs métier, le périmètre et un second passage. Idempotence requise sur les valeurs ; le contrôle vérifiera aussi write_date des lignes protégées.
Ce que l'utilisateur verra : valeurs corrigées et nouvelles demandes réinitialisées ; aucune vue fournie par ce module.

## 5. Critères d'acceptation
- [ ] **A1** — Le cron prépare seulement les drafts automatiques au restant positif ou zéro (livraison égale/supérieure incluse), conserve les drafts manuels et tous les done, et son rejeu conserve les valeurs.
- [ ] **A2** — action_set_manual enregistre la quantité et manual=True, y compris zéro ; un cron ultérieur conserve ces saisies.
- [ ] **A3** — copy() conserve ordered_qty et réinitialise delivered_qty=0, prepared_qty=0, manual=False, state=draft ; la source est inchangée et le cron prépare la nouvelle demande complète, y compris une source terminée/manuelle.
- [ ] **A4** — action_remainder singleton positif crée un draft au restant exact, delivered_qty=0, prepared_qty=0, manual=False, parent_id=source ; la source passe done sans écraser prepared_qty. Le cron suivant prépare le reliquat et laisse la source intacte.
- [ ] **A5** — action_remainder retourne un recordset vide sans création lorsque le reste est nul ou négatif ; une sélection multiple est rejetée sans modification.
- [ ] **A6** — Sur lab_client déjà installé, après update, la reprise transforme ID 1 de 999 à 7 et préserve intégralement les lignes ID 2 (zéro manuel), ID 3 (manuel 2) et ID 4 (done 88). Un rejeu ne change pas les résultats et aucune ligne n'est créée.
- [ ] **A7** — Les tests ciblés sont capturés rouges avant correction puis verts après correction ; lint du diff, installation QA et update de la copie sont vérifiés. La release reste ouverte et aucun déploiement n'est effectué.

## 6. Plan de preuve fixé avant tests
Commande rouge puis verte : python3 /home/blegoff/.odoo19-agents/scripts/odoo_evidence.py run --project /work --scope lab_preparation --module lab_preparation --environment lab-qa-19.0 --output changelog/2026-09-15_01_repair/preuves/tests-rouge.json (puis tests-vert.json) -- /bridge/labctl qa lab_preparation --quick --tags /lab_preparation:TestPreparation.
Portée : classe dédiée TransactionCase, attentes numériques issues de N-17, jeux synthétiques isolés, inclut petites fractions et cohorte mixte. Preuves distinctes et logs intégraux. Après vert : /bridge/labctl lint lab_preparation ; /bridge/labctl update ; /bridge/labctl shell .../reprise.py via odoo_evidence.py. Relecture croisée demande/décision/contrat/code/preuves en fin de tâche, non indépendante selon LAB.md. QA renforcée immédiate sur la copie ; recette complète différée à la clôture.

## 7. Estimation
Analyse déjà commencée : prévision initiale absente. Suite : développement 5–10–18 min ; QA/copie et réception 5–9–18 min ; orchestration/mémoire 2–4–8 min. Jugement initial, confiance faible, pont opérationnel et absence de reprise supposés. Pas de trace native de session accessible : durée/jetons par rôle indisponibles, aucune mesure inventée.
