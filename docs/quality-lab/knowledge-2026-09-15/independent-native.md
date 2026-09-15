# Réception indépendante de quatre réponses natives

Lecture indépendante le 2026-09-15. Seuls les quatre `work/result.json`, les pièces de leurs `work/` et leurs `raw.jsonl` ont été consultés. Aucun oracle ni `results.json` du banc consulté. Aucun dossier home ou secret ouvert. Aucun dépôt ni réponse modifié, aucun appel modèle supplémentaire.

## Verdict

| Réponse | Verdict | Motif |
|---|---|---|
| K01-codex | Acceptée | Règle préservée ; absence de report attesté distinguée explicitement d’un statut prêt/exécuté. |
| K01-claude | Refusée | `task_deferred=true` et suspension de T02 inventées à partir d’une passation seule. |
| K06-codex | Acceptée | Règle, arbitrage, report explicite du plan et absence de preuve de déploiement fidèles. |
| K06-claude | Acceptée avec réserves | État présent correct ; prescription finale de levée du report trop restrictive et schéma de décision confondu. |

Ainsi : deux réponses acceptées sans réserve, une avec réserves et une refusée. Les quatre identifient correctement la règle, le caractère non confirmé de la proposition et l’absence de déploiement vérifié. Ces trois booléens/énumérations seuls ne suffisent pas à recevoir l’ensemble des explications.

## Confrontation aux pièces brutes

### K01, deux fournisseurs

Le XLSX original contient uniquement les trois entrées XML de classeur/relations/feuille. `Livraison!B9` dit exactement : « Les livraisons inter-sociétés ne doivent jamais être regroupées. » `arbitrage.md` valide l’accord 2025 et retient cette exception. Le statut `reference` du catalogue n’a pas été utilisé seul comme autorisation métier. `proposition.md` qualifie explicitement la suppression des exceptions de non arbitrée ; D2 est `proposed` avec réalisation `not_started`. K1 est une découverte `proposed`, pas une décision confirmée.

Aucun `plan.json`, reçu ou report de prochaine tâche n’existe. La demande prescrit une passation et interdit le déploiement. Les notes laissent le contrôle de société à définir ; cela justifie de conserver une question technique/fonctionnelle, pas d’affirmer un report enregistré ou une suspension décidée de T02.

- **K01-codex** restitue correctement `exclude_cross_company`, false pour proposition/déploiement. Son `task_deferred=false` est immédiatement défini comme absence de report sourcé, sans prétendre que T02 est prête, exécutée ou reçue. Cette nuance rend la réponse fidèle malgré la pauvreté d’un champ booléen pour un état inconnu.
- **K01-claude** transforme la restriction de mandat « passation seule » et la question de K1 en `task_deferred=true` : « T02 reste […] suspendue […] à l’arbitrage de D2 ». Aucune pièce n’atteste cette suspension, et une proposition de suppression non arbitrée n’annule pas la règle déjà validée. C’est une erreur matérielle sur le statut de tâche. La réponse pourrait dire : statut d’exécution/report non attesté ; une question de périmètre reste à traiter.

Les citations de cellule, notes et arbitrage sont exactes dans les deux réponses. Dans K01-claude, le repère DECISIONS « status / implementation.status » accompagne la citation `status: proposed` ; `implementation.status` vaut en réalité `not_started`, correctement décrit ailleurs. Ce repère gagnerait à être limité au premier champ.

### K06, deux fournisseurs

Le DOCX original ne contient que `word/document.xml`, avec un unique paragraphe : les factures comptabilisées de la société B restent figées même après changement de tarif. D1 est confirmée par un responsable métier synthétique et sourcée par ce DOCX et `arbitrage.md`. D2 reste proposée. Le plan indique explicitement T03, titre « Uniformisation », avec `deferred.reason = "Arbitrage non reçu"`. Notes et réalisations ne fournissent aucune preuve de test ni déploiement.

