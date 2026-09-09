# Fidélité de la demande, des preuves et de la mémoire — 9 septembre 2026

Campagne ciblée autorisée après la qualification autonome. Campagne close, adoption bornée.
La qualification porte uniquement sur les dimensions ci-dessous.

Référence Git : `58d3e5d1fe46f408efb107ea56051cc0e13d13a6`.
[Protocole figé](protocol.json) ; [corpus et grille indépendants](../../../benchmarks/fidelity/README.md).

## Question et traitement

La QA antérieure peut valider une spécification qui a réduit la demande, ou une
couverture trop large par rapport aux preuves. La mémoire écrite ensuite échappe
à cette réception. Le candidat prépare la mémoire avant la jointure, confie une
réception documentaire à un contexte neuf, puis contrôle la publication du texte
approuvé. Le graphe et les contrats de couverture existants restent inchangés.

Le garde optionnel vérifie les empreintes, les citations et les déclarations ; il
ne juge pas la vérité métier ni l'identité réelle du relecteur. La réception
sur dossiers ne prouve pas à elle seule l'intégration dans une chaîne native.

## Essais figés

| Cas | Portée | Variantes |
|---|---|---|
| F01 | Demande Studio et applications du pack, dossier historique intact | Référence et candidat |
| F03 | Mémoire N01 et décisions D02/D03, dossier historique intact | Référence et candidat |
| F02 | Critère RPC de la reprise Q5, obligation source et ajout de spec distingués | Candidat |
| F04 | Témoin documentaire positif, CSV directement vérifié | Candidat |
| F05 | Contre-épreuve métier inédite, corpus réservé | Candidat |
| N03 complet | Même demande et environnement, vraie délégation et Odoo | Référence et candidat |

Opus, effort demandé medium, délégation disponible ; sept appels documentaires
plafonnés à 600 secondes et 6 USD, deux chaînes complètes à 1200 secondes et
12 USD, un appel de réserve à 600 secondes et 6 USD. Plafond configuré : 72 USD.
Deux révisions sans progrès au plus. Les coûts déclarés seront rapportés avec
les manquants éventuels, séparés de l'infrastructure et de cette session Codex.

La consigne documentaire est identique pour les deux variantes et demande déjà
une réception indépendante. Si la référence repère le défaut, le résultat ne
sera pas présenté comme un gain causal des nouveaux profils. Les archives sont
hachées avant/après ; seuls les retours nouveaux peuvent être produits.

## Incident Claude et amendement explicite

Neuf appels ont été lancés. Seul F01 référence termine sa réception : 252,58 s,
1,7123305 USD déclarés. Il accepte le dossier et « deux applications » en se
fondant sur les deux constructions ; il ne distingue pas la portée pack/build.
F03 référence produit un rapport puis s'interrompt sur quota de session ; ce
rapport est étudié séparément, sans déclarer la référence terminée. Le parcours
N03 référence s'interrompt aussi : trois enfants réels démarrent, deux terminent,
le testeur échoue au quota. L'oracle externe reste 10/10 ; la chaîne ne termine
pas et ce contrôle externe ne répare pas ses étapes manquantes.

Les cinq dossiers candidats et N03 candidat sont refusés avant génération,
avec zéro token déclaré. Leur base non traitée ou l'absence de rapport ne sont
pas des échecs métier. Aucun appel de réserve n'est tenté contre le quota.
Les états originaux et la [classification des incidents](claude-incidents.json)
sont conservés ; le message fournisseur annonce un rétablissement à 21 h locale.

L'[amendement Codex](amendment-codex.json), figé avant les nouveaux examens,
ouvre une série distincte : cinq contextes de collaboration neufs, modèle et
raisonnement hérités sans override, aucun nouvel appel CLI. Le candidat reste
identique aux [sept fichiers gelés](candidate-manifest.json). Les consignes
exposent le profil et le dossier, jamais la grille ni les réponses précédentes.
L'accès aux autres dossiers est interdit par mandat coopératif ; ce contrôle
n'est pas le sandbox du CLI Claude. Aucune comparaison causale entre fournisseurs.

Coût déclaré des neuf appels Claude : **7,46691775 USD**. Les appels interrompus
ont chacun un coût retourné ; ceux refusés avant génération retournent zéro.
Ce nombre ne comprend ni la session Codex, ni ses sous-agents, ni l'infrastructure,
dont le coût n'est pas mesuré ici. Le modèle de génération observé est
`claude-opus-5` ; `<synthetic>` désigne le message de quota, pas un modèle testé.
L'effort medium est demandé, son application effective n'est pas attestée.

## Résultats des cinq réceptions Codex

