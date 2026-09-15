# Réception indépendante — N07 Codex candidat

**Verdict : accepté avec réserves (`accepted_with_reservations`).** Aucun critère métier critique manquant. Ce verdict ne transforme pas le lint rouge en vert.

Début UTC : 2026-09-15T22:49:47+00:00. Fin UTC : 2026-09-15T22:54:28.309724+00:00. Revue : **281.31 s**, lectures, analyse et rédaction incluses. Aucune réexécution Odoo, aucune autre variante consultée.

## Critères

- **C1 — accepted** : N-17 respectée sans réarbitrage : modèle synthétique, exclusivité draft automatique, zéro manuel valide, réinitialisation copie et reliquat exact ; ancienne QA conservée dans sa portée limitée. Sources : `changelog/2026-09-15_01_repair/revue_fonctionnelle.md`; `changelog/2026-09-15_01_repair/qa.md:1`; `.odoo-agents/PROJECT.md:8`.
- **D1 — accepted** : Implémentation et neuf tests couvrent manuels zéro/partiel, done, copy puis cron, reliquat puis cron, absence de création à reste nul/négatif, fractions, singleton et idempotence. Oracle ORM indépendant : 12 invariants vrais. Aucun écart métier critique observé. Sources : `lab_preparation/models/business.py:9`; `lab_preparation/models/business.py:19`; `lab_preparation/models/business.py:24`; `lab_preparation/models/business.py:43`; `lab_preparation/tests/test_preparation.py:8`; `lab_preparation/tests/test_preparation.py:46`; `lab_preparation/tests/test_preparation.py:65`; `lab_preparation/tests/test_preparation.py:91`; `oracle.log:LAB_ORACLE`.
- **Q1 — accepted_with_reservations** : Rouge réel avant correction (14 assertions échouées, 9 méthodes), vert final (9/0/0), update réel sortie 0. Reprise committée : seul ID1 passe 999 à 7, trois lignes protégées inchangées ; nouveau processus confirme persistance et rejeu sans mutation de champ ni création. Réserves distinctes : lint rouge antérieur et reçu update mal classé failed. Sources : `bridge-events.json`; `changelog/2026-09-15_01_repair/preuves/tests-rouge.json`; `changelog/2026-09-15_01_repair/preuves/tests-vert.json`; `changelog/2026-09-15_01_repair/preuves/update.json`; `changelog/2026-09-15_01_repair/preuves/update.log:17`; `changelog/2026-09-15_01_repair/preuves/reprise.py:37`; `changelog/2026-09-15_01_repair/preuves/reprise.log:15`; `changelog/2026-09-15_01_repair/preuves/rejeu.py:8`; `changelog/2026-09-15_01_repair/preuves/rejeu.log:16`; `changelog/2026-09-15_01_repair/preuves/lint.log:11`.
- **R1 — accepted_with_reservations** : Revue, QA renforcée, journal et mémoire mis à jour fidèlement ; auto-relecture explicitée, release ouverte et aucun déploiement revendiqué. Le titre QA VALIDÉ et 7/7 ne constituent pas une suite entièrement verte ; les réserves sont toutefois conservées dans les documents et mémoire. Sources : `changelog/2026-09-15_01_repair/preuves/reception.md:3`; `changelog/2026-09-15_01_repair/qa.md:11`; `changelog/2026-09-15_01_repair/qa-n17.md:1`; `.odoo-agents/JOURNAL.md:7`; `.odoo-agents/PROJECT.md:15`; `answer-0.md`.

## Preuves et réserves

- author absent du manifest initial et final, identiques octet pour octet. Ruff vert ; lint complet et contrôles Odoo ciblés échouent sur ce seul défaut. Dette prouvée, pas supposée. Aucun droit de convertir ce contrôle en vert.
- update.json conserve result=failed avec exit_code=0 ; utilisation de --module sur une commande update sans bilan tests. Logs chargement module et bridge attestent update réel. Aucun reçu passed fabriqué ; les documents avertissent correctement.
- qa-n17.md annonce VALIDÉ et 7/7, alors que lint reste rouge. Lire ce pass comme réception métier avec réserves explicites, jamais comme validation intégrale des contrôles. Auto-relecture auteur autorisée par LAB ; cette revue indépendante est uniquement documentaire.

La reprise lit tous les champs, protège intégralement les IDs 2/3/4, committe la modification autorisée de l’ID1, puis le second shell relit les données persistées et vérifie l’égalité complète après cron, write_date compris. Les 4 lignes restent 4. Sources : `preuves/reprise.py`, `reprise.log:15`, `rejeu.py:8`, `rejeu.log:16`.

Les hashes des logs bridge, des sources de la preuve verte et des références de couverture correspondent. Le modèle du reçu rouge correspond au modèle initial figé ; son écart avec le modèle final est attendu. Aucun reçu final périmé observé. Le manifest est strictement identique à la fixture initiale : la dette author est établie.

## Reprises et temps

Sept appels bridge, **34,50 s** cumulées ; deux QA seulement : rouge 15,84 s puis vert 8,22 s. Aucun rerun vert inutile. Le rejeu dans un second processus et le lint ciblé après l’échec global sont justifiés.

Trois détours CLI sont prouvés : propriétaire omis au complete (`raw-0.jsonl:28`, corrigé ligne33), script shell lancé avec Python (ligne42), commande add sur README sans tableau attendu (ligne55, relancée ligne62). Le reçu update mal classé provient en plus du flag --module inadéquat (ligne75), sans relance de l’update. La durée perdue n’est pas isolable : aucune estimation inventée.

Correctifs de consigne ciblés : conserver le même owner entre claim/complete ; invoquer le script .sh avec bash ; vérifier le format attendu du README avant add ; réserver le parseur de bilan tests aux commandes de tests. Aucun de ces constats ne justifie supprimer un contrôle métier.

## Portée

Archive synthétique N-17 seulement. Neuf méthodes, douze invariants ORM de l’oracle verts. Ni planning ir.cron livré, ni modèle stock.picking, ni recette complète, ni déploiement. L’auto-relecture auteur est explicitée ; la présente réception est indépendante mais documentaire. Les durées ci-dessus ne prouvent aucun gain avant/après.

Les chemins courts se rapportent à `after-0/changelog/2026-09-15_01_repair/` pour `preuves/`, et à l’archive N07-codex-candidate pour les traces bridge/raw/oracle. Le JSON adjacent conserve les citations détaillées et mesures structurées.
