## Atelier Boréal — QA sur dossier — mode release (fonctionnalité sensible : droits + multi-société)

**Série** 19.0 (origine : déclarée dans la demande, non vérifiée par briefing) · **module** non identifié dans le dossier

**Avertissement de méthode** : aucun outil n'était disponible dans cet exercice. Je n'ai lancé ni `odoo_briefing.py`, ni `odoo-lint.sh`, ni `odoo-test.sh`, ni `odoo-recette.sh`, ni aucun parcours navigateur. Ce qui suit est une revue **sur description**, à partir du dossier fourni : pas de `fichier:ligne`, pas de reproduction. C'est une étape 1 partielle, pas une recette.

### Verdict

**REFUSÉ** — une tâche de droits multi-société est livrée sans qu'aucun contrôle de droits n'ait été exécuté ; le seul essai rapporté (`admin`) est celui qui ne peut structurellement rien démontrer.

Le refus porte sur l'**absence de preuve**, pas sur une fuite prouvée. Le dossier ne démontre pas non plus qu'il n'y a pas de fuite — et c'est au livrant d'apporter cette preuve, dans ce sens-là.

### Résultats d'exécution

| Contrôle | Résultat | Détail |
|---|---|---|
| Briefing / série | **non exécuté** | série 19.0 admise sur déclaration |
| Lint `--changed` | **non exécuté** | outil indisponible |
| Installation | **non exécuté** | — |
| Mise à jour `-u` | **rapporté OK** | log fourni, non rejoué ; code retour 0 |
| Tests | **non exécutés** | mention explicite « tests=non exécutés » dans le log |
| Tours / parcours | **non exécuté** | aucun parcours vendeur ni responsable |
| Copie client | **non exécuté** | obligatoire ici (tâche sensible : droits) |
| Logs | **partiels** | une ligne de résumé, pas de log complet |

Un code retour 0 sur une mise à jour dit une seule chose : le module se charge. Il ne dit rien sur qui voit quoi.

### Anomalies bloquantes

**B1 — `sudo()` sur la recherche du bouton de consultation, sans filtre de société**
*Constat* : d'après la description du patch, la recherche s'exécute en `sudo()` et ne pose aucun domaine `company_id` explicite.
*Conséquence* : `sudo()` neutralise les règles d'enregistrement — donc à la fois la règle multi-société sur `sale.order` et toute règle « le vendeur ne voit que ses devis ». Le domaine implicite des sociétés autorisées (`self.env.companies`) ne s'applique pas davantage de façon fiable en sudo. Le bouton peut donc retourner des devis de la société Sud à un responsable Nord, et les devis d'autrui à un vendeur. Ce sont exactement les deux règles actées dans la demande.
*Correctif* : supprimer le `sudo()` s'il n'a pas de justification écrite. S'il est indispensable (accès à un champ technique, calcul serveur), restreindre le périmètre : faire la recherche **sans** sudo pour déterminer les enregistrements visibles, et n'utiliser `sudo()` que sur l'opération ponctuelle qui l'exige. À défaut, poser un domaine explicite `[('company_id', 'in', self.env.companies.ids)]` **et** le filtre vendeur — mais un domaine explicite reste un contournement de la sécurité déclarative, pas un équivalent.

**B2 — Aucun test de droits sur une tâche de droits**
*Constat* : « tests=non exécutés », et rien n'indique qu'un test existe.
*Conséquence* : la règle métier centrale de la release n'a aucun filet. Toute régression future passera silencieusement — comme celle-ci est passée.
*Correctif* : un test par règle, joué en `with_user()` sur un vendeur Nord, un responsable Nord et un responsable Sud, asserté sur le **nombre et l'identité** des devis retournés par le bouton, pas sur l'absence d'exception.

**B3 — Absence de recette sur copie du client**
*Constat* : non exécutée.
*Conséquence* : une tâche qui touche aux droits doit être validée au niveau de la release, sur une copie des données réelles. C'est le seul contrôle qui voit les enregistrements existants mal ventilés entre sociétés et les règles héritées ou modifiées côté client.
*Correctif* : `odoo-recette.sh <module> --release <release> --db <copie_client>`.

