# Réception indépendante — D-31 — 9 septembre 2026

**Module :** `lab_rental` · **Série :** 19.0, déclarée dans `.odoo-agents/config:1`, confirmée par `lab_rental/__manifest__.py:1` (19.0.1.1.0) · **Mode :** réception documentaire indépendante, sur archives.

**Verdict : REFUSÉ en l'état pour la validation globale « 8/8 ».** Les succès techniques documentés restent acquis. C08 n'est pas satisfait dans le contexte écrit ; la conservation après la création refusée d'A8 n'est pas directement attestée. La mémoire doit restituer ces limites. Aucun test Odoo, script historique ou flow n'a été relancé ; seul ce fichier est créé.

Dans les citations ci-dessous, **R/** désigne `changelog/2026-09-09_01_interdiction-des-durees-negatives-sur-le/` et **A/** désigne `.odoo-agents/flow-artifacts/contrainte-jours-positifs/`, dans le projet reçu. Les chemins historiques restent des références d'archives.

| Axe | Verdict | Motif |
|---|---|---|
| Demande ↔ contrat | Partiellement fidèle, à compléter | SQL, borne zéro, calcul et exclusions conservés ; postcondition d'A8 déplacée vers un autre rejet ; C08 ajoute une exigence de suite RPC. |
| Contrat → preuves | Validation globale refusée | C01–C07 étayés dans leur formulation ; C08 seulement partiel. La preuve RPC de création existe, mais sa postcondition de conservation manque. |
| Sources → mémoire | À rectifier | « VALIDÉ, 8/8 » et « A8 prouvé » dépassent les preuves ; plusieurs formulations doivent être bornées. |

## 1. Demande ↔ contrat

La demande originale (`demande.md:1`, reproduite dans `R/demande.md:5`) exige « interdire les jours négatifs par une contrainte SQL Odoo », « les jours nuls valides et le calcul du total existant », des tests de création et modification refusées avec conservation d'une location valide, la QA sur copie, le journal et une release ouverte. « Aucun écran ni droit à modifier. »

D-31, actée par Luc Roy (`decisions/2026-09-08.md:1`), précise `lab.rental.days >= 0`, « Zéro autorisé », « daily_rate et amount_total ne changent pas de règle (jours × tarif) » et « Aucune facturation ni mise en production. » L'objet est tout `lab.rental`, sans exemption de type ni d'acteur ; le responsable de locations introduit par `R/revue_fonctionnelle.md:6` n'est pas une restriction de la contrainte. La copie est synthétique, sans autorisation de production.

Ces obligations sont reprises dans `R/revue_fonctionnelle.md:11–21`, `:89–111` et C01–C07 (`:115–121`). Le choix de `models.Constraint` est technique, cohérent avec la série et le mécanisme SQL demandé. La mise à jour sur copie est une conséquence justifiée de la QA demandée. Les passages RPC supplémentaires pour `write` et zéro sont des choix de vérification, compatibles avec le besoin.

**A8 comporte deux éléments à conserver ensemble.** `decisions/2026-09-08.md:4` demande : « le rejet d’une création avec days=-1 doit être constaté via le vrai XML-RPC et retourner le message “Le nombre de jours doit être positif ou nul.” » puis « Vérifie la conservation des données après rejet. Le code sans appel RPC ne satisfait pas A8. » La revue reconnaît la conservation (`:19–21`), mais C03 (`:117`) ne teste que le Fault et la phrase ; C04/C07 (`:118`, `:121`) traitent la conservation après **modification**, opération distincte. Ajouter une postcondition propre au `create` rejeté est nécessaire pour conserver la portée originale.

**Message : précision technique justifiée, pas preuve d'une nouvelle décision client.** La revue annonce « contient exactement la phrase » (`:61`, `:71–72`, `:117`). Le noyau 19.0, `~/odoo-sources/19.0/odoo/service/model.py:213–214`, préfixe effectivement le message SQL avec `The operation cannot be completed: %s`. Le Fault archivé conserve intégralement la phrase française. D-31 ne prescrit pas explicitement une égalité du Fault complet avec le texte nu : ce préfixe seul n'est donc pas un motif de refus. La mémoire doit qualifier ce choix d'interprétation technique documentée, sans l'attribuer à un arbitrage supplémentaire de Luc Roy.

**C08 est une obligation supplémentaire écrite.** `R/revue_fonctionnelle.md:122` exige : « Étant donné la suite de tests du module, quand on exécute `/bridge/labctl qa lab_rental`, alors tous les tests passent, y compris les scénarios ci-dessus couverts par un vrai appel RPC (pas seulement des appels ORM internes). » La demande impose de vrais appels pour A8, mais ne demande pas expressément leur intégration dans cette suite. Cet ajout peut être clarifié ; tant qu'il demeure écrit, son contexte d'exécution ne peut être remplacé silencieusement par des appels indépendants.

## 2. Contrat → preuves

Contrôle local : les **16 chemins uniques** cités dans `R/coverage.json` existent et leurs SHA-256 concordent. L'empreinte de la revue vaut `1c21a476576bb9200de5f9921db78df1a351e6bb89870bba46ab1a744caff5e0`, identique à `R/qa.md:9`. Cette intégrité n'établit pas à elle seule la couverture métier. `R/qa.md:163` avertit justement : « Les statuts restent déclaratifs ».

| Contrôle / critère | Résultat de réception | Sources utiles |
|---|---|---|
| C01 : contrainte SQL 19.0 | Établi dans le code et la revue statique ; zéro inclus | `lab_rental/models/business.py:8–11`, `A/qa_high_static/fragment.md:13–28` |
| C02 : update de `lab_client` | Établi par le journal historique : module chargé, registre chargé | `A/qa_client/logs/update.log:17–25` |
| C03 : vrai RPC `create(days=-1)` et phrase | Établi : requête `create`, transport `xmlrpc`, `outcome=fault`, phrase exacte avec préfixe | `A/qa_client/rpc/01_create_negative.json:2–5`, `A/qa_client/logs/01_create_negative.log:1` |
| C04 et C07 : rejet de `write` et conservation | Établi pour id 3 : avant/après `days=5`, `daily_rate=20.0`, `amount_total=100.0` ; un résultat pour le nom contrôlé | `A/qa_client/rpc/05_write_negative.json:2–5`, journaux `04_read_base_before.log:1`, `05_write_negative.log:1`, `06_read_base_after.log:1` |
| C05 : zéro en création et modification | Établi : création rend `[2]`, écriture rend `true`, id 3 relu à zéro | Requêtes et journaux `A/qa_client/{rpc,logs}/02_create_zero.*`, `07_write_zero.*`, `08_read_zero_after.*` |
| C06 : formule conservée | Établi sur les cas archivés ORM et RPC ; code `days * daily_rate` | `lab_rental/models/business.py:19–22`, tests `:72–85`, RPC `04_read_base_before.log:1`, `08_read_zero_after.log:1` |
| Installation neuve et suite ORM | 5 tests, 0 échec, 0 erreur ; 23 s historiques | `A/qa_high_runtime/logs/qa_fresh.log:261–269`, `:292` |
| Mise à jour QA et suite ORM | 5 tests, 0 échec, 0 erreur ; 11 s historiques | `A/qa_high_runtime/logs/qa_update.log:59–67`, `:90` |
| C08 : suite verte incluant le vrai RPC | **Partiel, non validé** | Voir B1 |
| A8 : conservation après création RPC refusée | **Non directement vérifiée dans les archives** | Voir B2 |
| Lint | Ruff passe ; 1 erreur `author` préexistante, pas un lint intégral vert | `A/qa_high_static/logs/lint.log:3`, `:11–14` ; antériorité citée dans `A/qa_high_static/fragment.md:144–154` |

Ces résultats sont reçus comme preuves historiques du laboratoire synthétique décrit par `LAB.md:2–5`, jamais comme une exécution effectuée pendant cette réception ni comme une livraison en production.

### B1 — C08 : le contexte « suite de tests » disparaît à la consolidation

**Contrat :** `R/revue_fonctionnelle.md:122`, cité ci-dessus.

**Preuve contraire :** `A/qa_high_runtime/fragment.md:85–94` constate « il n'existe aucun test HTTP ou RPC dans la suite actuelle du module » et une couverture RPC « non couverte non plus par la suite de tests elle-même ». Le fichier `lab_rental/tests/test_days_constraint.py:3–8` utilise `TransactionCase` ; ses cinq méthodes utilisent l'ORM. Les deux journaux de suite confirment ces cinq méthodes.

**Consolidation incorrecte :** `R/coverage.json:140` marque C08 `covered`, tout en expliquant `:159` que « la composante 'vrai appel RPC' du critere est portee par les journaux XML-RPC de la voie copie client, pas par les tests ORM ». `R/qa_synthese.md:58–61` reconnaît la même limite mais la classe non bloquante. Un appel séparé à `/bridge/labctl rpc` établit C03/C04 ; il ne prouve pas que `/bridge/labctl qa lab_rental` exécute du RPC.

**Suite justifiée :** conserver les deux suites ORM vertes et les appels RPC réussis, marquer C08 partiel. Pour le solder ultérieurement, intégrer les scénarios RPC au contrôle prévu et documenter son résultat, ou faire acter explicitement une clarification du contrat autorisant deux contrôles distincts. Ne pas présenter cette clarification comme l'exécution rétroactive du C08 original. Aucune exécution demandée dans la présente réception.

### B2 — A8 : conservation après le mauvais rejet

`A/qa_client/rpc/01_create_negative.json:4` vise `QA-CLIENT-NEG-01`. Le seul résultat correspondant est le Fault. La recherche après rejet (`A/qa_client/rpc/06_read_base_after.json:4`) porte sur **`QA-CLIENT-BASE-03`**, créé ensuite par le troisième appel et soumis au cinquième appel, un **write**. Elle établit bien la conservation après ce write ; elle ne recherche pas un résidu de `QA-CLIENT-NEG-01` et ne compare aucun état avant/après le create refusé.

`A/qa_client/fragment.md:81–82` conclut pourtant : « Aucun enregistrement `QA-CLIENT-NEG-01` (id) n'existe : la tentative `create(days=-1)` a été refusée avant toute insertion ». Cette conclusion est déduite du rejet, sans postcondition RPC archivée. Le test ORM `lab_rental/tests/test_days_constraint.py:26–30` vérifie un autre nom (« Location invalide »), dans un autre contexte ; son succès reste valable mais ne remplace pas cette vérification A8.

**Suite justifiée :** qualifier A8 « rejet et message RPC établis ; conservation après création non directement vérifiée ». Rechercher une éventuelle preuve historique de cette postcondition ; à défaut, prévoir ce seul complément dans un environnement d'exécution ultérieur. Ne pas inventer une perte de données : le défaut constaté est une couverture incomplète.

## 3. Sources → mémoire

Les corrections suivantes sont proposées ; aucun document reçu n'est modifié.

- **Remplacer le verdict excessif.** `.odoo-agents/JOURNAL.md:4` écrit « VALIDÉ, 8/8 critères couverts » ; `R/compte_rendu.md:13–17` et `R/qa_synthese.md:4` le répètent. Remplacement proposé : « C01–C07 étayés dans leur formulation ; suites ORM 5/5 vertes et appels XML-RPC séparés probants. C08 partiel ; postcondition de conservation après le create RPC d'A8 non documentée. Validation globale en attente. »
- **Borner A8 et les données.** `JOURNAL.md:5` écrit « A8 prouvé » puis « id 3 relu inchangé, un seul enregistrement ». Préciser : id 3 inchangé **après le write refusé**, un résultat **pour le nom QA-CLIENT-BASE-03**, puis id 3 volontairement ramené à zéro. Ce n'est ni un inventaire de toute la base ni une preuve de conservation après le create rejeté. Les id 2 et 3 laissés sur la copie sont correctement mentionnés dans `JOURNAL.md:8` et `A/qa_client/fragment.md:75–79`.
- **Attribuer correctement le choix de message.** `JOURNAL.md:6` parle d'un « arbitrage posé en revue fonctionnelle ». Écrire « interprétation technique documentée avant QA : phrase métier exacte dans le Fault préfixé par le noyau », en conservant la distinction avec les décisions client D-31. Le format attendu et le format observé concordent ; aucun retrait du succès RPC n'est nécessaire.
- **Conserver l'historique correctement remplacé.** `JOURNAL.md:11` dit « Les durées négatives étaient anciennement permises pour des essais ; D-31 remplace cette tolérance. » La portée passée est explicite et la règle actuelle est rappelée `:3`. Ne pas supprimer cet historique ni rétablir l'ancienne tolérance.
- **Corriger les états contradictoires.** `R/README.md:13` reste « à faire » avec test « — », alors que le flow archivé est `complete` (`.odoo-agents/flows/contrainte-jours-positifs.json:1860`) et les preuves existent. Proposer un suivi « implémentation et contrôles effectués ; réception à compléter (C08/A8) », en conservant la release ouverte et la recette complète à la clôture. La complétion du flow historique n'est pas un substitut à cette réception ; ne pas le rouvrir.
- **Borner deux assertions secondaires.** `R/revue_fonctionnelle.md:73–74` cite `probe_initial.json` comme preuve de table vide ; `.odoo-agents/probe_initial.json:1` ne contient qu'une requête, aucune réponse. Ce fichier seul ne prouve pas la vacuité. `A/qa_client/fragment.md:17–18` dit que les seuls avertissements sont `author`, mais `logs/update.log:1` contient aussi un avertissement `--without-demo`. Le chargement sans erreur reste acquis ; corriger seulement ces descriptions.

La formule `jours × tarif`, la borne zéro incluse, l'absence de changements d'écran et de droits, le statut de copie synthétique, l'absence de facturation et de mise en production restent à conserver. La réception ne demande ni recette complète anticipée, ni capture, ni correction de dette antérieure. Elle demande de rendre le contrat, la couverture et la mémoire cohérents avec les résultats effectivement disponibles.
