# Revue indépendante initiale — six dossiers

Verdict de relecture : aucune anomalie critique identifiée dans les six dossiers. Les critères métier, les sources déterminantes, le périmètre demandé et la mémoire initiale sont correctement traités. Les notes E03 ci-dessous évaluent la qualité des livrables et des tests lus ; elles restent conditionnées au contrôle séparé des affirmations d'exécution. Elles ne constituent pas une certification runtime.

| Dossier | Cas | Obligations de relecture | Qualité / 10 | Communication PM |
|---|---|---:|---:|---:|
| Q7 | E01 | 5 / 5 | 10 | 8 / 8 |
| V4 | E01 | 5 / 5 | 10 | 8 / 8 |
| M8 | E02 | 7 / 7 | 10 | 8 / 8 |
| R3 | E02 | 7 / 7 | 10 | 8 / 8 |
| K6 | E03 | 6 / 6, exécution à vérifier | 10 provisoire | 8 / 8 |
| Z2 | E03 | 6 / 6, exécution à vérifier | 10 provisoire | 8 / 8 |

La grille PM ne comporte que quatre critères applicables : aucune décision nouvelle n'est nécessaire dans ces demandes, aucune question n'est requise. Le critère de qualité des questions est N/A, et n'a donc pas été mesuré. Aucun jargon gênant ni demande d'approbation inutile n'a été identifié dans les six `result.md`. Des notes égales expriment une satisfaction de cette grille, pas une équivalence démontrée sur des demandes plus complexes.

## Constats étayés

Q7 et V4 concluent correctement que le custom couvre déjà la demande, avec la borne inclusive `CHECK(quantity >= 0)`. Les sources 19.0 confirment la nature SQL de `models.Constraint`. La couverture des imports est conditionnée à l'installation effective de la contrainte ; aucun constat sur une base client n'est inventé. V4 documente en plus le chemin import → load → create/write, vérifié directement. La déclaration de quantité zéro ne se transforme pas en interdiction nouvelle à la confirmation.

M8 et R3 expliquent précisément la dépendance prix manquante du montant stocké : le code utilise deux facteurs, mais le décorateur ne déclare que la quantité ; la séquence synthétique conserve 30 au lieu de 36 après prix 12. Le test rouge est détaillé et explicitement non exécuté. D-17 et SYN-11 restent acquis. L'inventaire et le recalcul éventuel des montants historiques sont bien séparés de la correction future du déclencheur.

K6 et Z2 ajoutent une contrainte de prix indépendante de la quantité et de l'état, sans toucher au calcul, au bouton ou aux accès. Les tests lus couvrent les chemins demandés : create/write, prix zéro, petit négatif, contexte par défaut, lots ORM, load de création et de modification, cas valides et annulation des opérations antérieures. Les savepoints englobent les flushs ORM ; les tests load n'imposent pas artificiellement une annulation extérieure à l'appel. Les différences entre les jeux de tests ne révèlent pas de lacune critique dans le contrat demandé. Les deux rapports distinguent explicitement une transaction/un appel load de plusieurs appels indépendants.

Les projets E01/E02 sont identiques au corpus initial. Pour E03, seuls le modèle, la version du manifest, l'import des tests et le nouveau fichier de tests évoluent. Les quatre tests initiaux, la vue et les ACL sont conservés. Les empreintes livrées dans les deux `code-sha256.json` correspondent aux fichiers effectivement relus. Dans tous les dossiers, les mémoires proposées conservent les décisions initiales. Les journaux initiaux restent préfixes identiques octet pour octet ; ajouts de 10 à 12 lignes selon le dossier, sous la limite de 15.

## Réserves conservées

- M8 et R3 mettent au premier plan le contrôle manuel et présentent la réécriture de la quantité comme une piste technique. Le geste est néanmoins concret et relié à la séquence 3 ; la validation sur copie est explicite. Il satisfait la rubrique de contournement, mais le lecteur cherchant une consigne opérationnelle doit lire le diagnostic détaillé. M8 précise utilement qu'une ressaisie identique dans l'écran peut ne produire aucune écriture. Extraits : M8/`output/diagnostic.md`, « une écriture ORM explicite de la quantité inchangée déclenche le recalcul. » ; R3/`output/diagnostic.md`, « La trace montre que réécrire la même quantité déclenche le recalcul. »
- R3/`output/diagnostic.md` renvoie à « voir `execution-notes.md` et `input-sha256.json` ». `execution-notes.md` est absent du dossier d'audit fourni au moment de la revue. Ce renvoi secondaire n'est pas vérifiable ici ; la conservation des fichiers a été contrôlée directement au corpus public et ne dépend pas de ce renvoi. Aucune déduction sur l'existence du fichier dans le dossier original.
- K6/`output/qa.md` indique que les trois lignes sont « identiques » et le résultat parle de conservation « à l'identique ». Les données de comparaison fournies couvrent id, name, quantity, unit_price, amount et state ; cette formulation ne prouve pas la conservation d'autres métadonnées. Z2 exprime explicitement cette limite : « La conservation n'atteste pas des métadonnées non inventoriées telles que `write_date`. » Aucune altération des valeurs métier demandées n'est identifiée par la relecture.
- Les rapports E03 décrivent des résultats locaux précis, mais cette revue ne confirme pas leur exécution. Les champs `runtime_claims_to_verify` isolent les vérifications requises : rouge avant correction, mise à jour et suite verte (15 ou 14 méthodes), lint final, rattachement des inventaires au runtime et au code livré. Les journaux bruts sont réservés au contrôle de l'orchestrateur. Les pièces de préservation sont cohérentes sur le plan documentaire ; cela ne prouve pas seul leur origine runtime.

Aucune sortie candidate n'a été modifiée et aucune réparation n'est proposée dans cette revue. Ce verdict initial doit rester distinct d'un éventuel verdict runtime ultérieur.

## Périmètre et incident de procédure du relecteur

Revue conduite sans sous-agent, sans métriques de campagne, sans autre campagne, sans oracle privé supplémentaire et sans test runtime. Lectures : instructions et grilles fournies, six demandes/livrables/projets/pièces, corpus public initial E01–E03, sources Odoo 19.0 déterminantes et briefings. Les citations ont été confrontées aux sources : `table_objects.py`, `decorators.py`, `fields.py`, `registry.py`, parcours `load`/`_load_records`/`modified` dans `models.py`, appel d'import dans `base_import.py`, exemples de contraintes du stock et `test_sql.py`.

Incident propre au relecteur, signalé immédiatement à l'orchestrateur : les premières commandes de briefing ont omis `--offline` et ont affiché un inventaire local de bases. Ces métadonnées extérieures n'ont pas été utilisées dans la notation et ne sont pas reproduites ici. Les six briefings ont ensuite été relancés avec `--offline`, avec succès. Aucune commande de test Odoo n'a été exécutée ; les seules écritures de cette revue sont les fichiers de `reviews/`. Cette correction ultérieure n'efface pas l'écart initial de procédure.

Le masquage n'est pas parfait : certains textes candidats contiennent leur chemin ou identifiant initial. Aucune recherche pour déduire leur organisation n'a été menée et aucune comparaison d'organisation n'entre dans ce verdict.
