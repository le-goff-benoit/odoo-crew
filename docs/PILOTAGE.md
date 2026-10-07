# Pilotage et contrats observables

`odoo_pilotage.py` expose `capabilities`, `readiness`, `delivery`,
`business-results`. Toutes les références ont `path` relatif au projet et
`sha256` ; les fichiers restent immuables. Le lecteur Python utilise
`read_session()` pour partager les validations pendant une seule requête.
Il n'écrit aucun workflow et ne modifie pas les fonctions internes du moteur.

## Moyens de recette

`readiness --file readiness.json` lit un objet `schema: 1`, `series`,
`environment`, `required: ["browser", "pdf", "filestore", "data"]`,
`checks: [{id, status: "available", evidence: {path, sha256}}]`.
Chaque observation JSON contient `series`, `environment`, `capability` et
`available: true`. Un moyen requis absent produit un verdict non prêt.
Choisir uniquement les moyens nécessaires ; ce contrat ne les installe pas.

## Résultats métier

À côté de `spec.md`, `spec.business.json` contient `schema: 1`, `basis`,
`reviewed_by`, `cases: [{id, population: [...], expected: {total: "120.00"}}]`.
L'oracle est fixé avant implémentation et relu indépendamment. L'observation
JSON contient les mêmes `cases`, `population`, et `observed` à la place
`expected`. `business_observation` dans la couverture pointe vers ce fichier.
Une différence de valeur ou de population interdit un verdict complet. Les
valeurs décimales sont des chaînes pour éviter un arrondi implicite.
Le validateur prouve la comparaison, pas l'indépendance intellectuelle de l'oracle.

## Publication et déploiement

`delivery <projet> --release R1 --file livraison.json` exige `status`, `target`,
`tasks`, `evidence`. Une publication simple vaut `published`. Avec réserves,
`published_with_reservations` exige une `decision` sourcée et `reservations`
contenant `missing_control`, `next_action`, `owner`. La clôture reste inchangée.

`deployed_verified` exige une contribution de type `deployment` acceptée et
actuelle. Ses `tasks` doivent correspondre exactement, sa cible et ses modules
au contrat vérifié. Une publication GitHub seule ne prouve pas un déploiement.
Les réserves et l'historique sont conservés dans `delivery-status.json`.

## Mémoire et temps

Les découvertes acceptées et sourcées sont projetées dans
`.odoo-agents/LEARNINGS.json`. Elles conservent `scope`, `effect`, `exceptions`
et relecture. Une découverte proposée n'est pas promue. Remplacer explicitement
un acquis devenu faux ; `prepare` ne transmet que les sources encore actuelles.

`odoo_effort.py track` suit une session dédiée après contrôle des estimations.
Les chemins des journaux restent dans le cache local privé, hors Git.
Le journal natif est l'autorité pour les périodes exécutées : la veille, la nuit
et la déconnexion réseau ne créent aucun segment de durée à elles seules.
`odoo_work.py prepare` réconcilie et relance la collecte après arrêt du poste.
Pour une session multi-tâches, utiliser des fenêtres bornées non chevauchantes.
Le réalisé connu reste un sous-total si des durées manquent.
