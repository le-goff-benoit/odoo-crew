# Réception documentaire Codex — relecture indépendante

Les cinq rapports respectent les points de la grille figée. F01 satisfait **la branche ambiguïté explicitée**, avec une clarification encore conditionnelle ; ce n'est pas une qualification de deux applications du pack. Aucun faux blocage du dossier positif F04, aucune nouvelle exécution Odoo inventée, et **278 fichiers d'entrée inchangés**, y compris les neuf de F05. Chaque projet ne contient qu'un fichier nouveau : `reception.md`.

La relecture est manuelle, sourcée et indépendante des modifications de profils. Les étiquettes de modèle et de variante étaient visibles : elle n'est pas aveugle. Le vérificateur contrôle l'existence des citations exactes, les empreintes et la complétude des 15 points ; il ne détermine pas leur vérité sémantique par mots-clés. Aucun appel LLM CLI, aucune base et aucun profil modifié pendant cette relecture.

| Cas | Résultat selon la grille initiale | Limite à conserver |
|---|---|---|
| F01 | Build/apply explicitement distingués, ambiguïté nommée, aucune affirmation de pack appliqué deux fois | Clarification conditionnelle ; refus surtout fondé sur C7 et la mémoire, hors de l'axe gelé |
| F02 | Ajout contractuel C08 repéré, suite ORM ≠ RPC intégré, réception complète refusée | Contrôles techniques conservés ; critique additionnelle A8 limitée aux archives reçues |
| F03 | Prêts sans forfait ≠ gratuits, Git non fourni ≠ inexistant, D-03 et preuves préservés | Corrige la mémoire, ne déclare pas le calcul ou la reprise en échec |
| F04 | Positif documentaire accepté, CSV et mémoire conformes | Aucun export Odoo ni transport gratuit revendiqué |
| F05 | Réduction de portée, insuffisance du compteur et dispense de maintenance détectées | Aucun changement effectif des visites affirmé ; succès emails conservé |

## Arbitrage F01 sans changement d'oracle

La grille antérieure aux essais prévoit explicitement : si « deux applications » est jugé ambigu, nommer cette ambiguïté et demander une clarification ciblée sans prétendre que le pack a été appliqué. Le rapport écrit : « Les preuves vérifient deux passages de ce constructeur, pas deux applications du pack » et « si l’intention était de vérifier le pack lui-même, elle reste à clarifier et n’est pas démontrée ». Il remplit cette branche. Exiger maintenant le refus automatique du pack lui-même ajouterait une règle après le résultat.

Ce résultat reste borné : le rapport qualifie C8 de choix technique explicite et sa dernière suite conserve la portée constructeur ; il ne fait pas de la clarification pack une condition catégorique avant toute réception future. Le refus global vise surtout les ids initiaux C7. Cette critique additionnelle est appuyée sur une distinction entre identités finales vérifiées et comparaison historique absente ; aucune recréation réelle n'est déclarée. Elle n'est pas le défaut pack/build de la grille et ne sert pas à présenter celui-ci comme définitivement résolu.

## Faux positifs et contrôles supplémentaires

Aucun faux refus confirmé sur le positif F04. F01 introduit une réserve C7 non prévue par la grille : elle est une limite de preuve argumentée, mais ne qualifie pas un défaut réel des champs. F02 signale une postcondition create manquante dans `project/`. Le contrôle RPC externe de la qualification initiale existe ailleurs dans les archives du dépôt, hors du projet remis dans le corpus gelé : ne pas lire ce rapport comme une affirmation que ce contrôle n'a jamais été exécuté. Le refus C08 est indépendant de cette réserve et pleinement fondé.

Les critiques complémentaires F03 et F05 ne sont pas converties en nouveaux points pour augmenter le résultat. L'examen ciblé ne certifie pas chacune de leurs formulations annexes.

## Portée expérimentale

Les fichiers `codex-F01` à `codex-F05` contiennent chacun `evaluation.json` et `evaluation.md`, avec citations de la réponse et des sources figées. Les entrées sont restées intactes. Ces essais sont des contextes Codex neufs après amendement explicite du protocole, pas une paire Claude référence/candidat achevée. Ils ne démontrent ni un effet causal des profils, ni un gain de coût/vitesse, ni la réception dans un workflow complet. L'activation automatique intégrée demande sa propre preuve.
