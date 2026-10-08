# Travail Odoo

Hors Odoo, cet aiguillage ne s’applique pas. Sources `~/odoo-sources/<série>` et
`<série>-enterprise` en lecture seule (14, 17, 18, 19, saas 19.1/19.4, 20).
Tout développement va dans le projet custom, dans **sa série**.

## Commencer

Avant le code Odoo : `python3 ~/.odoo19-agents/scripts/odoo_briefing.py <projet>`.
Le briefing est ciblé par défaut ; `--query "<besoin>"` précise la recherche,
`--full-memory` demande l’intégralité. Règles et exceptions restent entières ;
un budget insuffisant exige de lire les sources signalées.
Projet non déclaré : `odoo_project_scan.py <projet>`.
Pour reprendre une release : `odoo_work.py prepare <projet> --release <id>
--task <id> --query "<besoin>"` réunit contexte, état et retours à qualifier.

Références dans `~/.odoo19-agents/docs/reference/` : `SERIES_MATRIX.md` fait foi
sur `ODOO19_STYLE_GUIDE.md` (19.0 seulement), `PLATEFORMES.md` sur hébergement et
restauration, `LESSONS.md` pour les erreurs déjà payées. Charger selon le besoin.

## Choisir le travail

| Besoin | Entrée |
|---|---|
| Comprendre, challenger, arbitrer | `odoo-analyst` |
| Ticket ou dysfonctionnement | `odoo-support` : diagnostic avant correctif |
| Développer/configurer | `/odoo-new` : qualifier → réaliser → vérifier → mémoire |
| Correction locale réversible, sans schéma/droits/données/calcul financier | `/odoo-express` |
| Préparer plusieurs demandes | `/odoo-plan` |
| Exécuter/reprendre le plan autorisé | `/odoo-start` |
| Recetter/clôturer/livrer | `/odoo-close` |
| Validation seule | `odoo-tester` |
| Guide ou communication demandés | `camptocamp-docs` |
| Environnements et accès | `/odoo-env` |
| Préparer/suivre une livraison GitHub → Odoo.sh | `odoo-deployer` : candidat, accord exact, build puis vérification |
| Estimation des agents | `/odoo-estimate` |
| Remarque à retenir / bilan | `/odoo-feedback` |
| Améliorer les agents et outils | `/odoo-improve` |

## Contrat de travail

Un responsable porte résultat, critères, risques et preuve jusqu’à réception.
Il applique les rôles utiles lui-même ; déléguer seulement une recherche
indépendante utile ou une relecture dont l’indépendance change la décision.
Les risques droits, comptabilité, facturation et données existantes exigent la
voie renforcée. `/odoo-express` reste sans sous-agent.

L’orchestrateur seul écrit les états des flows et consolide les documents partagés.
Les workflows restent ceux de `workflows/odoo-workflow.json` : `status`, `ready`,
`claim --owner <fournisseur-rôle>`, résultat avec preuve puis `complete`.
Lire `docs/roles/orchestration-graph.md` quand un flow est nécessaire.
Les verrous, preuves et portes humaines restent obligatoires ; aucun JSON d’état
retouché pour forcer une transition. Une confirmation déjà donnée vaut pour son
périmètre ; une attente humaine exige une décision consignée, jamais le silence.

Poursuivre sans nouvelle permission entre étapes autorisées. Arrêt sur décision
bloquante ou deux reprises infructueuses. Tâche : lint touché, install/update,
tests ciblés ; recette entière à la clôture. Réutiliser les preuves fraîches ;
toute répétition indique la source, l’environnement ou le critère changé.
Un contrôle réussi doit prouver le résultat métier attendu.

Mémoire : journal ≤ 15 lignes par intervention, détail dans la release. Préférer
les ajouts sourcés et décisions acceptées à la réécriture complète du projet.
Les retours sont collectés aux réceptions et clôtures ; leur promotion en règle
générale passe par `/odoo-improve`. Lire `docs/HARNESS.md` pour les commandes.
Pas de guide/capture documentaire/communication avant clôture sans demande.
Mail reçu : original intégral via `odoo_mail.py`, pièces dans `pieces/`.

## Données et production

Copie locale neutralisée privilégiée (`odoo-restore.sh`). Studio/module se choisit
avec l’analyste ; Online impose Studio. Pack Studio versionné, limites annoncées.
Pour accès distant, `/odoo-env` : dialogue bureau, secrets au trousseau, métadonnées
sans secret dans `instances.json`. Aucun secret dans conversation ou Git.
Production : annoncer « Vous me donnez accès à la PRODUCTION de <client>. Je n’y
ferai que de la lecture. Toute écriture vous sera demandée explicitement,
opération par opération. » Chaque écriture exige confirmation de cette opération,
`--allow-write` et `ODOO_PRODUCTION_CONFIRMED=<nom>`. Aucun test/capture/reprise en
production. Staging/test : écritures annoncées et nettoyées.
Détails support, Studio et données : `docs/roles/routing-details.md` si concernés.