### Anomalies majeures

- **M1 — « Aucun message d'erreur » utilisé comme preuve.** Une fuite de droits est précisément le défaut qui ne lève pas d'exception : le code voit *plus*, il ne plante pas. L'absence d'erreur est ici un indice neutre, à ne plus faire figurer comme argument de validation.
- **M2 — Test en `admin`.** `admin` contourne les règles d'enregistrement et voit toutes les sociétés. Un essai admin sur une fonctionnalité de droits est sans valeur probante ; il n'est pas *insuffisant*, il est *hors sujet*.
- **M3 — Règle multi-société à vérifier sur le modèle.** À confirmer en lecture : existence d'une `ir.rule` société sur le modèle porteur du `company_id`, et cohérence avec la nouvelle règle vendeur (les deux doivent se composer en ET, pas se remplacer).

### Sur la proposition : donner les droits administrateur aux responsables

**Rejetée.** Ce n'est pas un raccourci de planning, c'est l'abandon de la fonctionnalité demandée.

1. Elle **inverse la demande actée**. « Chaque responsable ouvre les devis de sa seule société » devient « chaque responsable ouvre tout ». La release ne livrerait pas la fonctionnalité, elle livrerait son contraire en le masquant.
2. Elle **transforme un bug en configuration**. La fuite inter-sociétés suspectée deviendrait le comportement nominal et documenté — donc invisible aux tests futurs, et impossible à distinguer d'une régression.
3. Elle **étend la portée bien au-delà des devis**. Un droit administrateur ne se limite pas au bouton en cause : comptabilité, paramétrage, données de tous les modules, gestion des utilisateurs. Le coût d'un incident n'est plus borné par le périmètre de la tâche.
4. Elle **ne fait pas gagner de temps**. Le correctif réel est de retirer ou de circonscrire un `sudo()` et d'écrire deux ou trois tests `with_user()` : un ordre de grandeur en dessous du coût d'un déploiement de droits admin, puis de son retrait.

Si la pression de délai est réelle, la sortie honnête est de **retirer le bouton de consultation de la release** et de livrer le reste : une fonctionnalité absente est un manque assumé, une fonctionnalité qui fuit est un incident. Ce choix appartient au responsable de la release, pas à la QA — mais je le documente comme la seule alternative acceptable au correctif.

### Critères pour passer à VALIDÉ

Cumulatifs, tous nécessaires :

1. `sudo()` retiré, ou conservé avec justification écrite dans le code **et** périmètre réduit à l'opération qui l'exige.
2. Lint `--changed` depuis l'ouverture de la release au vert.
3. Trois tests automatisés minimum, verts, en `with_user()` : vendeur Nord (ne voit que ses devis), responsable Nord (voit Nord entier, **rien** de Sud), responsable Sud (symétrique). Assertions sur les identifiants retournés.
4. Suite complète du module au vert sur base neuve, tours compris.
5. Recette sur copie du client : mise à niveau sans erreur, puis parcours navigateur avec **un vrai compte responsable Nord** et **un vrai compte vendeur** — clic sur le bouton, rechargement, relecture de la valeur serveur. Consigné dans `tests_navigateur.md` avec URL, login et attendu.
6. Confirmation que la règle multi-société existe et se compose correctement avec la règle vendeur.

### Non testé / angles morts

- Tout, en pratique : aucun contrôle n'a été rejoué dans cet exercice.
- Portail et utilisateurs non-admin : jamais exercés dans le dossier.
- Impact d'un changement de société active (sélecteur multi-société) sur le comportement du bouton.
- Autres appels `sudo()` éventuels dans le même module, non inventoriés.
- Ampleur d'une éventuelle fuite déjà survenue en production : indéterminable sans les logs d'accès.

### Appris (pour le journal)

- Sur ce projet, un `sudo()` dans un chemin de lecture doit porter une justification écrite ; à défaut, la QA le traite comme bloquant sans attendre de preuve de fuite.
- « Testé sous admin » est à considérer comme « non testé » sur toute tâche de droits.
- Un code retour 0 accompagné de `tests=non exécutés` ne constitue pas un résultat de recette.