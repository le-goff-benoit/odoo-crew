# Qualification autonome — 9 septembre 2026

Campagne autorisée par l’utilisateur, référence `152aa737c7efc14cdba5c36b2e614ecb2715adb4`.
Le [plan](../QUALIFICATION_PLAN.md) fixe les dimensions et les bornes. Ce bilan
sépare les essais de composants, les comportements des agents et les parcours
complets. Une réussite synthétique ne qualifie pas tous les métiers Odoo.

## Matrice de qualification

| Dimension | Résultat mesuré | Portée et supervision à conserver |
|---|---|---|
| Droits serveur | Témoin 19/19 ; mutant sans règle détecté en ORM et XML-RPC | Utilisateur ordinaire limité à une société, modèle synthétique 19.0 ; ne mesure pas la conception de droits par un agent |
| Restauration | 3/3 scénarios conformes, voisine DB/filestore inchangée | Vrai restaurateur inchangé, ZIP SQL et pièce jointe, neutralisation ; base synthétique `base` en 19.0 |
| Versions et navigateur | ORM 18 et 19 : quatre contrôles chacun ; Chrome19 + postcondition serveur positifs, mutant détecté | Une fiche synthétique, utilisateur admin ; aucune extrapolation vers 17 ou SaaS |
| Cohérence de la réception QA | Rapports générés concordants avec les issues ; négatifs refusés, positif accepté | Rendu déterministe adopté ; récits libres encore imparfaits, relecture sémantique requise |
| Délégation et reprise réelle | Technique démontrée : 7 enfants natifs, reprise même environnement, SQL4/4 et RPC3/3 ; réception globale refusée sur C08 | Critère de suite RPC non rempli, `covered` erroné ; données vides à la coupure |
| Décision révisée et mémoire | N01 fonctionnel réussi : deux contextes, migration et oracle7/7 ; mémoire imparfaite | Prêt dit « gratuit » à tort, historique Git suraffirmé ; conserver la décision source |
| Studio | Calcul/RPC réussis ; pack livré vérifié17/17 par QA externe ; parcours natif partiel | Deux constructions ne remplacent pas deux applications du pack ; aucune écriture Online |
| Coût / autonomie | 10 appels, 24,7189542 USD déclarés pour9 ; un coût inconnu ; 0 sollicitation humaine | Coûts CLI seuls, total inconnu ; aucun classement ou gain causal |

## Contrôle des oracles et incidents conservés

**Droits.** Le premier oracle attendait le nom Python de l’exception dans un
Fault XML-RPC. Le transport 19.0 expose un code de faute. Le contrat a été
corrigé à partir des sources et la réponse originale réévaluée sans nouvelle
exécution. Un nouveau témoin et un mutant ont ensuite été exécutés. Aucun
changement d’instruction agent n’est attribué à cette erreur du banc.
Voir [résultats](evidence/rights/RESULTS.md) et [erratum](../../../benchmarks/qualification/rights/ORACLE_ERRATUM.md).

**Restauration.** La copie byte-identique du vrai restaurateur récupère les
octets de la pièce jointe via ORM, neutralise cron et SMTP et fixe l’URL locale.
L’archive sans dump est refusée avant création. L’update d’un module inexistant
échoue sans déclaration « prête » ; la base locale restaurée reste inspectable.
La base voisine et son fichier sentinelle sont inchangés après chaque scénario.
Le mot de passe admin n’a pas été authentifié par RPC. Voir le
[rapport brut](evidence/restore/report.json). La revue a trouvé un gel incomplet
du lanceur et des scripts ORM dans cette première archive. Ils sont maintenant
copiés avant exécution et les copies sont utilisées ; un
[second passage](evidence/restore-replay/report.json) confirme les trois scénarios
en 44,298 s et le nettoyage, avec des empreintes complètes. L’archive initiale
et sa limite restent inchangées.

**Navigateur.** Les premiers essais Odoo ont terminé avec un code zéro malgré
le saut du test après un crash Chrome. L’oracle indépendant a refusé ce faux
succès. Le diagnostic prouve un tmpfs inaccessible au profil Chrome. Après correction du
montage isolé, le vrai navigateur clique la confirmation, constate le statut
et l’ORM vérifie état et montant. Le mutant échoue exactement sur l’assertion
serveur volontairement fausse. Voir [les cinq essais et leurs limites](evidence/versions/README.md).

