# Couverture à compléter après la campagne native

Audit local du 9 septembre 2026, référence `ddc8f7d`. L'audit indépendant
initialement délégué n'a pas produit de résultat : quota fournisseur. Cette
analyse est donc celle de l'orchestrateur, non aveugle. Les priorités portent
sur les conséquences d'un échec, pas sur un classement des modèles.

Complément réalisé : N04 avec cinq sous-agents, puis reprise avec trois QA
concurrentes sur nouvelles bases. Les revendications abandonnées sont récupérées
et l'oracle métier passe, mais la jointure déclare satisfait A8 sans sa preuve
utilisateur. La tentative de correction par ajout d'une consigne n'apporte pas
de gain sur dossier isolé et n'est pas adoptée. La fidélité des critères dans
une consolidation longue est donc le prochain défaut prioritaire à reproduire.
Les autres scénarios ci-dessous restent à jouer ; leur simple présence dans
ce carnet ne constitue pas une preuve.

| Priorité | Dimension et preuve existante | Ce qui reste à éprouver | Critère et boucle proposée |
|---|---|---|---|
| 1 | Délégation : forks, jointures et verrous testés dans `tests/test_odoo_flow.py`. Les parcours natifs désactivent explicitement les sous-agents (`scripts/odoo_bench_native.py`, `native_command` et `_trial`). | Vrais enfants simultanés, passation, désaccord entre fragments, branche sans preuve, refus fournisseur. | Identifiants et événements natifs, responsabilités distinctes, synthèse après toutes les preuves ; aucun gain annoncé sans mesure. D01–D03 du protocole associé. Corriger seulement le défaut observé et rejouer un cas inédit. |
| 1 | QA et oracle : mutations métier et juge masqué, puis arbitrage non aveugle (`../experiment-2026-09-08/REVIEW-NOTES.md`). | Un agent QA indépendant refuse-t-il une preuve partielle, un test qui vérifie la mauvaise règle ou une synthèse qui contredit un résultat rouge ? | Injecter séparément contrôle absent, mauvaise attente et log d'un ancien code ; exiger refus motivé des trois et acceptation du témoin correct. Étalonner l'oracle avant de corriger le rôle. |
| 1 | Droits et données sensibles : garde de production testé sans réseau (`tests/test_odoo_guards.py`), route renforcée testée dans le graphe. | Refus réels ORM/RPC, isolation multi-sociétés et absence de contournement sous un vrai profil utilisateur ; comptabilité et facturation complètes non couvertes par ces petits cas. | Base synthétique avec deux sociétés, utilisateur limité, données témoins. Vérifier lecture/écriture/import et accès direct serveur, puis invariants comptables d'un contrat explicite. Aucune production nécessaire. Nouveau domaine sensible pour contre-épreuve. |
| 1 | Reprise et mémoire : N01 change une décision dans un contexte neuf ; empreintes, décision remplacée et sources omises testées (`tests/test_odoo_context_scenarios.py`, `tests/test_odoo_release_plan.py`). | Long journal contradictoire, décision arrivée pendant deux tâches, interruption au milieu d'une écriture, reprise par un autre orchestrateur. | Corpus contenant anciennes et nouvelles règles sourcées ; arrêter après une preuve partielle. Le repreneur invalide uniquement les dépendances affectées, conserve l'historique et les questions ouvertes. Contre-épreuve sur une tâche indépendante qui doit rester valide. |
| 2 | Restauration : vrai script avec transport Docker simulé (`tests/test_odoo_restore_shell.py`) ; clones synthétiques dans les oracles. | Sauvegarde complète avec filestore, neutralisation effective, interruption puis nettoyage sans dommage pour une stack voisine. | Produire un ZIP synthétique avec pièce jointe et tâches planifiées ; restaurer sur ressources jetables puis lire la pièce jointe, vérifier neutralisation et postconditions. Injecter archive incomplète et update en erreur. |
| 2 | Navigateur et clôture : présence/fraîcheur des preuves contrôlées par les sceaux ; navigateur exclu des campagnes natives (`../native-2026-09-09/PLAN.md`). | Bouton accessible au bon utilisateur, vraie action d'écran, comportement après validation, capture lisible et guide correspondant à l'état livré. | Parcours navigateur sur copie synthétique avec utilisateurs distincts ; associer chaque écran à une action et un résultat métier. Masquer un bouton sans contrôle serveur comme mutant. Vérifier séparément documents et rendu. |
| 2 | Séries : matrice documentée ; exécutions métier de la campagne sur 19.0 (`../native-2026-09-09/README.md`). | Exécution correcte en 17/18 et SaaS, différence Community/Enterprise, changement de série dans une conversation. | Contrat identique sur 18.0 puis 19.0 avec sources/images identifiées et tests adaptés ; contre-épreuve nouvelle série équipée. Échec attendu lorsqu'un composant n'existe pas, sans invention de compatibilité. Pas d'extrapolation à toutes les séries. |
| 3 | Coût et durée : timings descriptifs sous charge, aucun gain global démontré (`../native-2026-09-09/README.md`, « Qualité, vitesse et limites »). | Gain net de la délégation après lancement, transmission, attente et consolidation ; effet du contexte compact sur les omissions. | Au moins deux répétitions par ordre séquentiel/parallèle inversé, mêmes modèle/effort/cas, environnement comparable. Compter durée totale, tokens disponibles, incidents et erreurs critiques. Une perte de fidélité interdit la promotion, même plus rapide. |