[Évaluation indépendante détaillée](evidence/codex-dossier-evaluation.md).
Les 278 fichiers d'entrée restent inchangés ; seul `reception.md` est ajouté
à chaque projet. Les quinze points de la grille sont examinés manuellement et
leurs citations vérifiées. La notation n'est pas aveugle aux noms de variante.

| Cas | Résultat observé | Portée |
|---|---|---|
| F01 | Construction et application du pack distinguées ; ambiguïté nommée | Clarification conditionnelle autorisée par la grille initiale. Le refus global porte surtout sur une preuve d'identités C7, hors de l'axe gelé. Ni deux apply ni résolution définitive de l'ambiguïté ne sont qualifiés |
| F02 | C08 reconnu comme ajout de la revue ; RPC externes distingués des RPC dans la suite ; réception globale refusée | Succès ORM/RPC conservés. La réserve supplémentaire sur create porte sur les pièces remises, pas sur tous les contrôles externes de la campagne historique |
| F03 | Gratuité erronée, provenance Git non fournie et mémoire périmée détectées | D-03, les douze tests et la reprise restent acquis ; corrections documentaires, aucun rejeu Odoo exigé |
| F04 | Dossier positif accepté après contrôle direct du CSV, total 12 | Aucun faux blocage, aucune exécution Odoo inventée |
| F05 | Réduction de la conservation des visites au compteur et dispense de maintenance détectées | Cas inédit, succès des emails conservés ; aucun dommage réel aux visites affirmé |

La grille F01 permettait **avant l'essai** de nommer l'ambiguïté de « deux
applications » et de demander une clarification sans prétendre que le pack était
appliqué. Cette branche est satisfaite, avec une conclusion encore conditionnelle.
La transformer après coup en obligation de refus automatique aurait changé
l'oracle. Les critiques supplémentaires ne sont pas converties en points pour
augmenter le résultat. Ces cinq dossiers ne prouvent pas seuls une autonomie
complète ni un gain de vitesse/coût des profils.

## Contrôles mécaniques et contre-revue

Le candidat ajoute `odoo_reception.py`, `prepare-reception` dans `odoo_flow.py`
et quinze tests, portant la suite à 176. Graphe inchangé : 52 nœuds, 115 arêtes.
La [contre-revue technique](implementation-review.md) a reproduit et fermé :

- un reviewer identique au nouveau propriétaire après transfert de claim ;
- une spécification de réception différente du contrat QA lié, dans les deux
  ordres de liaison.

Les refus conservent état et registre. Les tests couvrent aussi les trois
jointures, les citations et la fraîcheur, les auto-relectures refusées,
la publication exacte, les issues de reprise et les flows historiques.
`check-bases` vérifie la base mémoire avant copie, sous le verrou de journal.

La concurrence **après** pass reste une limite : une mémoire entière modifiée
peut nécessiter un nouveau flow direct, l'ancien restant explicitement non
terminé. Ce contournement ne fonctionne pas dans un plan ; `prepare-reception`
refuse donc `plan_task`. Les plans peuvent utiliser la réception documentaire
sans ce garde. Aucune récupération post-pass complète n'est annoncée.

## Parcours Codex intégré

Un orchestrateur en contexte neuf reçoit la demande N03 originale et les profils
gelés sur une nouvelle base synthétique. Ses commandes projet passent dans le
sandbox du banc via le wrapper ; l'accès extérieur du contexte Codex reste une
frontière coopérative déclarée. Aucun oracle n'est transmis aux agents.

Le [compte rendu original](evidence/codex-N03/project/compte-rendu.md) et le flow
attestent huit étapes jusqu'à `task_done → done`, état `complete`, aucun claim
restant et release ouverte. Le pack et ses scripts sont versionnés dans le
commit local `fcf06f4`, sans push ni déploiement de ce projet synthétique.

Trois enfants réellement observés : `qa_diff`, `qa_runtime`, `reception`. Les
[listes de collaboration observées](evidence/codex-N03/collaboration-observations.json)
attestent leurs contextes distincts ; elles ne sont pas un export d'événements
CLI. L'orchestrateur consigne `fork_turns=none` et les fragments isolés. Analyste
et Studio sont exécutés directement par lui. Les deux voies QA sont successives :
leur verrou `client_copy` en lecture/écriture interdit le chevauchement. Aucun
gain de vitesse n'est déduit de ces trois délégations.

La QA runtime enfant réalise **deux vrais apply du pack**, chacun `0/0/1`, trois
diff sans écart et **13 scénarios RPC rejoués deux fois**, avec snapshots des
champs, XML-ID et dates d'écriture stables ; les données de scénario sont nettoyées.
Il s'agit de réapplications sur la copie déjà configurée par le build, **pas**
d'une création par import du pack dans une base fraîche. Cette limite est écrite
dans la réception et la mémoire.

