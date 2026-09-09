# Reprise après réception et mémoire concurrente — 9 septembre 2026

**Adoption bornée de V2**, après correction d’une omission de résultat détectée
par la relecture indépendante. La campagne traite le blocage identifié après la réception de fidélité : une
QA peut rester valable alors que la mémoire proposée ne l'est plus. Le correctif
ajoute une réception renouvelable dans le même flow, une publication reprenable
et un arrêt borné compatible avec les plans.

## Protocole et périmètre

Référence figée : `8d2b9403ae38b9d619f95c5f55ed3cce20dfc938`.
Le protocole et le corpus sont définis avant le candidat. Un auteur indépendant
prépare l'oracle ; le développeur ne reçoit pas le cas R04 avant le gel. Le
candidat est figé le 9 septembre à 16:02:16 UTC, après revue contradictoire et
correction du cas des bases mémoire vides. Son manifeste et son patch permettent
de retrouver les fichiers éprouvés.

Il s'agit de **tâches documentaires synthétiques**, sans développement ni test
Odoo. Le banc amorce explicitement une frontière QA et fabrique le reçu initial.
Ce reçu ne prouve aucune délégation passée. Les modifications d'état suivantes
passent par les API publiques ; les acteurs conservent les anciennes pièces.
Les preuves d'outillage et de jugement documentaire ne deviennent pas une
qualification générale des tâches Odoo.

Le plafond est de huit contextes d'exécution, huit enfants relecteurs/écrivains,
dix minutes par contexte et deux révisions sans progrès. Aucun appel CLI payant
n'est lancé. Les contextes de collaboration Codex héritent du modèle et de
l'effort de la session, sans override. Les coûts et tokens propres à ces contextes
ne sont pas exposés ici ; aucun coût nul ni gain de vitesse n'en est déduit.

## Référence, incidents et correction

R01 référence conserve les ajouts de B mais reste actif : `check-bases` refuse
la mémoire modifiée, la preuve documentaire reste valide, `prepare-reception`
refuse après pass et le journal ne peut pas terminer. La revendication est
libérée. Cet essai utilise un vrai contexte qui connaît le corpus : il n'est
pas présenté comme une référence aveugle. Le matérialiseur `--plan` reproduit
séparément le refus explicite du garde pour les tâches planifiées.

La revue indépendante trouve une régression avant gel : les nouvelles bases
vides ou composées d'espaces rendent impossible la citation exigée. Le correctif
conserve leurs hashes mais exige une citation seulement si elles contiennent du
texte non blanc. Les deux cas sont revérifiés indépendamment.

Le premier amorçage candidat échoue car le reçu **synthétique du banc** ne cite
pas les nouvelles bases. Un amendement de cinq lignes adapte ce reçu ; l'oracle,
les scénarios, les attendus et le candidat restent inchangés. Le gel initial,
le fichier original, le diff et les hashes sont conservés. Cet incident n'est
compté ni comme réussite ni comme échec comportemental du candidat. Le dossier
`candidate-R01-v2` est ce second amorçage **du candidat V1** ; les dossiers
`candidate-v2-R02/R04` correspondent à la seconde correction des rôles.

## Changements éprouvés

- `journal_task retry` mène à `reception_recovery_gate`, sous verrou mémoire,
  puis retourne au journal après une nouvelle réception indépendante. Les
  jointures QA existantes ne sont pas rejouées. Deux reprises au maximum ;
  `memory_task_blocked` donne une sortie explicite permettant `plan reopen`.
- Les nouvelles propositions partent de la mémoire courante. Le dossier conserve
  des copies de base et le relecteur doit confronter les contributions antérieures
  aux drafts. Demande, contrat, preuves et code demeurent identiques et frais.
- `publish-memory` vérifie toutes les cibles avant écriture et reconnaît, pour
  chacune, les octets initiaux ou déjà approuvés. La relance ne double pas le
  journal et refuse les valeurs d'un tiers.
- `upgrade-recovery` ajoute uniquement le delta connu à un ancien snapshot actif,
  sans claim ni journal exécuté, après vérification du graphe original exact.
  L'historique est conservé ; la migration générique reste stricte.

## Résultats comportementaux

| Cas | Résultat opérationnel V1 | Réception indépendante finale |
| --- | --- | --- |
| R01, plan et B réel | A validée, C prête sans démarrage, B conservé | Reformulation du résultat documentaire admise sur les textes cités |
| R02, publication partielle | A validée, C prête ; PROJECT déjà publié, JOURNAL publié | **Échec : le journal omet le succès accepté**, malgré un reviewer positif |
| R03, positif | A validée, C prête ; nouvelle réception choisie à cause du reçu fixture | Publication relue après achèvement ; équivalence contextuelle admise |
| R04, inédit au gel V1 | Publication refusée, A bloquée, C indisponible | Arrêt sain ; aucune preuve périmée blanchie |

Le [rapport indépendant V1](evidence/audit.md) confronte les pièces et les
publications. Les vérificateurs bruts de R01, R02 et R03 refusent deux prédicats
littéraux du journal. Le second exige `count(phrase_attendue) == 1` et signale
également l'absence de cette phrase, même sans duplication. Ces résultats restent
rouges dans les archives. L'audit distingue une reformulation étayée (R01/R03)
de la **perte réelle du succès documentaire dans R02** ; aucun assouplissement
n'est appliqué au checker ou à ses cinq contre-exemples négatifs.

### Boucle de rétroaction V2

