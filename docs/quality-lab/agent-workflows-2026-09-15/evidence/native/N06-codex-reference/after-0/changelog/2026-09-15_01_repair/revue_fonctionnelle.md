# Revue fonctionnelle — B-42

Projet synthétique Registre Boréal · Odoo 19.0 (config) · module `lab_register`.
Sources : demande originale `demande.md`, arbitrage `decisions/current.md`, autorisation locale `LAB.md`.

## Compréhension et verdict
L'utilisateur interne doit pouvoir réparer les brouillons sélectionnés de sa société active sans altérer les références émises ni les autres sociétés.
**À DÉVELOPPER** : la méthode custom dans `lab_register/models/business.py` recherche globalement sous sudo, numérote par 10 et inclut les lignes annulées. Aucun modèle `lab.register` dans les sources standard 19.0 disponibles ; les actions de `addons/repair/models/repair.py` concernent les réparations de stock, sans lien avec ce registre. La série suivante n'est pas montée dans ce banc : comparaison non vérifiable, sans incidence sur ce correctif custom.
L'inventaire de la copie (`proofs/inventory.log`) ne trouve ni champ manuel ni action serveur du registre. Configuration : aucun paramètre ne corrige cette méthode. Studio : ne surcharge pas la méthode et ajoute une maintenance inutile. Module existant : correction réduite avec tests, à conserver lors des migrations.

## Cohorte, décisions et risques
Copie `lab_client`, société initiale ID 1. Brouillons 1 (ancien, 20/999, lignes 20 + 495 annulé) et 2 (10/123, lignes 15 + 495 annulé). Contre-exemples : émis 3 (17/555, ISSUED/005, montant volontairement distinct des lignes), société 2 brouillon 4 (80/666). Utilisateurs ordinaires 5 multi-société et 6 limité à 1.
B-42 arbitre explicitement 100/200 et interdit toute renumérotation/recalcul des émis. L'ancien `qa.md` vérifie seulement une création vide : son PASS historique ne réceptionne aucune exigence actuelle. Aucune question bloquante.

## Spécification
Filtrer **self**, état draft et `company_id == env.company`, trier date_document puis id, numéroter 100, 200… et sommer quantity × price uniquement sur les lignes non annulées. Une sélection mixte accessible est admise ; ses éléments hors périmètre sont ignorés. La sélection vide ne modifie rien. Préserver les autres champs et toutes les lignes.
Aucun sudo, aucune modification des ACL/règles : les accès ORM restent applicables. Un ID interdit ne donne pas accès à une autre société ; AccessError attendu sous utilisateur limité. Contrôler le droit d'écriture sur les brouillons avant toute mutation, y compris si leurs valeurs sont déjà correctes.
Reprise locale explicite des deux brouillons existants de la société initiale 1, avec photographie préalable, mise à jour du module puis contrôle après commit et deuxième passage. Aucun hook global qui reprendrait implicitement une autre base. Éviter les write si valeurs identiques (choix technique pour un rejeu sans effet d'écriture), sans arrondi ajouté.
Hors périmètre : production, déploiement, changement de droits, schéma, interface, clôture et recette complète de release. Version inchangée jusqu'à clôture.

## Critères d'acceptation
- [ ] **A1** — Sous utilisateur interne multi-société, une sélection mixte ne répare que les draft de self dans env.company ; un brouillon non sélectionné et les autres sociétés restent strictement inchangés, même si accessibles. Changer de société active inverse le périmètre ; sélection vide sans effet.
- [ ] **A2** — Tri date_document puis id, séquences 100/200 et suivantes ; snapshot_total exclut les lignes annulées, vaut zéro sans ligne active, et conserve la précision non arrondie.
- [ ] **A3** — Les issued sélectionnés conservent strictement state, sequence, snapshot_total, reference ; aucune ligne ni champ hors correction ne change.
- [ ] **A4** — ACL/règles inchangées ; utilisateur ordinaire non sudo autorisé testé, utilisateur limité refusé sur une société interdite, absence de droit d'écriture refusée sans mutation.
- [ ] **A5** — Test de régression rouge conservé sur le code initial puis mêmes tests verts sur code corrigé ; lint du diff, installation QA et update sur copie déjà installée exécutés.
- [ ] **A6** — Reprise persistée uniquement des brouillons historiques 1 et 2 : 100/20 et 200/15 ; émis 3 et société 2 ID 4 intacts. Deuxième passage idempotent, valeurs et write_date stables, aucune écriture ORM au rejeu dans le test instrumenté.
- [ ] **A7** — Ancienne QA relue avec portée invalidée pour cette tâche ; revue, QA courante et journal publiés, release laissée ouverte, limites explicites.

## Découpage et QA
Analyse puis test rouge, correctif, QA renforcée (droits et données existantes), update et reprise locale, réception et journal. Une seule conversation conformément au LAB : relecture non indépendante. Prévision du travail restant : développement 8–12–20 min, QA 6–10–18 min, consolidation 3–5–8 min ; jugement initial sans historique comparable, confiance faible. Analyse déjà engagée sans estimation initiale. Trace native absente du banc : temps/jetons mesurés indisponibles, pas zéro.

## Ce que l'utilisateur verra
Résultat correct de la méthode existante ; aucun écran ajouté ou modifié.
