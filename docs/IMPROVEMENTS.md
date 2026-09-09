# Suivi des propositions et critères d'adoption

Références R/S/M : analyse privée du bureau, 7–8 septembre 2026. Elle reste la
source de conception ; ce tableau décrit la réalisation et ses limites. Une
modification d'instructions ne vaut amélioration mesurée qu'après un essai
comportemental. Les rapports des 8 et 9 septembre distinguent ces preuves.

## Fiabilité du socle

| Proposition | Réalisation | Preuve / limite |
|---|---|---|
| R01 — instructions contradictoires | Migration avec sauvegarde du bloc personnel ancien, suppression du doublon documentaire généré, pointeur commun | Tests migration/idempotence ; les règles non générées d'un projet ne sont pas écrasées |
| R02 — génération incomplètement contrôlée | Toutes les sorties Claude/Codex contrôlées, build isolé et code retour bloquant | Suite génération, build et CI |
| R03 — QA faussement verte | Résumé positif et tests du module exigés ; installation du module absent ; copie client/dispense selon risque | Faux vert reproduit sur Odoo, tests shell/parser |
| R04 — restauration masquant les erreurs | Échec de préparation/update bloquant, postconditions ; filestore via conteneur temporaire | Tests simulés puis vraie restauration synthétique SQL + filestore et neutralisation, voisine inchangée ; aucune restauration client |
| R05 — invariants masqués en lint | Invariants toujours évalués, y compris diff vide ou uniquement suppressions | Tests lint ; analyse AST déjà employée pour les modèles, pas un analyseur complet d'Odoo |
| R06 — ressources réelles | Registre physique optionnel, relations parent/enfant ; plan réserve les périmètres des tâches | Tests interprojets et périmètres ; déclarations coopératives, pas d'isolation magique |
| R07 — concurrence Docker | Bases par projet, verrous DB/gabarit, PostgreSQL laissé au superviseur ; banc avec réseaux/bases distincts | Tests shell et exécutions isolées ; stack interactive garde des ports explicites, concurrence bornée par l'orchestrateur |
| R08 — preuve obsolète | Empreinte de contenu et log, réception du plan et sceau de clôture | Tests ajout/mutation/timeout ; environnement et couverture doivent aussi être relus |
| R09 — reprise après évolution du graphe | Snapshot, libération indépendante du graphe courant, migration sémantique contrôlée | Tests de migration ; pas de migration forcée d'un nœud dont le sens change |
| R10 — accès distant Studio | Chemin local limité, méthodes de lecture explicites, garde d'instance distante | Tests sans production ; les droits serveur restent nécessaires |
| R11 — pack partiel/idempotence | Prévalidation, import objet/XML-ID atomique, ordre des références, rejeu | Tests ORM et Studio ; le pack entier n'est pas une transaction globale Online |
| R12 — défaut non bloquant par étiquette | Contrat QA optionnel lié au flow : couverture exhaustive inchangée requise pour pass | [Garde adopté après comparaison native et contre-épreuves](quality-lab/coverage-2026-09-09/README.md) : D31 passe de pass erroné à blocked, positif accepté. Rendu QA lié à l’issue adopté dans la [qualification autonome](quality-lab/qualification-2026-09-09/README.md) ; contradictions contrôlées mécaniquement pour le rapport cité, récits libres et sens des preuves restent à relire |
| R13 — couverture concentrée | Suites par outil, cas métier, mutations, campagnes natives et juge masqué | Résultats et limites dans les rapports ; un nombre de tests n'est pas une note métier |

## Vitesse, sans affaiblir les verdicts