## Réception QA : adoption bornée du rendu

`odoo_flow.py qa-report` génère le rapport à partir de la couverture et de l’issue
proposée. La réception revérifie rapport, contrat, couverture, propriétaire et
issue lorsque le rapport enregistré est cité. Une sortie négative reste possible
avec un constat du manque si les anciennes preuves ont changé. Les flows anciens
et les rapports libres restent compatibles, sans nouvelle garantie mécanique.

| Essai natif, Claude opus/medium | Durée CLI | Coût déclaré | Issue |
|---|---:|---:|---|
| known-reference | 283.03 s | 2.413645 USD | retry |
| known-candidate | 243.54 s | 2.133661 USD | retry |
| held-positive-candidate | 120.47 s | 0.883573 USD | pass |
| held-negative-candidate | 142.84 s | 0.915006 USD | retry |

La référence fraîche refuse correctement D31 : le faux libellé observé dans la
campagne précédente n’est pas systématiquement reproduit. Elle suraffirme
néanmoins huit critères prouvés deux fois alors que les fragments répartissent
leur couverture. Le candidat génère un rapport exact, reconnaît A8 partiel et
n’utilise plus cette synthèse abusive. Le cas P62 est accepté en distinguant les
identités des fragments. J73 reconnaît l’insuffisance du compte de lignes, mais contient aussi un mauvais
numéro de ligne dans la réponse RPC : une erreur de préparation a introduit cette
seconde contradiction. Son refus ne mesure donc pas isolément le contrôle de
l’invariance. La réponse et la fixture sont conservées avec un
[erratum](evidence/J73-preparation-erratum.json). J73 est un transfert du témoin I7,
pas une nouvelle famille métier indépendante. Il anticipe aussi la création du
journal malgré l’arrêt demandé après la jointure, sans engager de nœud aval.

**Adopté :** outil de rendu et instruction ciblée pour l’utiliser. Tests de
non-régression, preuve de comportement et contre-épreuve positive justifient
cette adoption. Aucun gain causal de fiabilité ou de vitesse n’est estimé.
**Limite restante :** dans le récit libre D31, le candidat présente d’anciens
répertoires comme disparus alors que seule leur absence de la sandbox est prouvée.
Le rendu contrôlé n’élimine pas toutes les affirmations excessives de la réponse
finale. Un statut `covered` mensonger peut toujours franchir le contrôle déclaratif.
Voir la [relecture indépendante des quatre essais](evidence/qa-independent-review.md).

## Décision révisée : calcul et migration réussis, mémoire imparfaite

N01 termine les deux contextes D-02 puis D-03 dans la même release ouverte.
La première QA détecte les valeurs stockées non recalculées après update ;
l’agent ajoute une migration et prouve son effet. Après D-03, une seconde migration,
des tests frais et des appels RPC démontrent les nouvelles bornes et les valeurs
existantes. Oracle final7/7, suite12/12, quatorze fichiers de preuve D-02 conservés
à l’identique et explicitement déclarés périmés pour D-03. Les questions déjà
tranchées ne sont pas redemandées. Durée CLI : 1080,11 s pour les deux contextes ;
coût déclaré : 6,9877705 USD.

La qualification de la mémoire reste partielle : PROJECT décrit les prêts comme
« toujours gratuits » alors que seul le forfait de préparation est exclu, et
mentionne un historique Git D-02 qui n’existe pas dans ce dépôt à un seul commit
initial. La décision et le calcul écrits ailleurs sont corrects. La revue extrapole
aussi aux séries19.1/19.4 sans preuve exposée ; l’auteur Camptocamp ajouté au manifest
est présenté comme une hypothèse à confirmer. Ces récits ne doivent pas remplacer
la décision métier source. Les [revues des parcours complets](evidence/complete-independent-review.md)
conservent ces réserves et distinguent résultat fonctionnel, QA et mémoire.

## Reprise déléguée : technique acquise, réception globale refusée

Le [protocole et les preuves de reprise](evidence/recovery/README.md) conservent
une vraie coupure à 481,10 s, puis un second contexte terminé en 400,59 s.
Sept sous-agents natifs sont attestés : analyste, développeur, deux testeurs
interrompus, puis trois testeurs achevés. Le chevauchement commun des fenêtres
natives de la seconde QA est de 78,865 s ; ce n’est pas une mesure CPU ni un gain
de vitesse. Le pont Odoo sérialise toujours ses opérations.