- **K06-codex** restitue cet état sans le confondre avec une inspection d’un environnement distant. Les repères `K1.statement (L6)` et `plan.tasks[0].deferred.reason (L18)` sont exacts. L’accord préexistant ne lève pas automatiquement le report : conclusion conforme au plan inchangé.
- **K06-claude** restitue correctement les quatre champs et les citations. Deux réserves dans l’explication :
  1. « Lever le report exige […] D2 […] qui remplacerait explicitement D1 » présente comme seule voie une décision future qui n’est pas imposée par les pièces. Un arbitrage peut conserver D1 et rejeter/reformuler D2. Le plan exige un arbitrage reçu, pas nécessairement la suppression de l’exception. De plus, `reviewed_by`/`review` décrivent une contribution acceptée, alors que D2 appartient ici à DECISIONS.json : la marche à suivre mélange les schémas.
  2. La possibilité d’une « révision masquée » est répétée alors que l’original XML complet a été lu et ne contient aucune révision, commentaire ou en-tête. C’est une réserve générale non applicable à cette pièce minimale, pas un défaut de la règle identifiée.

La formulation « dépend de D2 » est une interprétation métier plausible du titre Uniformisation, de la proposition et du motif du report, pas une dépendance de plan démontrée (`depends_on` est vide). Elle devrait rester présentée comme cette interprétation.

## Vérifications réellement exécutées selon raw.jsonl

Les numéros suivants sont les lignes JSONL des traces originales.

- **K01-codex** : documentation KNOWLEDGE lue (7), brief vers context.json (11), contexte (13), verify réussi (15). Tentative openpyxl échouée (17), remplacée par lecture ZIP/XML réussie (19), puis résultat écrit (21). La revendication de vérification est soutenue par les traces.
- **K01-claude** : hashes calculés (28), tentative `verify /work --release R1` sans `--file` (37), erreur réelle `AttributeError: 'NoneType' object has no attribute 'stat'` (38), show/brief puis lecture XML de l’original (45/47). Aucune nouvelle tentative correcte de verify. Le résultat décrit un `TypeError`, ce qui est inexact ; le context.json artisanal consigne lui l’AttributeError. Les recalculs d’empreintes soutiennent l’intégrité des pièces, mais ne constituent pas une vérification réussie d’un snapshot de passation. Résultat et context.json écrits ensemble (65).
- **K06-codex** : contexte généré (17), mémoire show (19), contexte vérifié (23), original DOCX lu avec recherche de parties complémentaires et révisions (25), résultat écrit (27). La preuve de fraîcheur du contexte est réelle.
- **K06-claude** : KNOWLEDGE lue (19), brief sauvegardé (25), verify mémoire et contexte généré (32), hashes et XML original lus (34), verify contexte (43), résultat écrit (46). La tentative accessoire `odoo_documents --list` (27) emploie un argument non prévu ; cela n’invalide pas les lectures directes et contrôles réussis suivants.

## Changements et intégrité

Les empreintes référencées dans DOCUMENTS.json, DECISIONS.json et K1.json correspondent toutes aux originaux actuels dans chaque work. Les hashes ZIP diffèrent entre fournisseurs ; leur contenu métier XML a été comparé indépendamment et est identique pour un même cas.

Les traces montrent des écritures de `result.json`, `context.json` et, chez Claude, des fichiers temporaires de lecture/extraction. Elles ne montrent aucune modification des décisions, contributions, plan, demandes ou originaux, ni aucune exécution de développement ou déploiement. K01-claude retire/recrée `/tmp/xl_dump` pour extraire le classeur : opération scratch, pas mutation d’une source métier. En l’absence d’un inventaire antérieur complet, cette conclusion porte sur les actions tracées et les sources hashées contrôlées, pas sur une certification générale du système de fichiers.

## Artifacts de cette réception

- `independent-verdict.json` : verdict structuré figé avant toute consultation d’oracle.
- `commands-observed.json` : commandes pertinentes extraites des traces avec numéro de ligne.
- `input-hashes.json` : empreintes des fichiers work lus lors de cette réception.

Aucune action corrective n’a été exécutée sur les réponses.