Ces éléments sont un carnet d'essais priorisé, pas huit améliorations déjà
constatées ni une promesse de tout avoir testé. Les premiers essais doivent
porter sur délégation, fiabilité du verdict et reprise ; les parcours sensibles
exigent un contrat métier et un oracle dédiés avant toute modification des rôles.

## Essais de délégation à exécuter

- **D01 — voies indépendantes.** Utiliser le vrai graphe `development_complex`
  sur un dossier synthétique : une capacité standard décrite par un extrait de
  référence, une décision de projet, un inventaire de données. Trois enfants
  reçoivent chacun une voie, le briefing commun et un fichier de sortie propre.
  L'orchestrateur seul revendique/termine et consolide. Vérifier dans les
  événements du moteur que les enfants existent et travaillent avec un
  chevauchement ; les seules heures de `claim` ne suffisent pas. Les extraits
  fictifs ne valent pas validation des sources Odoo.
- **D02 — interruption.** Faire terminer une voie, interrompre une autre après
  un résultat partiel et laisser la troisième disponible. Vérifier la conservation
  de la preuve terminée, la libération du seul verrou abandonné, l'absence de
  synthèse prématurée et la réattribution explicite. Un incident fournisseur
  reste distinct d'une erreur d'analyse. Les tests déterministes livrés ici
  vérifient ces mécanismes sans prétendre reproduire le comportement d'un LLM.
- **D03 — contre-épreuve réservée.** Construire, après D01 et avant toute correction
  candidate, un second domaine avec contradiction sourcée et ressource commune.
  Figer dossier et grille avant exécution ; ne pas fournir le corrigé aux agents.
  Le résultat doit respecter la sérialisation et conserver l'arbitrage ouvert.
  À ce stade seul le thème est réservé : aucun corpus inédit n'a encore été figé
  ni exécuté, donc aucune généralisation comportementale n'est acquise.

Chaque essai conserve : révision des profils, demande, dossiers et empreintes,
modèle demandé et modèle effectivement retourné si disponible, événements
parent/enfants, logs `claim`/`complete`/`release`, fragments originaux, verdict
par critère et incidents. Calibrer le correcteur avec un résultat correct et
des défauts injectés avant de noter les générations. Si une correction de rôle
est nécessaire, comparer avant/après à réglages constants et conserver les
échecs ; ne jamais retoucher la génération pour améliorer la note.
