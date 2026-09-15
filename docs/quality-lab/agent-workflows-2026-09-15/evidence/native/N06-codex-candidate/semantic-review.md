# Réception indépendante N06 — Codex candidat

**Verdict : accepté avec réserves.** Aucun critère métier critique manquant. La réserve lint global antérieur reste entière ; la réception sémantique ne transforme pas le gate mécanique en succès.

Début UTC : 2026-09-15T22:39:29+00:00 · Fin UTC : 2026-09-15T22:42:26.613388+00:00 · Revue : **177.613 s**. Date locale : 16 septembre Europe/Zurich.

## C1 / D1 / Q1 / R1

| Critère | Verdict | Constat |
|---|---|---|
| C1 | Accepté | B-42 et demande inchangés. Revue conforme, aucun arbitrage rouvert ; ancienne QA limitée à une création vide, conservée dans qa-before.md et non réutilisée comme preuve courante. |
| D1 | Accepté | action_repair filtre self/draft/env.company, trie date/id, applique 100/200 et exclut cancelled ; états émis, autres sociétés et lignes préservés. ACL/règles/manifest inchangés. Oracle : sept checks vrais. |
| Q1 | Accepté avec réserves | Six tests rouges puis mêmes six verts ; update et état installed ; droits ordinaires et reprise persistée ; rejeu sans write. Lint global rouge antérieur et reçu update mal qualifié, mais preuves réelles conservées. |
| R1 | Accepté avec réserves | Revue, QA, PROJECT/JOURNAL publiés avec historique et limites, release ouverte, aucune livraison. Auto-relecture annoncée. Incidents initiaux explicitement séparés des contrôles réussis. |

## Fidélité et portée réelle

`lab_register/models/business.py:17` remplace le search global sudo par contrôle read, filtre métier puis contrôle collectif write. Aucun changement de droits. Les six méthodes `tests/test_repair.py` couvrent la sélection mixte/incomplète/vide, égalité de dates départagée par id, changement de société active, issued/autres sociétés, lignes annulées/vides, petit delta non arrondi, refus write atomique, refus read et ACL utilisateur public. Le sixième test n’est pas en soi une preuve de couverture supérieure : ce sont les scénarios et postconditions lus qui comptent.

Les commandes capturées via evidence sont attestées dans `raw-0.jsonl:46` (rouge) et `:52` (vert), chemins distincts, même classe et mêmes tests. Le rouge correspond au business.py initial ; le vert et ses sources correspondent au module final. Aucun changement de module après le vert. Les compteurs bruts indiquent six échecs métier puis zéro échec/erreur, six méthodes ; les hooks ne sont pas présentés comme tests fonctionnels supplémentaires.

Sur la copie existante : `bridge-004.log` établit l’update. `copy-rights.py` confirme installed, réalise succès sous utilisateur ordinaire multi-société et refus read/write, vérifie les postconditions puis rollback complet des données, utilisateur et règle temporaires (`bridge-006.log:33`, COPY_RIGHTS_PASS). La reprise persistée est ensuite un vrai RPC sur [2,1] avec allowed_company_ids=[1], retour true (`bridge-008.log:1`). Elle n’est pas confondue avec le scénario transactionnel ordinaire.

`verify-repair.py` relit dans une autre transaction : ids 1/2 = 100/20 et 200/15, autres champs métier inchangés ; id 3 issued = 17/555/ISSUED/005, id 4 autre société = 80/666/OTHER/DRAFT, huit lignes strictement identiques. L’espion write transmettrait une écriture réelle ; aucune appelée au rejeu, valeurs et métadonnées stables (`bridge-009.log:16`). L’oracle indépendant conserve sept invariants vrais (`oracle.log:16`).

## Réserves sans faux reçu

- `lint.json` est rouge sur author absent avant intervention ; QA, réponse, README et mémoire le disent. Ruff bloquant et diff conformes ne valent pas lint global vert.
- `update.json` est `failed` avec exit_code=0 parce que --module demande un bilan de tests absent d’un update. Le candidat conserve ce fichier tel quel et établit l’update par log réel/exit0/installed ; il ne fabrique pas un reçu passed ni ne rejoue l’update pour maquiller ce résultat. C’est une mauvaise sélection d’option de preuve, pas un échec de mise à niveau démontré.
- `copy-rights.json/log` conserve le FileNotFoundError avant mutation ; v2 prouve l’exécution corrigée. `repair-first.json/log` conserve le Fault RPC, tandis que repair-authorized et repair-verified attestent seuls la reprise réussie. Les droits du compte n’ont pas été élargis.
- La relecture native est explicitement du même auteur. Cette revue indépendante est postérieure et documentaire.

## Intégrité et mémoire

Toutes les références de coverage.json correspondent aux fichiers actuels, aucun hash périmé. Tous les logs bridge concordent avec leurs empreintes. La demande, la décision, le manifest et les deux fichiers de sécurité sont inchangés ; modifications des fichiers initiaux limitées à business.py, QA/README de release, PROJECT/JOURNAL. Les nouveaux fichiers portent tests et preuves/documentation. La mémoire conserve l’historique et distingue règle métier, réparation locale, incident RPC et absence de livraison.

## Reprises prouvées

Un cycle rouge → correctif → vert, **aucune relance QA verte inutile**. Rouge : 16,61 s ; vert : 6,75 s. Dix appels bridge, total 40.58 s.

Deux incidents de transport évitables : accès à `/work/.../before.json` depuis le conteneur non monté (bridge-005, 1,36 s), puis contexte RPC demandant une société non autorisée (bridge-007, 2,46 s). Les répétitions qui suivent sont nécessaires pour achever ces contrôles corrigés. Ces deux appels échoués représentent **3,82 s de bridge seulement** ; coût de diagnostic/rédaction et temps total perdu inconnus.

Autres détours : --owner omis à complete (raw-0:26) et --module appliqué à update (raw-0:61). Les deux lints ont des portées globale puis diff ; leur lecture de dette est justifiée, aucune nouvelle règle de suppression du lint proposée. Le rejeu final répond au contrat d’idempotence.

## Comparaison de qualité et limites

La même grille confirme les critères métier et maintient la réserve lint antérieure. La capture rouge/vert est correctement exécutée avant la réception, sous fichiers séparés ; les preuves fraîches sont réutilisées. Les incidents de transport et le reçu update mal qualifié restent visibles : aucune préférence accordée au candidat, aucun gain temporel conclu ici.

Aucune réexécution Odoo, aucune correction d’archive, aucune autre variante consultée pendant cette revue. Les contenus/hashs sont contrôlés ; le vérificateur absolu /work et les permissions originales ne sont pas rejoués sur les snapshots normalisés. Pas de qualification navigateur, production, livraison ni autre série.

Ajustements ciblés étayés : réserver --module aux exécutions avec tests ; transmettre au shell du pont les données dont il a besoin sans supposer /work monté ; vérifier les sociétés du compte RPC sans les élargir ; conserver le propriétaire claim/complete. Détails structurés dans `/tmp/N06-codex-candidate-independent-review.json`.
