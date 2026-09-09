# Revue indépendante — reprise mémoire

Verdict : **favorable après correction de la régression des bases mémoire vides**. Revue de scripts/odoo_flow.py, scripts/odoo_reception.py, workflows/odoo-workflow.json et tests/test_odoo_recovery.py ; empreintes de la version relue dans reviewed-sha256.json. Aucun cas heldout, matérialiseur ou oracle de campagne lu. Aucun fichier canonique modifié.

## Invariants vérifiés

- La publication exige le journal revendiqué par le bon propriétaire, un verrou compatible présent au registre, et la réception effectivement acceptée. Elle contrôle toutes les cibles avant mutation et reprend seulement les états avant/draft.
- La reprise passe par le nouveau nœud dédié. Elle ne recrée pas les jetons des gates QA join=all. Demande, spécification, preuves, périmètre et code restent liés à l'acceptation précédente.
- Une nouvelle réception remplace l'acceptation active en conservant ses références historiques. Un ancien reçu ne valide pas le nouveau bundle. Les erreurs de source ou preuve empêchent la reprise mais permettent l'arrêt motivé.
- Deux reprises maximum ; arrêt terminal distinct d'une QA rouge ; une tentative planifiée encore active ne peut pas être rouverte comme si elle était terminée.
- Migration explicite : intégrité du graphe ancien vérifiée, aucune revendication active, journal jamais exécuté, delta connu exact, conservation des tokens et événements. Le durcissement final compare aussi le contenu précis des nouveaux nœuds et arêtes.

## Anomalie trouvée et correction réceptionnée

`prepare_reception` créait une copie de base pour un JOURNAL existant vide, puis `verify_bundle/check_ref` refusait ce fichier car project_file impose un contenu non vide. Un fichier ne contenant que des espaces atteignait ensuite une citation obligatoire impossible à satisfaire (quote.strip() vide).

La correction maintient l'empreinte exacte et distingue fichier absent de fichier vide ; elle autorise la lecture d'une base vide et n'exige pas de citation littérale pour les bases sans texte. Deux cas adverses indépendants (0 octet et 5 octets d'espaces/sauts de ligne) passent désormais : adversarial-fixed.json. Ce résultat utilise des citations valides, sans citation vide artificiellement ajoutée par la fixture.

## Vérifications effectuées

- 13 tests ciblés de reprise verts dans targeted-tests.log, avant les tests supplémentaires ajoutés ensuite par le développeur. La suite entière est exécutée par l'orchestrateur/développeur ; elle n'est pas dupliquée ici.
- Une vraie interruption de processus, complémentaire au mock du test unitaire : le processus enfant exécute le premier remplacement puis reçoit SIGKILL. Son code de sortie est -9. Le parent reprend la même revendication ; actions `already_published` pour PROJECT et `published` pour JOURNAL, puis journal done. Aucune modification manuelle d'état. Preuve process-interrupt.json et script process_interrupt.py.
- Revalidation ciblée des bases vides/espaces après correction.

## Limites exactes

Ces contrôles ne constituent pas une exécution Odoo ni une preuve du jugement sémantique d'un agent. L'interruption porte sur un vrai processus local utilisant les APIs publiques, avec une fixture d'entrée QA explicitement synthétique. Le remplacement est atomique par fichier, pas entre les deux fichiers ; le verrou est coopératif et aucune résistance à une panne électrique n'est revendiquée. L'identité déclarée du relecteur n'est pas une authentification cryptographique de son indépendance.

Les anciens drafts peuvent être périmés lors d'une reprise (cas autorisé explicitement par les tests) : les empreintes historiques signalent alors leur ancienne identité mais ne permettent pas de reconstruire les octets perdus. Les rôles doivent donc continuer à créer de nouveaux fichiers et conserver les anciennes pièces ; le garde ne répare pas une archive volontairement écrasée. Cela n'autorise pas à réutiliser des sources, preuves ou contrats périmés.
