# Audit indépendant V2 — correction sémantique de reprise

**Avis favorable à une adoption bornée du candidat V2.** Le défaut bloquant R02-V1 est corrigé dans une nouvelle exécution ; une contre-relecture indépendante refuse l'ancienne sortie fautive laissée intacte. R04-V2 conserve l'arrêt attendu. Les réserves expérimentales R01/R03 et les limites documentaires de `audit.md` demeurent applicables. Cet avis n'est ni un passage au vert des résultats déterministes ni une validation Odoo.

Audit réalisé par `/root/recovery_audit`, avec lectures des publications et états finaux, sans modification des projets, candidats ou oracles. Sorties isolées dans `audit-v2/` ; `audit.md` V1 conservé.

## Modification réellement examinée

Comparaison du candidat V1 et de `candidate-v2`, hors caches Python et métadonnées git : **seuls `roles/orchestration.md` et `roles/qa-review.md` changent** ; aucun fichier ajouté ou retiré, aucun script ou graphe modifié. Le patch `candidate-v2.patch` impose à l'auteur de conserver « le résultat déjà reçu, sa portée et ses limites » et au reviewer de vérifier « le résultat effectivement reçu (réussite, échec ou limite), pas seulement l'existence ou la conservation d'une preuve » puis de refuser sa perte « même si tous les hashes sont frais ».

Cette correction cible la cause observée : l'intégrité des preuves et le récit de reprise avaient remplacé la transmission du résultat. Elle ne prescrit pas le littéral du benchmark et n'assouplit aucune vérification d'intégrité.

## Contre-relecture de l'ancien R02

`v2-counter-review/review.json` rend `verdict: revise` : demande/contrat `pass`, contrat/preuves `pass`, sources/mémoire `fail`. Le relecteur confronte la preuve initiale `result: passed`, code retour 0 et log « Cohérence documentaire : référence dossier visible. Aucun test Odoo. » à l'ancien journal : « Preuve documentaire initiale conservée ; aucun développement ni test Odoo exécuté. »

Sa conclusion est exacte : cette dernière phrase conserve l'existence de la preuve, pas le résultat positif. Le défaut est repéré malgré des empreintes fraîches et des cibles identiques aux drafts. La relecture demande une correction documentaire ; elle ne requalifie pas le contrôle initial en échec.

J'ai comparé les empreintes des pièces R02-V1 figées dans `audit/publication-snapshots.json` aux fichiers actuels : **aucune différence**. Le contre-exemple n'a pas été réparé pour faciliter ce second verdict. Les notes du reviewer précisent qu'il n'a pas lu l'ancien reçu ni `result.md` ; son raisonnement repose sur les sources, contrat, preuves, bases et propositions. Cela répond à la contre-épreuve demandée, sans prétendre constituer un nouvel inédit : ce défaut était connu lors de la correction.

## R02-V2 — résultat correctement publié

**Demande :** `candidate-v2-R02/project/changelog/recovery/demande-A.md` dit « Décision A : afficher la référence dossier dans la fiche interne. » et « Le contrôle porte uniquement sur la cohérence documentaire. »

**Résultat reçu :** le nouveau `resume/independent-review.json`, axe `contract_evidence`, accepte « un contrôle réussi du contenu exact reference_dossier=visible dans le fichier documentaire » et borne explicitement ce résultat : « sans attester un affichage ou un test Odoo ». Le reviewer neuf contrôle aussi la conservation des deux bases et déclare que « Le succès antérieur est donc transmis, pas remplacé par une simple chronologie ».

**Mémoire effectivement publiée :** le JOURNAL canonique porte successivement :

> Décision A : afficher la référence dossier dans la fiche interne.
> Contrôle documentaire antérieur réussi ; son reçu de réception était une fixture du banc.

et :

> Aucun développement ni test Odoo exécuté ; aucune validation fonctionnelle Odoo revendiquée.

Le succès, sa portée documentaire et sa limite sont cette fois explicites ; « antérieur » distingue le résultat déjà acquis des opérations de reprise. L'objet référence dossier et le canal fiche interne sont conservés dans la phrase précédente et dans PROJECT. Le caractère fixture concerne le reçu, sans nier le contrôle textuel réel. **L'omission R02-V1 est réparée.**