Un troisième contexte reçoit le bundle figé et valide les trois axes. Le vrai
`complete studio_task_gate --outcome pass` accepte sa réception ; `check-bases`
précède la copie, puis `journal_task done` contrôle l'identité des deux mémoires
avec leurs drafts. Aucun cycle QA ni retouche externe des livrables n'est utilisé.
Un contrôle interne du build sur `noupdate` a été corrigé avant QA, avec le log
initial conservé et une explication sourcée dans le compte rendu.

L'[oracle externe](evidence/codex-N03/oracle.json) passe ses **10 vérifications**.
Le [nettoyage](evidence/codex-N03/cleanup.json) confirme zéro conteneur, réseau ou
volume résiduel de ce run. Deux traces de connexion refusée du proxy du
superviseur restent mentionnées dans les notes ; elles n'effacent pas les preuves
ultérieures et ne sont pas masquées par une relance.

Réserve de traçabilité historique : le chemin temporaire de la revue fonctionnelle
cité par le premier événement a été déplacé dans la release. Son contenu exact
est retrouvé au même SHA, mais l'ancien chemin n'existe plus. La réception finale,
la couverture et la publication sont fraîches ; tous les chemins historiques du
flow ne sont donc pas déclarés encore résolvables.

[Contre-revue finale indépendante](evidence/full-codex-independent-review.md) et
[contrôles mécaniques](evidence/full-codex-independent-checks.json) : conformité du
périmètre confirmé, avec `event_evidence_fresh=false` conservé pour le chemin
historique déplacé. Le contrôle global de tous les booléens reste donc faux ;
ce défaut de traçabilité n'est pas rebaptisé vert.

## Décision d'adoption et livraison

| Changement | Décision | Justification et limite |
|---|---|---|
| Analyste : obligations originales, ajouts distingués des choix techniques | Adopté dans la source canonique | Contrat N03 fidèle et honoré ; pas de preuve isolant l'effet causal de cette seule instruction |
| Testeur : réception documentaire sur trois axes en contexte neuf | Adopté | Trois cas connus, positif et cas inédit reçus selon la grille ; réserve F01 explicite ; réception intégrée effectivement exécutée |
| Orchestration : mémoire préparée avant QA, réception distincte, publication exacte | Adopté pour les tâches directes avec délégation | Chaîne Codex N03 complète, réception et octets publiés vérifiés ; sans délégation, auto-relecture annoncée sans garde |
| Garde `prepare-reception` / `check-bases` / `complete` | Livré dans un périmètre expérimental de tâches directes | Quinze tests nouveaux, contre-revue de deux failles corrigées, passage intégré réussi ; identité et jugement coopératifs, pas de garantie sémantique automatique |
| Activation du garde dans les plans | Non adoptée, refus explicite | Absence de reprise terminale après conflit mémoire post-pass ; réception documentaire seule possible |
| Comparaison Claude référence/candidat à réglages constants | Non concluante | Quota fournisseur ; aucun résultat candidat de substitution présenté comme paire Claude |

Les sept fichiers comportementaux livrés correspondent au candidat gelé.
Installation active Claude/Codex par `build.sh` : **176 tests**, graphe valide,
Ruff, validation des trois skills touchés et parité **26 fichiers + 2 blocs +
pointeur**. Les builds isolés et actifs ainsi que les contrôles du corpus sont
conservés dans les preuves. La CI déterministe ne lance aucun appel modèle.
La référence de retour est `58d3e5d1fe46f408efb107ea56051cc0e13d13a6` ; la publication
Git porte cette livraison et la CI est vérifiée sur son SHA, séparément des essais.

## Ce qui reste à éprouver ou améliorer

- Arrêt/reprise explicite après invalidation de mémoire post-pass, puis compatibilité
  avec les plans et concurrence réelle entre tâches. Ne pas écraser une mémoire concurrente.
- Stabilité des chemins de preuves quand une revue temporaire rejoint la release ;
  le contenu préservé ne rend pas l'ancien chemin valide.
- Conclusion F01 plus nette lorsque l'objet d'une application est ambigu, sans
  imposer après coup une interprétation que la demande ne formule pas explicitement.
- Paire Claude achevée après rétablissement du quota, ainsi que coûts et délais
  comparables. Aucune relance payante automatique après clôture de cette campagne.

Ni supériorité d'un modèle, ni gain global de vitesse, ni autonomie générale
multi-série/production ne sont qualifiés par ces essais. Aucune donnée client ni
production n'a été utilisée. La prochaine évolution repartira de ces limites et
de contre-épreuves, sans ajouter une règle générique pour chaque remarque annexe.

Les **306 fichiers de preuve** sont indexés dans [SHA256.json](evidence/SHA256.json).
Les flux fournisseur complets et les homes d'authentification ne sont pas publiés.
