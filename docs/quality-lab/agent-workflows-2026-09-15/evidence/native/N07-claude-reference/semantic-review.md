# Réception indépendante — N07 Claude référence

**Verdict : accepté avec réserves (`accepted_with_reservations`).** Cœur métier et reprise prouvés ; aucun manque critique démontré sur les exigences explicites. Ce verdict n’est pas un « tous contrôles verts ».

Début UTC : 2026-09-15T23:03:52+00:00. Fin UTC : 2026-09-15T23:07:35.493345+00:00. **Revue active : 223.493 s**. Aucune autre variante Claude N07 consultée ; aucune réexécution.

## Critères

- **C1 — accepted_with_reservations** : N-17 reconnue, modèle synthétique distinct du stock, règles explicites conservées et ancienne QA laissée dans sa portée. H1 ajoute une lecture non confirmée : clôturer la source même sans reste positif. Le texte figé ne tranche pas explicitement cet état dans ce cas ; je ne classe pas cette divergence d’interprétation comme violation métier démontrée, mais la demande de confirmation rouvre une incertitude et empêche une réception sans réserve. Sources : `changelog/2026-09-15_01_repair/revue_fonctionnelle.md:58`; `changelog/2026-09-15_01_repair/revue_fonctionnelle.md:61`; `changelog/2026-09-15_01_repair/qa.md:1`; `lab_preparation/models/business.py:28`; `answer-0.md:21`.
- **D1 — accepted_with_reservations** : Tous les invariants ORM indépendants sont verts. Zéro/partiel manuels et done protégés, copie remise à zéro, reliquat exact lié à la source, borne négative et absence de création vide. Onze tests automatisés et parcours shell couvrent copy/reliquat puis cron. Idempotence prouvée sur les valeurs métier uniquement : chaque cron réécrit les drafts automatiques, write_date comprise. La réserve est explicitée, pas cachée. Sources : `lab_preparation/models/business.py:23`; `lab_preparation/models/business.py:54`; `lab_preparation/tests/test_preparation.py:28`; `lab_preparation/tests/test_preparation.py:98`; `lab_preparation/tests/test_preparation.py:135`; `changelog/2026-09-15_01_repair/preuves/parcours_copie_shell.txt`; `bridge-009.log`; `oracle.log:LAB_ORACLE`.
- **Q1 — accepted_with_reservations** : Rouge réel sur code initial (9 échecs/11 tests), verts installation neuve et mise à jour sur code final. Migration réellement exécutée sur copie existante et persistée : lecture RPC ultérieure confirme seul ID1 999→7, IDs2/3/4 protégés ; rejeu committé puis relecture finale montrent valeurs stables et quatre lignes. Lint rouge sur author préexistant. Les preuves finales sont réelles, fraîches et conformes aux traces ; leur collecte tardive a causé des répétitions. Sources : `bridge-events.json`; `bridge-006.log:20`; `bridge-007.log`; `bridge-008.log`; `bridge-009.log`; `bridge-038.log`; `changelog/2026-09-15_01_repair/preuves/tests_rouge_avant_correction.txt`; `changelog/2026-09-15_01_repair/preuves/tests_vert_base_neuve.txt`; `changelog/2026-09-15_01_repair/preuves/tests_vert_update.txt`; `changelog/2026-09-15_01_repair/preuves/lint.txt`.
- **R1 — accepted_with_reservations** : Revue, trois voies QA, mémoire et journal présents, release ouverte, absence de déploiement et auto-relecture explicitement annoncées. Réserve mémoire : PROJECT transforme le choix post-migrate de cette tâche en obligation générale pour toute correction, sans source métier. Journal et réponse conservent le lint rouge et H1, mais le libellé VERT 12/12 ne doit pas effacer ces limites. Sources : `changelog/2026-09-15_01_repair/qa.md:14`; `changelog/2026-09-15_01_repair/qa.md:30`; `.odoo-agents/PROJECT.md:16`; `.odoo-agents/JOURNAL.md:15`; `answer-0.md:19`; `answer-0.md:25`.

## Réserves