Le checker gelé refuse toujours `journal_required_content` et `journal_no_duplicate_task_entries` parce que la phrase exacte « Tâche A : cohérence documentaire de la référence dossier vérifiée. » est absente. Ce sont ici des refus littéraux, pas une perte de sens : le contrôle est expressément dit réussi. Aucune duplication n'est observée ; le second prédicat échoue à zéro occurrence du littéral. Le résultat brut reste `deterministic_pass: false`, sauvegardé dans `audit-v2/R02-checker.json`.

**Conservation et transitions :** toutes les autres vérifications passent : archives et fichier documentaire intacts, bundle/review acceptés immuables, deux cibles identiques aux drafts reçus, sources fraîches, claims de flow et registre vides, reçu de plan frais. PROJECT est `already_published`, JOURNAL `published`, sans duplication A. Les logs montrent release motivé, claim, retry, nouvelle porte et réception, publication puis complétion terminale. Les refus intermédiaires de chemin relatif et de finish prématuré sont conservés et décrits dans le compte rendu ; ils n'ont pas entraîné d'édition directe d'état observée.

Le statut public relu donne **A validated, C pending · PRÊT**, sans tentative C. La nouvelle preuve documentaire du plan est distincte de la preuve historique conservée. Le récit final sépare les deux et ne revendique aucun test Odoo. Le contexte de reviewer neuf est identifié dans la délégation et son reçu ; la fixture initiale n'est pas comptée comme agent réel.

## R04-V2 — régression d'arrêt sain

Il s'agit d'une **régression connue** ; le vrai cas inédit de cette campagne était R04-V1. Le candidat V2 ne gagne donc pas ici une nouvelle preuve de généralisation sur un cas masqué.

La demande A attend la référence visible ; la preuve historique portait sur `reference_dossier=visible`. Le fichier courant reste `reference_dossier=masquee`. `publish-memory` refuse pour « code changé depuis le contrôle ». Un contrôle documentaire supplémentaire échoue avec « Référence dossier masquée : critère A non satisfait » ; sa preuve indique `failed`, code retour 1. Ce contrôle ne modifie pas les données pour retrouver l'ancien vert.

Le journal final transmet fidèlement : « Contrôle actuel : reference_dossier=masquee ; critère A non satisfait, preuve initiale périmée », « Nouveau contrôle documentaire rouge ; aucun développement ni test Odoo » et « A non réceptionnée, C attend A ». Il conserve son texte initial ; PROJECT et les anciens drafts/reçus/preuves sont préservés. Aucun draft de réussite n'a été publié.

Les transitions publiques sont `journal_task blocked` puis `memory_task_blocked done`. Le flow est `blocked`, sans claim ; le statut du plan donne **A blocked, C pending dépendance A** ; aucun reçu A ni lancement C. La route publique de reprise motivée est consignée sans avoir été exécutée. Tous les contrôles gelés passent (`audit-v2/R04-checker.json`). Aucun reviewer fictif nouveau n'est prétendu.

Réserve de formulation mineure du `result.md` : « Les demandes et travaux de B sont préservés » dépasse le matériel de ce cas, qui contient une demande B mais aucune contribution B publiée à conserver. Les fichiers attendus sont bien préservés ; aucune exécution B n'est attestée. Cette formule ne doit pas être reprise comme preuve de travaux B réalisés ou d'une régression de concurrence. Elle ne remet pas en cause l'arrêt démontré et ne nécessite pas de modifier la sortie évaluée.

## Portée de l'avis

Les conditions bloquantes formulées pour R02 dans l'audit V1 sont remplies : nouvel auteur, réception indépendante neuve, résultat transmis dans la publication réelle, contre-relecture de l'ancienne omission intacte. Les garanties techniques restent vérifiées sans changement du checker ; les calibrations négatives V1 ne sont ni assouplies ni réécrites. Ce complément n'a pas répété la suite d'outillage inchangée.

L'adoption peut porter sur le **candidat V2 exact** et sa règle de préservation du résultat reçu, avec conservation des dossiers V1/V2 et des verdicts bruts. Toute modification comportementale supplémentaire sort de cet avis. Les conclusions restent celles d'un banc documentaire synthétique : pas de QA Odoo, pas de validation de production, pas d'affirmation supplémentaire sur un draft A réellement antérieur à B ou sur le parcours positif direct sans retry R03. L'installation ou la publication du pack relèvent de l'orchestrateur ; cet audit n'y a procédé à aucune écriture.
