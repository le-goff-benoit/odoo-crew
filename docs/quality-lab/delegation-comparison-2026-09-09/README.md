# Déléguer quand cela aide ; parler clairement au chef de projet

Les six essais sont acceptés. Sur le seul cas où un sous-agent a réellement
été utilisé, la délégation prend **19 % de temps en plus et environ deux fois
plus de jetons**, sans différence de note de qualité. Nous conservons donc le
choix de déléguer au cas par cas. Cette campagne ne justifie pas une délégation
systématique ni une promesse de gain sur tous les projets.

Le retour sur le langage est traduit en une **consigne commune installée dans
les profils Claude et Codex** : résultat ou blocage, conséquence métier,
prochaine action et responsable ; une décision nécessaire est accompagnée des
choix, conséquences et recommandation. Une question technique garde sa précision.
Les trois essais de communication réussissent avec les anciennes comme avec les
nouvelles consignes : c’est une préférence désormais explicite, **pas un gain de
qualité démontré**. La prochaine vérification utile est le retour d’un chef de
projet sur les échanges réels, notamment les questions de décision.

## Ce qui a été comparé

| Demande | Seul | Délégation possible | Sous-agents réellement utilisés | Qualité reçue |
|---|---:|---:|---:|---:|
| Vérifier qu’un contrôle existe déjà | 1 min 44 ; 170 644 jetons | 2 min 05 ; 211 042 jetons | 0 | 10/10 dans les deux cas |
| Diagnostiquer un montant qui ne se recalcule pas | 2 min 54 ; 275 869 jetons | 3 min 27 ; 571 715 jetons | 1 | 10/10 dans les deux cas |
| Interdire les prix négatifs sans casser la gratuité | 5 min 55 ; 756 542 jetons | 5 min 41 ; 648 684 jetons | 0 | 10/10 dans les deux cas |

Les différences des première et troisième lignes ne mesurent pas l’effet d’une
délégation réelle : les deux agents ont travaillé seuls. Dans le diagnostic,
le sous-agent vérifie le code et les sources pendant que le principal lit le
besoin et prépare la mémoire. Son tour dure 60,487 s ; des appels d’outils du
principal ont lieu pendant cet intervalle. Il n’y a pas de chevauchement entre
deux enfants, puisqu’un seul est lancé. Le principal attend son résultat et
l’intègre. Les observations ne mesurent pas une activité de calcul continue.

La communication des six comptes rendus obtient 8/8 sur les quatre critères
applicables. Aucun arbitrage humain n’y était nécessaire : la qualité des
questions n’est donc pas mesurée par ces six essais. Les réserves du relecteur
restent dans sa [synthèse initiale](evidence/audit/reviews/synthesis.md), notamment
la visibilité du contournement dans les diagnostics et la portée exacte des
champs conservés. Une note maximale sur cette grille n’est pas une garantie
d’exhaustivité sur d’autres demandes.

## Réception et preuves réelles

- **36 obligations métier relues**, 156 contrôles de réception satisfaits au total.
  Les sources déterminantes, décisions initiales et mémoires proposées sont
  confrontées aux entrées ; les journaux restent en ajout strict.
- Les deux correctifs exécutent d’abord leurs tests sur le code initial : rouge
  attendu, puis vert après correction, avec **15 et 14 méthodes** respectivement.
  Ce rouge préparatoire n’est pas une reprise après correctif raté. Aucune
  correction supplémentaire n’a été demandée après réception.
- L’oracle indépendant, écrit avant les essais et ajouté seulement à des copies
  d’évaluation après gel des sorties, passe ses **5 méthodes sur chaque correctif**.
  Suites complètes de réception : 20 et 19 méthodes, sans échec ni saut.
- Les trois lignes initiales sont conservées dans chaque base sur les champs
  inventoriés : identifiant, nom, état, quantité, prix, montant. Le gabarit reste
  inchangé. Cela ne prouve pas toutes les métadonnées, par exemple `write_date`.
- Les lints prescrits passent. Dans chaque essai de développement, une recherche
  complémentaire de détails Ruff sur l’hôte échoue faute de binaire ; le lint
  avait utilisé son mécanisme de repli avec succès. Les incidents restent archivés.
- Le réseau, PostgreSQL et les conteneurs synthétiques de campagne sont nettoyés ;
  l’absence de ressource restante du propriétaire est vérifiée.

[Réception finale et arbitrages](evidence/reception.json) ·
[Verdicts par essai](evidence/verdicts/summary.json) ·
[Contrôles Odoo indépendants](evidence/runtime-audit/E03-S/attestation.json) ·
[Nettoyage](evidence/environment/evidence/cleanup.json).

## Consigne de communication adoptée

La source est [roles/communication.md](../../../roles/communication.md).
`build.sh` l’intègre aux corps des 13 profils/commandes/skills, dans les 26 sorties
Claude/Codex. Le contrôle de génération refuse une distribution périmée si cette
source commune change. Les définitions de rôle et les protections métier restent
portées par leurs sources habituelles.

L’essai distinct compare les rôles de référence à ces mêmes rôles accompagnés de
la consigne. Deux contextes neufs traitent trois demandes figées avant lancement :
une décision sur 42 commandes existantes, un correctif dont le contrôle des droits
reste à faire, puis une question destinée explicitement à un développeur. Ce
dernier cas sert de contre-épreuve à une simplification excessive ; il n’a pas
servi à ajuster la consigne. Aucune révision n’est effectuée après observation.