V1 n'est pas adopté à ce stade. La correction suivante touche seulement les
rôles d'auteur et de relecteur : conserver explicitement le résultat déjà reçu,
sa portée et ses limites ; « preuve conservée » ne transmet pas que le contrôle
a réussi. Les scripts et le graphe restent ceux éprouvés en V1. V2 est figé à
16:17:23 UTC ; son patch et son manifeste restent distincts.

Un nouveau contexte relit l'ancien dossier R02 inchangé, sans son ancien reçu
ni le verdict d'audit. Il conclut **revise** : les deux premiers axes passent,
mais sources→mémoire perd le résultat positif. Son [rapport avec citations](evidence/v2-counter-review/notes.md)
confirme que la nouvelle consigne détecte ce défaut sans réclamer de nouvelle QA
Odoo. Sur une R02 neuve, le journal publié écrit « Contrôle documentaire
antérieur réussi » et conserve la décision A ainsi que la limite sans test Odoo.
Le reviewer neuf accepte ; A est validée, C prête sans démarrage. La régression
R04 sur V2 s'arrête de nouveau avec preuve périmée, sans réception A ni départ C.

Le checker R02 V2 conserve ses deux refus littéraux : la phrase exacte attendue
n'est pas recopiée. La publication exacte, la fraîcheur, les archives, le plan et
les revendications passent. L'[audit final indépendant](evidence/audit-v2.md)
confirme la correction de sens sur les textes réellement publiés et donne un
avis favorable à l'adoption bornée du V2 exact. R04 V2 passe tous ses contrôles. Son récit mentionne B préservé, alors qu’aucune
contribution B n’est publiée dans ce cas : ce n’est pas une preuve de concurrence. Ce second
R04 est une **régression connue**, le cas inédit au gel était R04 V1.

### Ce que les délégations prouvent

Huit contextes d'exécution (dont la préparation A et la référence non aveugle)
et sept contextes auxiliaires d'écriture/relecture sont utilisés, dans les
plafonds. Les contextes neufs emploient `fork_turns=none`. Les
[observations de collaboration](evidence/collaboration-observations.json)
conservent les noms effectivement démarrés ; un lancement refusé faute de slot
est repris après la fin d'un autre contexte, sans simuler le relecteur.

A et B ont coexisté ; B a réellement publié sous verrou. Cependant, la capture
du draft réel A est **postérieure à B** : A l'a déjà conservé. La reprise traite
le conflit avec le bundle initial synthétique. Cet essai ne démontre donc pas
la réconciliation d'un draft réellement rédigé par A avant B. Un flow B mal
aiguillé demeure actif sans claim ; son flow documentaire correct est terminé.
Aucun verrou orphelin n'est laissé.

R02 et R03 ont choisi une nouvelle réception, car le reçu hérité est une fixture.
R03 ne prouve pas le parcours positif direct sans retry. La reprise directe
idempotente est éprouvée séparément par les tests et par le SIGKILL réel. Les
nouveaux contrôles documentaires, les premières commandes échouées et les appels
`finish` prématurés restent distingués de la QA initiale et d'une exécution Odoo.

## Validation technique

192 tests d'outillage passent, dont 16 tests de reprise. Ils couvrent les trois
jointures QA, les plans, les preuves et le code périmés, l'ancien reçu refusé,
les bornes, les transferts de propriétaire, la migration restrictive, les bases
vides et la publication partielle. Le lint ciblé passe. Le graphe comporte
54 nœuds, 119 arêtes et cinq cycles bornés. La génération isolée et ses contrôles
passent : 26 fichiers, deux blocs d'aiguillage et le pointeur personnel ; les
trois skills touchés sont également validés.

La revue indépendante ajoute une **vraie interruption SIGKILL** d'un processus
après le premier remplacement. Sortie -9 ; la reprise produit
`already_published` pour PROJECT et `published` pour JOURNAL, puis termine le
journal sans réparation d'état. Cela complète la simulation unitaire de cette
interruption.

## Limites conservées

Le remplacement est atomique par fichier, pas entre PROJECT et JOURNAL ; aucune
résistance à une panne électrique n'est revendiquée. Le verrou est coopératif.
Le garde vérifie l'intégrité et les citations, pas la fidélité sémantique ni
l'identité cryptographique du relecteur. Les traces de collaboration attestent
les contextes réellement observés, sans export natif détaillé ni mesure de coût.

Les vieux drafts peuvent être périmés lors de la reprise : leur hash ne restaure
pas un fichier écrasé. Les rôles imposent des noms neufs et la conservation des
archives ; l'oracle de cette campagne vérifie leur maintien. Une preuve, une
source ou un code périmés exigent une autre tentative avec la QA appropriée.
Les plans historiques ne sont jamais migrés silencieusement.


## Livraison

Les deux scripts, le graphe et les trois rôles sont adoptés avec les limites
ci-dessus. `prepare-reception` est utilisable dans les plans équipés de la reprise ;
les anciens snapshots demandent une migration explicite. Aucune mémoire de projet
client, base distante ou production n'est modifiée par cette livraison.

Installation active, parité Claude/Codex, publication Git et CI sont vérifiées à
la livraison. Les fichiers de preuve sont inventoriés dans [EVIDENCE.json](EVIDENCE.json) ;
les hashes couvrent les résultats bruts, les incidents, les deux gels, les audits
et les comptes rendus sans les réécrire. Les chemins absolus des essais restent
ceux du scratch d'origine ; le corpus permet de rematérialiser de nouveaux essais.