| Proposition | Réalisation / arbitrage | Vérification |
|---|---|---|
| S01 — tests répétés développeur/QA | Réutilisation autorisée d'une preuve encore valable, relecture indépendante maintenue | Contrôles de fraîcheur ; pas de réutilisation sur une base ou image différente non contrôlée |
| S02 — version préparée trop tard | Préparation idempotente avant recette, version choisie par le projet préservée | Tests manifest et clôture |
| S03 — diff tâche/release | Empreintes initiales du plan et commande `changed` ; diff release conservé à la clôture | Tests réception ; invariants de module toujours contrôlés |
| S04 — journal zéro | Extraction corrigée sans perte de champs Appris | Tests briefing |
| S05 — briefing lent/gros | Mode offline, contexte ciblé et index des blocs omis | Tests contexte ; recherche lexicale, rappel non exhaustif |
| S06 — cache gabarit insuffisant | Clé enrichie par image et révisions Enterprise, verrou lors de reconstruction | Tests outillage ; aucune promesse de réutilisation entre environnements différents |
| S07 — filestore dépendant du service permanent | Conteneur temporaire avec volume partagé, erreurs non masquées | Tests transport, syntaxe shell |
| S08 — environnement non identifié | Image effective enregistrée dans les campagnes, série explicite, empreintes des sources | Témoins ORM 18/19 et vrai Chrome19 avec résultat serveur/mutant ; pas de compatibilité globale des séries |
| S09 — RPC répétitifs | Métadonnées groupées/cachées dans export/prévalidation/application, invalidées lors d'écritures de schéma | Tests packs et rejeu Studio ; pas de concurrence des écritures |
| S10 — double update | Update et tests dans un passage commun après installation | Comparaison réelle de l'ancien et du nouveau shell ; résultat mesuré dans le rapport |
| S11 — prêt mais verrou indisponible | `ready` expose revendicable/bloquant/propriétaire ; `claim` reste atomique | Tests de conflits ; état indicatif jusqu'au claim |
| S12 — argument restore transmis deux fois | Sous-commande retirée avant l'appel au restaurateur | Test de contrat du dispatch |

## Mémoire et architecture

| Proposition | Réalisation / limite |
|---|---|
| M01–M03 — apprentissages perdus | Extraction complète avec provenance, zéro explicite ; les récits rédigés restent imparfaits (prêt dit gratuit dans N01, qualification autonome) |
| M04 — anciennes règles prises pour actuelles | Décisions structurées optionnelles et remplacements ; contexte courant distinct des archives. Pas d'arbitrage automatique de vieux journaux |
| M05 — consolidation peu contrôlée | Réception de tâche et clôture portent un fragment de consolidation haché ; l'orchestrateur relit sa pertinence |
| M06 — synchronisation/passation | Plan et réceptions versionnés, contexte sourcé vérifiable ; checkout sans état local signalé, jamais déclaré vert silencieusement |
| M07 — volume | Sélection progressive à la demande, blocs entiers et index de sources ; les anciens dossiers restent consultables |
| §6 / §10 — préparer puis exécuter | `/odoo-plan` et `/odoo-start`, en conservant `/odoo-new` direct ; tâches, dépendances, risque, critères et réception |
| §7 — parallélisme utile | Analyse/tâches indépendantes quand ressources compatibles ; compteur de revendications distingué des agents démarrés ; mode natif Claude de délégation expérimental, événements et reprise dans [l'essai complémentaire](quality-lab/delegation-2026-09-09/README.md). Le pont Odoo et la recette partagée restent sérialisés ; aucun gain de vitesse démontré |
| §8 / §14 — métier et tests | Catalogue SCENARIOS optionnel sourcé, sélection par impact, élargissement si dépendance inconnue, oracle indépendant |
| §9 — documentation | `doc.md` et consolidation obligatoires ; guides DOCX/PDF et communication facultatifs sur demande, y compris après clôture |
| §15–16 — boucle d'amélioration | Référence figée, essais, défaut, correction, contre-épreuve, décision d'adoption, installation/publication ; pas de promotion automatique par une note LLM |

Les nouveaux modules d'outillage sont vérifiés dans un projet jetable. Ils ne
migrent pas les bases clients ni les plans historiques. Une parallélisation complète
de la recette, un raisonnement sémantique automatique sur tous les vieux journaux
ou une supériorité générale d'un modèle ne sont pas déclarés livrés : ces promesses
ne sont pas justifiées par les preuves disponibles.
