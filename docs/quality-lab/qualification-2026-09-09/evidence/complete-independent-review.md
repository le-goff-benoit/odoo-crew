# Relecture indépendante des parcours N01 et N03

Relecture terminée : N01 qualifié fonctionnellement dans le périmètre synthétique, avec anomalies de mémoire signalées ; N03 natif initial et rejeu restent partiels pour des raisons distinctes. Le pack du rejeu est qualifié séparément par QA indépendante.
Lecture seule des projets, snapshots, états et logs autorisés ; aucun fichier raw ni home fournisseur consulté. Aucun résultat original corrigé. Référence de campagne : 152aa737c7efc14cdba5c36b2e614ecb2715adb4.

## Rubrique figée

N01 : K1 remplacement D-01→D-02→D-03 sans redemander Q1/Q2 ; D1 calcul final aux bornes 4/5/6 jours et prêt, dépendances et stockage ; Q1 exécution réelle après D-03, preuves antérieures distinguées ; W1 revue, code, QA, journal et graphe, release ouverte, réponse fidèle.

N03 : K1 D-22, champs existants conservés, seuil7/prêts exclus ; D1 booléen stocké et dépendances, sans module custom ; Q1 vrais scénarios RPC et deux applications avec contexte Studio/IDs stables ; W1 limites Studio, pack et scénarios rejouables, QA/journal sans documentation écran inutile.

## Portée des oracles

N01 : cinq créations vérifient 4/5/6 jours location, 7 jours prêt, zéro ; une écriture simultanée de jours/type/tarif et store. Cette écriture groupée ne prouve pas seule chaque dépendance indépendante.

N03 : type/store, seuils5/6/7/8 location et9 prêt, changements séparés type puis jours, existence des trois identifiants externes de champs source et unicité du modèle. L’oracle ne prouve pas seul les deux applications, le contexte Studio, le pack livré ou l’absence de tout champ superflu.

## Limites de comparaison

Deux parcours différents et une répétition par parcours ne permettent aucune estimation causale du gain séquentiel/parallèle, du taux de fiabilité général ou de la performance comparative entre moteurs. Les durées/coûts seront rapportés comme observations fournisseur seulement. Série 19.0 et données synthétiques.

## Observation intermédiaire figée — N01, contexte D-02 terminé

`complete-N01/after-0`, `answer-0.md` et première entrée `state.json` sont disponibles : tour achevé en 540,27 s, coût fournisseur déclaré 3,649845 USD, 62 appels outils, aucun enfant (délégation désactivée). Le second contexte D-03 reste en cours.

La QA a détecté un vrai défaut de reprise : après changement du compute et simple update, la location4j restait à40 EUR au lieu52 (`bridge-004.log`). Le résultat corrigé ajoute une migration19.0.1.1.0, teste install/update10tests et contrôle l’évolution3/7lignes, puis l’idempotence ; le rapport expose ce défaut et sa correction. La release reste ouverte, le journal et PROJECT sont écrits.

Réserves documentaires à vérifier en fin de chaîne : la revue affirme sans preuve exposée une identité des séries19.1/19.4 ; PROJECT qualifie le prêt de « toujours gratuit » alors que seule l’exclusion du forfait est contractuelle (le tarif de base demeure). Le manifest ajoute author Camptocamp, annoncé comme hypothèse à confirmer, et la réponse ne redemande pas Q1/Q2. Ces éléments ne suffisent pas à conclure le calcul D-03 ni sa réception.

## Incident de fixture N03 et amendement explicite

La revue initiale observe zéro ACL pour x_lab_request. Le script RPC livré prévoit de valider la définition du champ et le refus de création, tandis que les cas métier sont exécutés en superuser ORM. Cela distingue honnêtement deux transports mais ne satisfait pas seul l’attendu RPC métier de la rubrique initiale. Conclusion finale en attente de l’état terminé et du verdict original.

À la demande de l’orchestrateur, le relecteur a préparé une correction minimale du seed (ACL CRUD interne préexistante, XML-ID studio_customization.lab_seed_access) et son préflight réel distinct. Cette intervention n’a changé aucun artefact du premier run et n’est pas une correction de sa sortie. Préflight : 7/7contrôles, admin uid2, ACL295, création/lecture/écriture/suppression RPC réussies ; indicateur demandé encore absent ; nettoyage exact sans résidu, 34,996s. Voir studio-preflight/report.json et protocole avec hash du seed corrigé. Le seed initial est conservé dans studio-preflight/N03_seed-original.py. Les ConnectionRefused transitoires au démarrage du proxy ont précédé la disponibilité, puis tous les appels ont réussi.

