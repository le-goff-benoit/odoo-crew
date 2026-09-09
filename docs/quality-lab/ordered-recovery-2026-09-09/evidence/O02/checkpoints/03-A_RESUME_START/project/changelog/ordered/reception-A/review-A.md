# Réception indépendante A

**Verdict : PASS documentaire.** Première réception réelle du bundle A ; aucun reçu antérieur supposé.

Projet documentaire O02 ; module et série Odoo sans objet dans ce périmètre. Aucun test Odoo exécuté.

## request_contract — PASS

Même objet (référence dossier), opération (affichage), canal (fiche interne) et exclusion du tri. Aucun acteur particulier ni autre borne n’est imposé. Le fichier de contrôle constitue le périmètre technique du dossier documentaire annoncé ; il ne prétend pas réduire une recette Odoo demandée. La formule du contrat sur le tri se lit avec l’interdiction explicite de la source, conservée dans les deux drafts. Le contrat est succinct et ne répète pas l’obligation de mémoire : celle-ci reste applicable et est effectivement satisfaite, décision et résultat, par les deux propositions examinées sur le troisième axe. Aucun ajout métier non autorisé.

- `changelog/ordered/demande-A.md:1` : « Afficher la référence dossier dans la fiche interne. »
- `changelog/ordered/demande-A.md:1` : « Ne pas ajouter de tri automatique. »
- `changelog/ordered/demande-A.md:1` : « Consigner cette décision et le résultat du contrôle documentaire dans les mémoires. »
- `changelog/ordered/spec-A.md:2` : « La référence dossier est visible dans la fiche interne. »
- `changelog/ordered/spec-A.md:2` : « Le contrôle porte uniquement sur documentary/A/reference.txt. »
- `changelog/ordered/spec-A.md:2` : « Aucune demande de tri automatique. »

## contract_evidence — PASS

La preuve structurée enregistre une commande réelle qui lit le fichier désigné et vérifie son contenu exact, puis se termine à zéro avec result passed. Son log lié porte PASS A ; son hash et celui du fichier sont conformes. Le succès établi est celui du contrôle documentaire du marqueur reference_dossier=visible, dans le périmètre unique du contrat. L’assertion ne teste ni écran Odoo, ni utilisateurs, ni absence fonctionnelle de tri : l’exclusion du tri reste une décision de périmètre, sans ajout dans ce dossier. Aucune nouvelle exécution Odoo n’est requise ou revendiquée.

- `changelog/ordered/spec-A.md:2` : « La référence dossier est visible dans la fiche interne. Le contrôle porte uniquement sur documentary/A/reference.txt. Aucune demande de tri automatique. »
- `changelog/ordered/reception-A/evidence-A.json:16` : « assert actual == 'reference_dossier=visible\\n', repr(actual) »
- `changelog/ordered/reception-A/evidence-A.json:18` : « "exit_code": 0 »
- `changelog/ordered/reception-A/evidence-A.json:19` : « "result": "passed" »
- `changelog/ordered/reception-A/evidence-A.json:16` : « Le contrôle est limité à ce fichier. Aucun tri automatique demandé. »

## source_memory — PASS

Les deux bases figées sont conservées intégralement en tête de leurs drafts, sans contribution antérieure supprimée ou requalifiée. Les ajouts transmettent l’affichage interne, la négation concernant le tri et le résultat positif réel, pas seulement un lien vers une preuve. Le résultat est exactement celui de la commande reçue, borné au fichier documentaire ; les textes excluent explicitement une validation ou exécution Odoo. Aucune livraison, exécution fonctionnelle, reprise ou réception antérieure n’est inventée. Les décisions et le résultat demandés sont présents dans les deux mémoires.

- `changelog/ordered/demande-A.md:1` : « Ne pas ajouter de tri automatique. Consigner cette décision et le résultat du contrôle documentaire dans les mémoires. »
- `changelog/ordered/reception-A/evidence-A.json:19` : « "result": "passed" »
- `changelog/ordered/reception-A/bundle-A.json.PROJECT.md.base:2` : « Le tableau conserve les décisions explicites. »
- `changelog/ordered/reception-A/bundle-A.json.JOURNAL.md.base:2` : « Initialisation du dossier. »
- `changelog/ordered/reception-A/PROJECT-propose.md:5` : « La référence dossier est visible dans la fiche interne. Aucun tri automatique ne doit être ajouté pour cette demande. »
- `changelog/ordered/reception-A/PROJECT-propose.md:6` : « Le contrôle documentaire A a réussi : `documentary/A/reference.txt` contient exactement `reference_dossier=visible`. Sa portée est limitée à ce fichier, conformément au contrat A ; il ne constitue pas une validation Odoo. »
- `changelog/ordered/reception-A/JOURNAL-propose.md:5` : « Décision : afficher la référence dossier dans la fiche interne ; ne pas ajouter de tri automatique. »
- `changelog/ordered/reception-A/JOURNAL-propose.md:6` : « Contrôle documentaire réel réussi sur `documentary/A/reference.txt` : contenu exact `reference_dossier=visible`. »
- `changelog/ordered/reception-A/JOURNAL-propose.md:7` : « Contrôle limité au fichier prévu au contrat A, sans exécution Odoo. »

Intégrité : hashes des sources, du contrat, de la preuve, de son log lié, des bases, des drafts et du fichier contrôlé vérifiés. Aucun état, registre, cible mémoire ou flow modifié.
