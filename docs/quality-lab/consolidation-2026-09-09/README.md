# Consolidation des preuves et message RPC — 9 septembre 2026

**Livré : le banc des modules peut vérifier le véritable message retourné en
XML-RPC. Le faux succès de consolidation reste ouvert.** Deux variantes de
consigne ont été éprouvées puis retirées : aucune n'a rendu sa décision sur le
dossier complet dans le budget fixé. Les rôles installés conservent la référence.

## Protocole et périmètre

Référence : `4e92bcb02f81f96bc577401791cc1f2470ef6dcc`. Six appels Claude,
alias demandé `opus`, effort `medium`, modèle observé `claude-opus-5` ; 180 s
par appel, contexte neuf et outils natifs dans bubblewrap. Aucun appel Codex
ni nouvelle délégation de voies dans cette campagne. La délégation réelle
reste documentée dans [la campagne précédente](../delegation-2026-09-09/README.md).

La jointure D31 est reconstruite en rejouant les six événements antérieurs
du flow, avec la revue et les trois fragments QA complets issus de cette
délégation. Les documents postérieurs à la jointure sont retirés et la mémoire
pré-reprise rétablie. Ce rejeu **ne reconstitue pas le contexte conversationnel
long** et ne réexécute pas les tests Odoo de ces fragments. Les attestations
constituent les entrées déclarées de l'exercice. L'instruction demande de
s'arrêter après l'enregistrement de la jointure.

Les cas réservés T41/T42 sont des **dossiers synthétiques de raisonnement QA**,
avec attestations textuelles et vrai graphe exécuté. Ils ne sont pas des tests
ORM de droits multi-sociétés. Les profils candidats sont exportés depuis la
référence, seule la consigne de jointure change ; le nouveau transport RPC
n'est pas disponible dans ces six exercices de consolidation.

[Protocole initial](evidence/protocol.json), [variante V2 et nouveau cas](evidence/protocol-v2.json),
[résultats évalués](evidence/evaluation.json). Les entrées, réponses, états du
graphe, commandes et sorties `claim`/`complete`, variantes et empreintes sont
conservés dans `evidence/`. Les flux bruts et homes fournisseur restent hors
du dépôt ; leurs empreintes sont conservées.

## Résultats de consolidation

| Essai | Exécution | Décision enregistrée | Évaluation |
|---|---|---|---|
| D31, référence | timeout à 180,01 s | `pass` | Faux succès : A8 explicitement partiel |
| D31, V1 : table de couverture avant verdict | timeout à 180,01 s | aucune | Inachevé, aucun gain établi |
| T41, V1 : administrateur seulement | achevé, 125,40 s | `blocked` | Correct : gestionnaire B non testé |
| T41, V1 : preuve complète sous gestionnaire B | achevé, 138,58 s | `pass` | Correct, aucune capture hors contrat exigée |
| D31, V2 : traiter d'abord la preuve absente | timeout à 180,01 s | aucune | Inachevé, arrêt de cette variante |
| T42, V2 : lecture B autorisée, transfert interdit | achevé, 110,70 s | `pass` | Correct : contrat différent respecté |

La référence écrit dans sa [QA](evidence/known-reference/qa.md) : « 8 critères
verts sur 9, le neuvième partiel », puis enregistre `pass`. Le critère A8
original exige que le message configuré soit effectivement remonté à
l'utilisateur. Le fragment copie dit expressément que la couche RPC n'a pas
été traversée. Reporter ce contrôle à la clôture ne satisfait pas le contrat.
La référence modifie aussi le suivi README de la release malgré la consigne
d'arrêt à la jointure ; cette modification est relevée dans les empreintes.

Le timeout de la référence ne supprime pas cette transition fautive déjà
enregistrée. En revanche, les timeouts candidats **ne prouvent pas une erreur
de décision** : aucune décision n'a été rendue. Ils empêchent l'adoption dans
les conditions de l'essai. Après deux révisions sans résultat exploitable sur
D31, les deux ajouts sont retirés des rôles canoniques. Les bons résultats des
petits dossiers ne justifient pas une promotion ni un gain général de fiabilité.