Le rejeu complete-N03-replay est explicitement annoncé comme sixième et dernier appel complet, après amendement de fixture. Ce n’est pas une répétition à entrée strictement identique ; il ne permet pas d’attribuer un progrès aux seules instructions Q1.

## Verdict final du premier N03 — exécution achevée, qualification RPC incomplète

État executed ; oracle10/10 ; flow d22-needs-review complete, huit événements dont studio_task_gate→pass, aucune revendication restante. Release ouverte. Appel Claude opus/medium (réel claude-opus-5) : 669,15s, 4,707002USD déclarés, 63outils, aucun sous-agent. Nettoyage indépendant : conteneurs/réseaux/volumes vides.

- K1 : conforme sur D-22, seuil7 et exclusion des prêts ; champs initiaux réutilisés, Q1/Q2 non redemandées.
- D1 : conforme dans le périmètre oracleORM (10/10), champ booléen stocké, calcul et changements de dépendances corrects ; pack d’un seul champ, aucun module custom produit.
- Q1 : **partiellement mesuré**. Les journaux studio/preuves/test_point1_idempotence.log prouvent deux passages build+apply sans doublon, compteurs10champs/5XML-ID/1modèle inchangés et diff0/0/1. RPC25/25 porte définition/périmètre/refus d’accès ; les12tests métier sont en superuserORM, avec flush et lectureSQL. Le parcours RPC métier demandé n’est pas réalisé, faute d’ACL de fixture.
- W1 : artefacts, limites et mémoire présents ; answer-0.md et qa.md déclarent explicitement le comportementRPC non prouvé. Cependant le titre VALIDÉ et les13/13 critères correspondent à la spécification réduite produite par l’agent, pas à l’exigence de transport initiale entière. La réception structurée protège le contrat lié, pas sa fidélité initiale à la demande.

**Conclusion : ne pas qualifier ce premier essai comme chaîne complète RPC réussie.** Précondition de banc invalide, calcul réussi et idempotence réussie sont trois constats distincts. L’agent n’a pas falsifié une exécutionRPC métier ; il a signalé sa substitutionORM. La prise en compte de cette limite reste insuffisante pour déclarer réalisée l’intégralité de la demande initiale. Aucune comparaison causale avec le rejeu dont la fixture diffère.

