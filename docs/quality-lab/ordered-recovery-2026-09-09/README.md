# Réceptions réelles, reprise ordonnée et tâche Odoo — 9 septembre 2026

La référence `c19e80540917709e1c8d59325a696aa27a7fc5ce` est conservée : aucun
nouveau défaut des profils ou du garde de reprise n’a été observé dans les trois
parcours documentaires. Cette campagne complète deux limites explicites de la
précédente : A reçoit réellement sa proposition avant que B publie ; le positif
part d’une réception réellement indépendante et suit le chemin direct.

## Résultats documentaires

| Cas | Exécution observée | Audit indépendant |
| --- | --- | --- |
| O01, concurrence ordonnée | A reçue avant B ; B publie sous verrou puis termine ; A reprend dans un contexte neuf, refuse la base périmée, fusionne et obtient un nouveau reçu avant publication | PASS : décisions, résultats acquis, portée et limites A/B conservés ; anciennes pièces intactes |
| O02, positif | Réception initiale réelle ; publication des drafts exacts sans nouvelle QA, nouveau bundle, reviewer ou retry | PASS : la trace des appels confirme le chemin direct |
| O03, inédit au gel | Un saut de ligne ajouté au reçu accepté change ses octets ; publication refusée, arrêt motivé et verrous libérés | PASS de la contre-épreuve : aucune réparation silencieuse ni publication |

L’ordre O01 est établi par les instantanés et les enveloppes natives : réception
A à 16:43:19 UTC, ouverture de B à 16:43:46, fin d’exécution B à 16:51:13.304,
ouverture de la reprise A à 16:51:24.493. Le contexte B reste adressable après sa
fin ; aucune destruction de session n’est revendiquée. Les comptes rendus,
citations et identifiants figurent dans l’[audit indépendant](evidence/audit/audit.md).

Le banc initialise uniquement une frontière QA documentaire. Il ne fabrique
aucun des reçus de cette campagne. Les preuves documentaires exécutées ne valent
pas tests Odoo. Tous les auteurs et relecteurs travaillent dans des contextes
réels distincts ; les reprises et les réceptions comportementales utilisent
`fork_turns=none`. La publication et les transitions utilisent les API publiques.

## Boucle de rétroaction du banc

Le [protocole](evidence/protocol.json), le corpus et le candidat sont figés avant
les exécutions. Le cas O03 est révélé seulement après gel, puis injecté après
l’acceptation réelle de son reçu. La référence est le premier et seul candidat ;
aucune modification opportuniste des rôles ou du graphe n’est adoptée.

Le correcteur initial suppose à tort un champ `resource_registry` toujours
présent et refuse le terminal public normal `task_done done` du positif. Ces
deux erreurs sont corrigées dans le banc, séparément des projets et du candidat.
Le gel original, les erreurs, la correction et les hashes avant/après restent
dans l’[amendement](evidence/corpus/amendment/AMENDMENT.json). La calibration
passe de 7 à 15 contrôles locaux, dont deux lectures/rejeux de la trace positive observée. Les 13 contrôles portables sont ajoutés à la CI sans appel modèle ; les deux contrôles liés à ce run local ne sont pas disponibles sur le runner GitHub. Les trois sorties
sont réévaluées sans retouche de leurs réponses ; l’auditeur relance lui-même les
vérifications mécaniques. La lecture sémantique demeure obligatoire.

Une annonce intermédiaire de succès du checker était erronée : une compilation
suivante masquait son code de sortie. Elle a été corrigée et le verdict brut
conservé. Deux invocations Python d’un script shell échouent avant mutation ;
les commandes correctes passent par Bash. Les autres refus de commande et les
ajustements de préparation sont conservés dans les traces, sans les compter
comme défauts métier du candidat.

## Épreuve Odoo locale

Le briefing effectif détermine la série depuis le manifest 19.0, ce qui corrige l’annonce initiale d’une origine configuration. Le module existant `lab_qualification`, version 19.0.1.0.0, est installé sur
une base synthétique de trois lignes. Un vrai dump PostgreSQL puis une
restauration créent `ordered_copy` ; `ordered_seed` reste la référence. Réseau
Docker interne, aucune base client, aucun port publié ; seules les données
synthétiques de la copie sont modifiables.

Un analyste indépendant vérifie les sources 19.0 et l’existant, puis écrit douze
critères. Le besoin est un invariant : zéro autorisé au brouillon, quantité
strictement positive pour un confirmé, y compris créations, écritures et imports.
La confirmation groupée invalide doit échouer intégralement. La tâche suit un
plan et la branche QA renforcée du graphe parce que le modèle est déjà peuplé.

Avant développement, l’orchestrateur clarifie la temporalité d’AC12 sans retirer
ses obligations : preuves QA avant la porte, réception à la porte, publication
mémoire et réception du plan ensuite. Le paragraphe introductif des critères est
déplacé hors de la section de cases après refus explicite du parseur ; le binding
n’avait pas encore réussi. Revue originale et consolidation sont conservées.

Le développeur ajoute les attentes avant l’invariant : **8 échecs métier sur
20 tests**, sans erreur d’infrastructure. Une contrainte conditionnelle
`models.Constraint` donne ensuite **20/20**, avec les mêmes octets de tests et
les quatre tests initiaux conservés. Les seize nouveaux tests utilisent un
utilisateur interne non superutilisateur. Les preuves incluent `load` en
création et mise à jour, la borne 1, le recordset mixte et la relecture après
savepoint. ACL, vue et manifest restent inchangés ; aucune réparation historique.