L’ancien groupe de processus est arrêté, le pont drainé, puis l’orchestrateur
libère lui-même les trois revendications abandonnées avec preuve. PostgreSQL,
les deux bases, le dépôt Git, le code et les décisions sont conservés à la
frontière de reprise. `lab_qa` est ensuite recréée volontairement par `--fresh` ;
`lab_client` reste la même base. Elle était vide à la coupure : aucune conservation
d’un jeu métier non vide pendant cette interruption n’est revendiquée.

Les oracles indépendants finaux passent (SQL4/4 et RPC3/3), avec phrase exacte
reçue et valeurs conservées après rejet. Le code et les décisions sont inchangés
entre coupure et fin. Aucun correctif manuel du code généré, aucune sollicitation
humaine ; nettoyage vérifié.

**Le pass global reste injustifié.** C08, rédigé par l’analyste, impose des
scénarios RPC dans la suite appelée par `/bridge/labctl qa`. Cette suite est ORM ;
la QA fusionne des RPC externes et déclare néanmoins C08 `covered`. L’arbitrage
indépendant exige `partial` sous ce contrat. L’utilisateur demandait une vraie
preuve RPC sans imposer son intégration à cette commande : une surspécification
initiale est possible, mais ne peut être effacée après coup. Cela confirme que
le garde déclaratif et le rendu ne remplacent pas la réception sémantique.

## Studio : fixture initiale rendue utilisable en RPC

Le seed N03 créait un modèle manuel sans ACL. Le contrat exigeait pourtant des
scénarios métier RPC sur ce modèle existant, en conservant ses droits. Le premier
essai termine en 669,15 s (4,707002 USD), avec oracle métier 10/10 et flow complet,
mais reste **non qualifié pour le parcours RPC métier** : sa spécification a réduit
le transport demandé. La QA 13/13 couvre cette spécification rédigée par l’agent ;
les 25 contrôles RPC portent sur la définition et les refus d’accès, les 12
contrôles de calcul passent par ORM superutilisateur. La limite est annoncée,
mais ne justifie pas de qualifier toute la demande. Ce défaut montre aussi que
le garde ne vérifie pas l’exhaustivité du contrat dérivé face à la demande initiale. Le banc initialise désormais une ACL d’utilisateur interne
avec XML-ID stable avant la demande, sans ajouter le champ à réaliser.

Un [préflight indépendant](evidence/studio-preflight/report.json) authentifie
admin uid2 et exécute create/read/write/unlink sur les champs initiaux ; il vérifie
l’ACL et l’absence de l’indicateur demandé. Les sept contrôles, nettoyage inclus,
passent en 34,996 s. Ce préflight ne prouve pas le calcul du futur indicateur.
Le rejeu termine en 526,19 s (3,797781 USD) avec vrai RPC métier9/9 et oracle10/10.
Le parcours natif reste partiel : il prouve deux constructions idempotentes,
puis export/diff, sans deux applications du pack comme demandé. Sa spécification
a de nouveau réduit une obligation. La réponse ne prétend pas avoir exécuté
`apply`, mais le pass du flow ne suffit pas à qualifier toute la demande.

Une [QA externe du pack inchangé](evidence/studio-pack-qa/report.json) ferme le
contrôle concret : premier apply1/0/0, second0/0/1, identifiants stables, droits
inchangés, calcul et dépendances vérifiés par RPC. Les17contrôles passent en27,798s,
sur un Lab neuf ensuite nettoyé. L’artefact est reproductible ; cette intervention
de l’orchestrateur n’est pas attribuée rétroactivement au CLI.

## Autonomie, durées et coûts observés

Le [relevé des dix appels](evidence/costs.json) conserve les coûts cumulés finaux
sans sommer leurs répétitions dans le flux fournisseur. Neuf appels terminés
déclarent **24,7189542 USD** ; le coût du premier appel de reprise interrompu est
inconnu. Le total n’est donc pas calculable. Plafonds CLI configurés : 5 USD pour
chaque consolidation, 12 USD pour chaque parcours complet, maximum92USD configuré.
Ces coûts excluent la session Codex de cette campagne et ses sous-agents, Docker
et la relecture ; aucune estimation de coût complet n’est avancée.

