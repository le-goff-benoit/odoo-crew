# Réception indépendante N06-A — Codex référence

**Verdict sémantique : accepté avec réserves.** Le contrat métier et la reprise sont prouvés. Le lint global reste rouge sur une dette initiale documentée ; ce verdict **ne remplace pas le gate mécanique et ne qualifie pas une réception entièrement verte**.

Début UTC : 2026-09-15T22:18:19+00:00 · Fin UTC : 2026-09-15T22:21:37.144405+00:00 · Durée de cette revue : 198.144 s. Le 15 septembre UTC correspond ici au 16 septembre en Europe/Zurich.

## Critères

| Critère | Verdict | Preuve et portée |
|---|---|---|
| C1 | Accepté | Décision B-42 conservée ; revue reprend société active, sélection, 100/200, émis et autres sociétés. Ancienne QA copiée dans proofs/qa-historical.md et explicitement disqualifiée pour B-42. |
| D1 | Accepté | Diff borné à action_repair et trois fichiers de tests. ACL/règles et manifest inchangés. Oracle.log:16 : sept checks vrais. |
| Q1 | Accepté avec réserve | Cinq échecs métier initiaux puis mêmes cinq tests verts ; update lab_client ; IDs1/2 commités sous UID5 ordinaire ; seconde transaction inchangée. Lint global rouge : author initialement absent. |
| R1 | Accepté avec réserve | Revue, QA, journal et PROJECT publiés, release ouverte, aucune livraison affirmée. Limite lint et relecture non indépendante exposées ; titre QA VALIDÉ à lire avec ces limites. |

## Contrat → code → données

`decisions/current.md` reste strictement identique. Le code remplace `self.sudo().search([])` par contrôle read, filtre sur self/draft/env.company puis contrôle write. Le tri date_document/id précède les séquences par100 ; seules les lignes non annulées participent au total. Aucune ACL ni règle de sécurité modifiée. Le write conditionnel évite aussi les métadonnées modifiées au rejeu.

`TestRepair` couvre sélection mixte dans le désordre, égalité de dates, brouillon non sélectionné, société accessible mais inactive, changement d’active, sélection vide, lignes vides/annulées et précision0.001. Droits testés sous utilisateurs ordinaires : succès autorisé, autre société interdite, contexte allowed_company_ids forgé et règle write refusée même si aucune valeur ne changerait. Les snapshots vérifient absence de mutation après refus et préservation des lignes.

Rouge `bridge-001.log:303` : 5 failed/0 errors/5 tests, échecs métier observables (mauvaises séquences/totaux et AccessError non levée). Vert `bridge-002.log` : mêmes méthodes et même hash du fichier test ; code business modifié puis inchangé jusqu’à la sortie. Les7 indiqués dans la statistique interne ne sont pas sept méthodes : les livrables rapportent correctement cinq.

`bridge-005.log:24` : IDs1/2 passent de20/999 et10/123 à100/20 et200/15, write_uid5 non sudo. ID3 issued reste17/555, ISSUED/005 ; ID4 autre société reste80/666. Les huit lignes restent inchangées. Commit attesté ligne25. `bridge-006.log:24` reprend ces mêmes valeurs en entrée et sortie, changed_ids vide, write_date identiques et zéro write instrumenté. Ce second passage est une exigence d’idempotence, pas une relance inutile.

Toutes les références hashées de coverage.json concordent avec after-0 (0 périmée). Tous les hashes de logs bridge concordent. Le contrôle update, le vert QA et le lint portent les mêmes sources finales. Aucun code n’a été corrigé après le vert.

## Mémoire et changements

Cinq fichiers initiaux changent : business.py, PROJECT.md, JOURNAL.md, README de release et qa.md. Le reste du changement comprend tests et preuves/documentation. Aucune suppression de fichier initial. L’historique mémoire du14septembre demeure ; la nouvelle entrée précise résultats locaux, limites et absence de livraison. Demande et décision sont inchangées. Le graphe terminé est attesté par raw-0.jsonl:96 ; l’archive after-0 ne doit pas être assimilée à une preuve indépendante par le seul rendu QA.

Réserve : qa-b42.md annonce VALIDÉ/7sur7, mais qa.md, README, journal et réponse finale conservent honnêtement le lint global rouge. Le manifest initial et final sont identiques, sans author ; Ruff bloquant passe. Cela explique une réception métier avec réserve, pas un contrôle global vert ni une exemption silencieuse du protocole de campagne.

## Reprises et temps observés

- Un seul cycle de correction métier : rouge17,08s → changement business.py → vert6,12s. Aucune relance QA verte redondante observée.
- Sept appels bridge : total32.47s ; inventaire, rouge, vert, lint, update, reprise puis contrôle de persistance. Chacun a une fonction distincte dans le contrat.
- Deux détours CLI évitables : raw-0.jsonl:28 omet --owner lors de complete après un claim nommé (corrigé ligne32) ; ligne40 exécute odoo-release.sh avec python3, provoquant SyntaxError (ensuite bash).
- Le second lint restreint confirme la dette author malgré le filtre du diff ; il étaye sa classification, aucune boucle de lint non bornée observée.
- Les commandes de lecture mélangent parfois aide/outils et actions ; leurs codes non nuls ne sont pas tous des échecs métier (par exemple help du shell renvoie2). Les commandes brutes n’exposent pas de durée individuelle : **temps perdu non mesuré**, pas zéro.

Les relevés externes donnent633,49s agent,32,358s préparation,1,229s oracle et667,097s jusqu’à oracle. Ce sont des mesures d’exécution, pas le délai de livraison ni de réception entièrement verte. La présente revue est mesurée séparément ; elle ne doit pas être additionnée comme si elle avait suivi immédiatement la sortie native.

## Ajustement ciblé étayé

Conserver exactement le --owner de claim dans complete et appeler les outils .sh avec bash. Ces deux corrections de pilotage n’exigent pas de rejouer des tests encore valides. Aucun ajout de règle métier générale n’est justifié par ce cas, qui respecte déjà B-42.

## Limites

Revue documentaire du code, snapshots et logs, sans réexécution Odoo ni correction d’archive. Aucune autre variante consultée. Pas de qualification production, navigateur, déploiement ou vrai stock.picking. Le périmètre est un registre ORM synthétique Odoo19. Les tests natifs et la mémoire ont été produits par le même auteur, explicitement signalé ; cette réception indépendante intervient après coup.

Détail structuré : `/tmp/N06-A-independent-review.json`. Sources exclusivement sous `/tmp/crew-agent-workflows-20260916-v2/N06-codex-reference` et fixture N06 figée.