La QA indépendante relit le diff et chaque assertion, vérifie les mêmes noms et
hashes de tests, puis réutilise le rouge/vert et le lint. **Aucun nouveau test
Odoo ni lint répété par la QA.** Un contrôle neuf vérifie 88 conditions, les
images, les valeurs et les contraintes SQL dans des transactions READ ONLY sur
les deux bases. La nouvelle CHECK est validée uniquement sur la copie. Les trois
voies du graphe sont confiées à un seul testeur et sérialisées, puisqu’elles
partagent cette copie physique.

Deux erreurs de cadrage de ce vérificateur sont conservées : comparaison d’un
hash de fichier à un hash de contrat, puis option `--module` qui exigeait un
nouveau bilan Odoo absent d’une simple vérification. Le wrapper refuse malgré la
sortie zéro du second script ; la preuve finale se déclare générique et lie les
exécutions historiques. Aucun test neuf inventé pour obtenir un PASS.

La réception indépendante relève un hash différent pour la matrice de couverture :
le vérificateur QA avait lu son squelette, puis l’orchestrateur l’avait rempli.
Le relecteur reconstitue en mémoire le squelette déterministe depuis le contrat
inchangé et retrouve exactement le hash ancien. Il vérifie la couverture actuelle
et distingue explicitement ces deux moments dans le reçu. Aucun critère, code ou
résultat de test n’est retouché ; aucun test supplémentaire demandé pour cet écart.

La réception est positive sur les trois axes. L’API publie les deux drafts exacts,
puis le flow et la réception durable du plan terminent : **A validated, C prête
sans exécution**. La release reste ouverte. Le [reçu indépendant](evidence/integration/run/project/changelog/2026-09-09_01_quantite-positive-a-la-confirmation/reception/review.md)
et l’[état final](evidence/integration/completion.json) donnent les preuves.
Le nettoyage ciblé vérifie l’absence de tous les conteneurs et du réseau créés ;
le dump synthétique et les logs sont conservés.

## Traces natives, mesure et limites

Les exports retiennent la provenance des threads, le modèle/effort, les appels
et résultats d’outils, les réponses finales et les compteurs d’usage. Ils
excluent messages entrants, système, développeur et raisonnement de l’assistant.
L’exporteur v1 ne reconnaissait pas `phase=final_answer` ; sa version conservée et
l’export terminal corrigé distinguent ce défaut de collecte d’un défaut de reprise.

Les paramètres de certains messages natifs sont chiffrés. L’audit peut donc
vérifier la séparation des threads, les fichiers effectivement lus et les actes,
mais **ne certifie pas l’exposition intégrale aux consignes ni l’absence de
consignes additionnelles**. Des recherches trop larges ont également exposé des
chemins de campagnes historiques ; aucun accès observé à l’oracle courant.
Ce PASS comportemental ne vaut pas certification intégrale de l’isolation.

Le protocole borne 12 contextes d’exécution et 12 auxiliaires, dix minutes par
tour documentaire et vingt par tour Odoo, sans appel CLI payant. Les [métriques finales](evidence/metrics.json) comptent **9 contextes d’exécution
et 12 auxiliaires**, tous terminés ; tour le plus long : **525,038 secondes**.
Les followups sont détaillés par tour, avec leurs attentes entre tours exclues
de la durée active. Les compteurs natifs totalisent **14 714 010 jetons**, dont
13 771 648 jetons entrants en cache ; le root historique et l’infrastructure
sont exclus. Un seul dernier cumul est pris par thread, sans addition des
sous-compteurs cached/reasoning au total. Aucun coût monétaire n’est inféré.
Ces données ne prouvent aucun gain de vitesse. Le modèle/effort natif observé est
`gpt-6-astra / high`, sans override. Aucun comparatif de modèles ou de traitement
séquentiel/parallèle n’est réalisé.

## Livraison et réexécution

Le corpus `benchmarks/ordered_recovery/` permet de matérialiser un nouveau cas,
sceller les événements ordonnés et relancer calibration et contrôle mécanique.
Les nouvelles réceptions exigent de vrais contextes : les rejouer ne se réduit
pas à écrire un JSON PASS. Les archives conservent les chemins absolus historiques ;
`EVIDENCE.json` vérifie leurs octets par chemins relatifs sans prétendre déplacer
les bases, les flows ou les preuves d’exécution sur un autre poste.

Validation : graphe 54 nœuds/119 arêtes, **192 tests**, compilation du banc,
calibration locale **15/15**, builds isolé et actif, parité **26 fichiers + deux
blocs et pointeur**. La CI vérifie les contrats et la calibration portable sur
Python 3.10/3.12, sans LLM. Les verdicts et les empreintes sont relus séparément
par l’[auditeur du banc](evidence/corpus-review/review.md).

Décision : **référence conservée, qualification bornée complétée**. Le banc et sa
calibration CI sont livrés ; aucune nouvelle règle générale n’est ajoutée aux
profils. Les données clients, les historiques invalides, les autres séries et un
comparatif coût/délai avec une exécution sans délégation restent non mesurés.