## Correction du transport et contre-épreuve sur Odoo

`scripts/odoo_bench_native.py` ajoute `labctl rpc FICHIER.json` pour le modèle
du cas, sur `lab_client`, sous l'administrateur synthétique. Le vrai serveur
XML-RPC est démarré puis arrêté à chaque appel, dans le réseau Docker du banc,
avec un proxy de boucle locale. Le module est synchronisé avant l'appel.
Une requête ne peut pas fournir d'URL, de base ou d'identité externe. Le Fault
et son message sont conservés ; son code de sortie est 1, jamais un succès
de QA implicite. Le mode Studio réutilise le démarrage HTTP existant.

Deux stacks indépendantes ont été créées puis supprimées. L'ancien `handle`
refuse la commande RPC ; le nouveau traverse réellement la couche de service.
Huit appels RPC dans chaque stack vérifient création valide, zéro, refus de
création et d'écriture négatives, lecture après refus, comptage, mutation du
message et restauration. L'oracle SQL indépendant reste à **4/4** dans les
deux exécutions.

La première mutation était inopérante : changer seulement le message Python
laissait le message original servi. Ce résultat est conservé dans
[l'essai initial](evidence/rpc-runtime/result.json). La lecture des sources
19.0 établit la cause : `odoo/orm/models.py:3270` consulte d'abord
`ir.model.constraint.message`, avant le message de l'objet Python ;
`odoo/service/model.py:207` transforme ensuite l'erreur d'intégrité en
`ValidationError`. L'oracle n'a pas été assoupli. Un
[amendement de calibration](evidence/protocol-amendment.json) prévoit une
seconde stack et une mutation du message réellement enregistré en base.

La [contre-épreuve corrigée](evidence/rpc-runtime-calibrated/result.json)
obtient **7/7 contrôles vrais** : message configuré retourné à la création
et à l'écriture, location valide intacte, zéro accepté, aucune création
refusée persistée, mauvais message détecté malgré le Fault, message attendu
retrouvé après restauration. Le contrôle nommé `fresh_registry_after_restore`
atteste ici le message après restauration ; il ne mesure pas séparément
un effet causal du cache de registre. Les réponses et scripts originaux sont
préservés. Les deux vérifications de nettoyage ne trouvent aucun conteneur restant.

Cette preuve RPC n'atteste pas le rendu navigateur, ni les droits d'un
utilisateur ordinaire. Elle ne corrige pas rétrospectivement la QA de l'ancien
flow. Une nouvelle chaîne complète utilisant spontanément le transport reste
à mesurer. Le banc sérialise toujours ses opérations Odoo.

## Validation et suite

Sept nouveaux tests déterministes couvrent réponses/Faults, refus de cible
externe ou de requête invalide, périmètre des fichiers, journalisation du
Fault, indisponibilité HTTP et nettoyage du service. Les tests du transport
ont été exécutés rouges avant son ajout, puis verts. Suite complète :
**136 tests verts** ; graphe et génération des profils contrôlés.

La prochaine boucle sur la consolidation doit éprouver une réception plus
structurée des critères et des preuves, avec un budget adapté au dossier
complet et une référence comparable. Ajouter un troisième rappel de texte
sans nouveau mécanisme n'est pas justifié par ces essais. Restent également
à mesurer : droits multi-sociétés réellement exécutés, restauration avec
filestore, navigateur, autres séries et comparaison contrôlée des coûts.

Les scripts d'expérience archivés conservent leurs chemins scratch d'origine.
Pour reconstruire les entrées D31 ailleurs, les projets interrompu/repris sont
dans `../delegation-2026-09-09/evidence/` ; les empreintes d'entrée de chaque
essai permettent le contrôle. Les scripts de mesure ne font pas partie de
la CI et ne doivent pas lancer d'appels modèles implicitement.