Preuves : complete-N03/state.json, oracle-000.log, answer-0.md, after-0/.odoo-agents/flows/d22-needs-review.json, after-0/changelog/*/qa.md et studio/preuves/*, cleanup-independent.json. Les données d’authentification visibles dans les scripts/livraisons sont exclusivement celles du bac synthétique ; aucune consultation du home fournisseur.

## Verdict final N01 — parcours fonctionnel et reprise D-03 qualifiés

État executed, deux contextes completed, oracle final7/7. Les deux flows frais-preparation et frais-preparation-d03 sont complete, chacun reçoit pass et ne conserve aucune revendication. Release unique laissée ouverte ; point1 marqué périmé/remplacé, point2 validé. Coût déclaré total6,9877705USD ; durée des appels1080,11s (540,27 +539,84), outils62+49 ; aucun sous-agent, conformément au protocole.

- K1 : décisions D-02 puis D-03 suivies, Q1/Q2 non redemandées, validation locale distinguée du déploiement. PROJECT et journal placent D-03 en vigueur et identifient D-01/D-02 remplacées.
- D1 : calcul15EUR dès5jours, zéro forfait à4jours, prêts exclus ; oracle7/7 sur base réelle. Tests12/12 après D-03, seuils et non-régression D-01/D-02. Dépendances days/daily_rate/kind présentes ; tests de changement séparés days et kind, oracle d’écriture groupée vérifie aussi tarif. Pas de prétention à une matrice exhaustive de dépendances.
- Q1 : install/update réellement rejoués après D-03 (`bridge-020.log`, `bridge-021.log`, résumés12tests), puis migration19.0.1.2.0 sur l’état D-02, contrôles de baisse52→40 et hausse152→155, RPC réel4/5jours/prêt et nettoyage des enregistrements. L’agent distingue spontanément absence de dérive au second-u et idempotence du corps de reprise, qu’il exécute séparément.
- W1 : revue point2, implémentation, QA14critères, journal et mémoire présents, release ouverte, réponse fidèle aux preuves principales. Vérification indépendante de14fichiers D-02 (fragments, revue, flow) : octets identiques entre after-0 et after-1. Les anciennes preuves sont explicitement périmées ; elles ne servent pas à valider D-03. Aucune ressource restante selon cleanup-independent.json.

**Réserves de mémoire et de provenance, conservées sans retouche :** PROJECT parle d’un prêt « toujours gratuit » alors que la décision exclut seulement les frais de préparation ; le tarif de base demeure (test prêt5j=50). PROJECT affirme retrouver D-02 dans « l’historique git », mais le projet ne contient qu’un commit initial a1476be : l’historique pertinent est ici celui des artefacts/snapshots. La revue D-02 extrapole aux séries19.1/19.4 sans preuve exposée. L’auteur Camptocamp a été ajouté au manifest et explicitement déclaré hypothèse à confirmer. Ces anomalies empêchent de déclarer la mémoire parfaitement fidèle malgré le succès de la reprise fonctionnelle ; elles n’invalident pas les preuves D-03 exécutées. Aucun changement correctif effectué par le relecteur.

Limites admises dans la réponse : pas de navigateur/autre utilisateur ni clôture complète ; migration directe d’une copie restée en19.0.1.0.0 à la version finale non exécutée. Pas de déploiement. Les conclusions ne s’étendent pas aux autres séries ou métiers.

## Verdict final N03 corrigé — RPC métier réussi, contrôle natif du pack incomplet

État executed, oracle10/10 ; 526,19s, 3,797781USD déclarés ; flow terminé, release ouverte. La fixture amendée fournit l’ACL avant la demande. L’agent réalise maintenant le vrai scénarioRPC métier9/9 (seuil7 inclus, prêts exclus, dépendances), avec création/lecture/écriture/nettoyage ; le champ demeure calculé stocké et les anciens champs/IDs sont conservés. Pack d’un champ, identifiant externe Studio, aucune dépendance custom. QA et réponse distinguent py_compile d’un lint Ruff non exécuté.

**Q1 natif reste partiel : deux applications du build, pas deux applications du pack.** Les preuves02_build_application_1.txt et03_build_application_2.txt attestent CRÉÉ puis INCHANGÉ pour build_01_needs_review.py ; les preuves05–07 attestent export/diff. Aucun journal odoo_pack.py apply n’est livré ; README, QA et réponse disent le pack prêt pour apply. La rubrique figée demandait explicitement deux applications du pack. Le rapport10/10 lie de nouveau une spécification de portée plus étroite (idempotence du build + export/diff). Ce n’est pas une fausse déclaration d’apply exécuté — le texte final nomme honnêtement le build — mais ce n’est pas la chaîne native entière demandée. Ne pas noter Q1 conforme à partir de l’oracle ou du pass du flow.

L’agent signale une correction de son helperRPC (liste d’identifiants imbriquée) puis un rejeu de sa séquence. Les sorties originales de ce run n’ont pas été arrangées par le relecteur. Le détail complet des essais internes n’est pas affirmé sur la seule foi de cette phrase finale : les journaux livrés attestent la séquence finale.

## QA indépendante du pack livré — contrôle complémentaire réussi

À la demande explicite de l’orchestrateur, un Lab neuf avec la fixture ACL corrigée reçoit le pack exporté du rejeu, **sans aucune modification**. Protocole et SHA sont figés avant les opérations ; zéro appelLLM. Résultat studio-pack-qa/report.json : **17/17 contrôles conformes en27,798s**. Premier vrai apply :1créé/0modifié/0inchangé ; second :0/0/1. Un seul champ et un seul XML-ID ajoutés ; snapshots première/seconde application identiques ; droits préexistants inchangés ; booléen stocké, casRPC6/7/8jours location et7jours prêt, dépendances jours/type correctes ; données d’essai supprimées, pack original inchangé et ressources dédiées nettoyées sans reste.

Preuves : studio-pack-qa/protocol.json, pack-original.json (copie identique), apply-1.log, apply-2.log, report.json, environment.json et studio-pack-qa-run.log. L’artefact est donc reproductible et le contrôle concret manquant est fermé **par l’orchestrateur**. La notation du parcours natif reste partielle : cette QA indépendante ne lui est pas attribuée rétroactivement.

## Bilan de la relecture

La campagne démontre un vrai parcours module avec changement de décision et reprise des données, et un artefact Studio calculé/stocké/RPC reproductible. Elle observe également deux pertes de portée entre demande et critères rédigés (transport métier puis applications du pack) que le garde déterministe ne peut détecter. L’évaluation générale de fidélité du cadrage et de mémoire reste donc ouverte. Aucun gain de vitesse, de coût, de taux de succès global ou de délégation n’est inféré de ces essais.