Le relecteur indépendant attribue **30/30 à chaque ensemble**, sans faux succès,
blocage effacé ou autorisation inventée. L’adoption formalise la préférence
explicite de l’utilisateur avec une non-régression bornée. Elle ne démontre pas
une meilleure lisibilité en situation réelle ; les questions purement factuelles
manquantes n’ont pas fait l’objet d’un essai distinct.

[Retour original](JOURNAL.md) ·
[Revue de communication](evidence/pm-style/audit/reviews/verdict.md) ·
[Décision d’adoption](evidence/pm-style/decision.json).

## Protocole, mesure et limites

Référence : `f6ea0b6851df5269dbec151bbdebe337d67707e8`. Ordre figé : E01-S,
E01-D, E02-D, E02-S, E03-S, E03-D. Budgets respectifs : 10, 12 et 20 minutes,
identiques dans chaque paire. D permet zéro, un ou deux enfants, sans petits-enfants.
Les six arbres de participants sont exécutés successivement, sans audit ou test
concurrent extérieur. Le modèle/effort observé dans les sept threads primaires
est `gpt-6-astra/high`, sans override. Aucun appel modèle par CLI.

Entrées publiques, rôles et conditions identiques dans chaque paire, sauf chemins
propres et permission de déléguer. Une même préférence de communication est
appliquée aux deux variantes avant gel. Les profils canoniques ne sont modifiés
qu’après les six sorties primaires. E03 n’a pas servi à ajuster la politique avant
son exécution ; il ne sera plus un cas inédit pour une future campagne.

Les deux bases Odoo 19.0 sont clonées depuis le même gabarit PostgreSQL par
`CREATE DATABASE ... TEMPLATE`, et non par restauration de sauvegarde dans cette
campagne. Images immuables et empreinte sémantique initiale identiques, trois
lignes synthétiques ; aucun client ni production. Cette comparaison de rôles et
d’exécution ne certifie pas toute une chaîne `/odoo-new`, une release complète,
une autre série ou un autre fournisseur.

Le temps va du début natif du participant à la fin de tous ses enfants. Départ de
coordination et collecte sont conservés séparément. Les jetons sont le dernier
compteur cumulatif de chaque thread, additionné une seule fois ; cache et
raisonnement sont des sous-ensembles, jamais ajoutés au total. Les six essais
consomment **2 634 496 jetons, dont 2 420 096 d’entrée en cache** ; somme des durées
primaires : 1 306,804 s. Aucune conversion monétaire n’est déduite.

Les coûts annexes sont séparés : préparation par trois agents, 1 711 439 jetons ;
deux revues communes, 1 109 254 ; exercice de communication, 329 510. Les
[métadonnées auxiliaires](evidence/auxiliary-native/metrics.json) donnent les tours
et durées ; leur somme n’est pas un temps écoulé global en cas de parallélisme.
Le travail de coordination du principal couvre plusieurs campagnes dans la même
conversation et n’est pas attribuable exactement : il n’est pas compté comme zéro.
La préparation Docker et les réceptions ont leurs propres journaux horodatés.

Le jugement commence avec des labels opaques, sans métriques ni traces natives.
Certains textes et chemins révèlent leur identifiant initial : masquage imparfait.
Les paramètres chiffrés de certaines passations natives ne permettent pas de
certifier l’exposition complète aux consignes. Les exports primaires excluent
messages entrants et raisonnement ; les exports auxiliaires ne contiennent que
les métadonnées, sans contenu d’outil ni message. Une paire par cas ne démontre
pas un gain causal général.

La condition de gain prédéfinie n’est pas atteinte : E02 est 18,60 % plus lent et
consomme 107,24 % de jetons supplémentaires, au lieu d’au moins 20 % de gain de
temps avec un ratio de jetons ≤ 1,5. **La politique optionnelle existante est
conservée**, sans nouvelle règle de délégation systématique.

## Incidents conservés et livraison

Avant gel, l’oracle utilisait une forme d’assertion incompatible avec le helper
Odoo 19 : corrigé, puis recalibré rouge/vert et sélection vide refusée. Une limite
de threads empêche aussi une réaffectation du concepteur ; le principal écrit
l’instrumentation. Aucun de ces incidents ne compte comme échec candidat.

Après E02-D, le compteur interprète le contexte hérité du parent comme un tour
inachevé de l’enfant. La correction ne touche que la mesure : exclusion du préfixe
hérité à la frontière native du thread, refus si cette frontière manque. Les
exports initiaux, le gel original et l’amendement sont conservés, puis les mêmes
règles corrigées s’appliquent aux six arbres. Cinq tests couvrent ces métriques.

Le relecteur omet initialement `--offline` dans ses briefings et affiche un
inventaire local de bases. Cet écart est déclaré, les métadonnées extérieures ne
sont pas utilisées ni publiées, les briefings sont repris hors ligne. Le renvoi
R3 à `execution-notes.md`, masqué lors de la première revue, est confirmé dans
l’original à la réception ; le verdict initial reste intact.

Validation locale : **198 tests d’outillage**, graphe, calibration de réception
**28/28**, build isolé puis actif, parité **26 fichiers + 2 blocs et pointeur**,
validation de structure des **13 skills**. La calibration déterministe entre en
CI sans appel modèle ni Odoo. Les contrôles GitHub de la révision publiée restent
consultables dans le workflow « Qualité du dispositif Odoo ».

Le [registre des preuves](EVIDENCE.json) contient les empreintes relatives des
artefacts et sources du banc. Les chemins absolus des journaux sont ceux de
l’exécution historique ; `materialize.py` et `runtime.py` préparent de nouveaux
espaces pour un rejeu. Aucune sortie candidate n’est corrigée rétroactivement.