La somme des durées CLI est3947,02s ; les essais ont tourné en partie simultanément,
ce n’est pas la durée murale de la campagne. Modèle orchestrateur demandé opus,
effort medium ; modèle principal observé claude-opus-5, effort effectif non retourné.
L’usage agrégé de la reprise mentionne aussi Sonnet et Haiku : aucune attribution
à un enfant précis sans preuve. Les cas et charges diffèrent ; gain de vitesse,
coût relatif séquentiel/parallèle et taux de fiabilité global restent non établis.

Zéro sollicitation humaine après autorisation. Interventions du banc consignées :
erreur d’oracle RPC, montage Chrome, fixture ACL, gel des entrées restauration,
coupure/drainage/contrôle des processus et QA externe du pack. Les réponses natives
et leur notation ne sont pas corrigées après coup. Aucun autre appel LLM au-delà
des dix prévus ; les contrôles déterministes et Odoo n’appellent pas de fournisseur.

## Décisions de livraison

Les trois lanceurs droits/restauration/versions sont des outils de qualification
réutilisables. Ils ne sont pas lancés par la CI et ne font aucun appel LLM.
Le rendu `qa-report` et son usage ciblé sont adoptés ; le seed Studio corrigé et
les oracles/archives du banc sont livrés avec leurs contre-épreuves. Le superviseur
de reprise reste expérimental et archivé avec ses chemins de campagne ; il ne
constitue pas une reprise automatique générale du runner natif.

La délégation et la production de corrections sur copie peuvent être exercées
avec ces contrôles. Une réception indépendante doit encore confronter demande,
spécification, preuves et mémoire avant livraison : les erreurs de portée et les
récits libres observés ne permettent pas de qualifier une autonomie générale.
Les prochains investissements justifiés sont cette fidélité de bout en bout,
la reprise avec données non vides et les parcours/séries encore non mesurés.
La présente campagne est close par ce bilan borné ; ces suites ne sont pas lancées
implicitement à chaque usage du dispositif.

Les [revues des lanceurs et archives](evidence/tooling-review.md) n’ont trouvé
aucun faux vert dans les résultats retenus. Elles précisent aussi les limites
mécaniques : le booléen global du mutant droits doit être lu avec les fuites
réellement observées ; le contrôle d’import autorisé ne compare pas exhaustivement
tous les champs. La restauration exige de lire le bloc nettoyage et le code de
sortie, en plus de son statut de scénario. Les sources privilégiées des audits
ne sont jamais assimilées à des actions de l’utilisateur limité.

## Limites transversales

- Aucun client ni production ; aucune comptabilité, facturation, paiement ou migration client qualifiés.
- Pas de compatibilité globale 18/19 : seuls les scénarios explicitement exécutés sont couverts.
- Les attestations Markdown vérifiées par empreinte ne deviennent pas des preuves sémantiques.
- La sécurité serveur, la restauration et le navigateur ont des témoins écrits par le banc ; leur réussite n’est pas une mesure de conception autonome par un LLM.
- Le pont Odoo sérialise ses opérations, même lorsque plusieurs agents sont actifs.
- Pas de comparaison causale séquentiel/parallèle : les scénarios et charges diffèrent, les répétitions sont insuffisantes.
- Ni clôture complète de release, ni déploiement, ni reprise après perte de disque ne sont qualifiés par cette campagne.

## Reproduction et intégrité

Les fixtures et les oracles sont dans `benchmarks/qualification/`. Les lanceurs
acceptent un dossier de sortie neuf et créent uniquement leurs ressources
synthétiques. Les protocoles, identités, réponses et journaux originaux sont
conservés sous `evidence/`. Les états initiaux rouges restent visibles ; aucune
réponse du modèle n’est corrigée après génération. Les flux bruts fournisseur
et les homes d’authentification restent hors publication.

## Validation et livraison du dispositif

Les contrôles locaux finaux passent : **161 tests**, graphe valide, lint ciblé,
validation du skill, builds isolé puis actif et parité des26fichiers/deuxblocs/
pointeur. Le [relevé de validation](evidence/validation/result.json) identifie les
sources vérifiées et les journaux. Les profils sont installés à partir des rôles
canoniques ; la publication sur main et sa CI sont vérifiées lors de la livraison.
Les défauts natifs conservés dans ce bilan ne sont pas des corrections client
livrées : aucun code ni pack de cette campagne n’est déployé chez un client.