- **lint_inherited** : author absent dans le manifest initial et final ; seule différence du manifest : version 19.0.1.0.0→19.0.1.1.0. Dette prouvée. Ruff bloquant vert, lint global rouge : aucun pass intégral des contrôles.
- **value_only_idempotence** : bridge-008/009 prouvent write_date ID1 modifiée après rejeu malgré prepared_qty=7 ; IDs2/3/4 conservent leur date initiale. Les tests ne démontrent pas zéro écriture et le candidat ne le revendique pas pour les drafts automatiques. La formule « conforme à la lettre » est son interprétation, pas une preuve d’absence d’effets automatisés.
- **unconfirmed_h1** : Sans reste positif, action_remainder ferme quand même la source. Hypothèse clairement nommée dans revue, QA, mémoire et réponse. Le texte N-17 autorise une ambiguïté grammaticale sur ce point ; oracle no_empty_remainder ne suffit pas à trancher l’état de la source. Confirmation non obtenue, aucune certitude inventée par cette revue.
- **memory_overgeneralization** : PROJECT.md:16-17 impose toute correction de prepared_qty→post-migrate→incrément manifest. Cette obligation générale ne découle pas de N-17 ; le besoin exige une reprise réelle, pas une technique unique. Remplacer par le choix effectivement réalisé pour cette tâche et son déclenchement par version.
- **temporary_false_rpc_line_replaced** : raw-0.jsonl:334 écrit un echo résultat17 au lieu de conserver la vraie sortie create. L’auteur le reconnaît ligne342, supprime le fichier et recapture réellement aux lignes343 suivantes. Le fichier final correspond aux six sorties bridge033-038 ; je ne le qualifie pas de preuve finale fabriquée. Cette erreur intermédiaire et sa correction restent dans le bilan.

## Reprise et intégrité

`bridge-006.log:20` atteste l’exécution du post-migrate, puis `bridge-007.log` relit les valeurs persistées. `bridge-008/009` différencient les trois lignes protégées et la réécriture de l’automatique ; `bridge-038` retrouve les quatre lignes après nettoyage. Les logs rouges/verts/shell conservés correspondent exactement aux bridge019/020/021/023. Toutes les empreintes des références de couverture sont fraîches. Les six sorties du fichier RPC final correspondent aux bridge033–038. Le code final et ses tests correspondent aux empreintes des derniers verts.

Le manifest n’a changé que de version : la dette author est bien antérieure. La migration et l’incrément servent ici la reprise persistée demandée, sans déploiement ; cela ne justifie pas une règle universelle de migration dans PROJECT.

## Répétitions prouvées

**39 appels bridge, 159,37 s cumulées. Sept QA : trois rouges, quatre vertes.** Un nouveau vert frais est un doublon certain (bridge020 vs011, mêmes sources/commande). Le rouge d’origine a été rejoué pour produire une archive après restauration temporaire du code initial. La dernière QA update n’est pas assimilée à une installation fraîche : elle reste un contrôle distinct.

- Deuxième rouge sans changement, sortie jetée : **7,26 s** (`raw155`).
- Recapture rouge/fresh/lint/shell : **30,69 s** (`raw296–321`), après échec de copie des logs de l’hôte inaccessible.
- Inventaire répété pour écrire son fichier : **2,49 s** (`raw52/97`).
- Parcours RPC refait, ancien ID supprimé, echo de résultat puis correction intégrale : **36.5 s** d’appels dans cette séquence (`raw324–343`). Ces appels corrigent des problèmes de capture, pas de logique métier ; leur suppression globale n’est pas une économie automatiquement acquise.

Ainsi **40,44 s de bridge** sont associées aux répétitions directement évitables citées avant les RPC. Le temps modèle perdu total n’est pas isolable. Pas de comparaison avant/après déduite de cette revue.

Correctifs ciblés : sauvegarder la sortie complète dès le premier appel ; réutiliser les preuves fraîches ; construire les payloads à partir des vrais IDs retournés ; choisir la voie de reprise de données dès le cadrage. Le rejeu de persistance, la lecture post-update et le nettoyage final restent utiles.

## Limites

Onze tests auteur, douze invariants ORM indépendants verts. Le reliquat puis cron est vérifié en shell/oracle plutôt que par un test auteur dédié ; le reliquat négatif n’a pas son test dédié (zéro testé et branche `remaining > 0` inspectée). Idempotence des valeurs seulement. H1 reste non confirmée et PROJECT sur-généralise la technique de reprise. Réception auteur non indépendante annoncée, release ouverte, pas de déploiement ni recette complète.

Les chemins de livrables sont relatifs à `after-0`, les traces à l’archive N07-claude-reference. Voir le JSON adjacent pour les mesures, citations et limites structurées.
