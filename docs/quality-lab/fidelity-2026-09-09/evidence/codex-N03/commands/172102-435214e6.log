# QA indépendante — voie graph-lane-studio-diff

**Module :** aucun module custom ; pack Studio de /work. **Série :** 19.0, confirmée à nouveau par RPC (19.0+e-20260817), briefing initial par défaut corroboré. **Mode :** QA de tâche, voie diff uniquement.

## Verdict de voie
**VALIDÉ pour le diff et le périmètre contrôlable du pack.** Aucune anomalie constatée. Les scénarios, applications répétées et la jointure documentaire relèvent des autres voies.

## Commandes et preuves
Lecture de LAB.md, rôle qa-review.md figé, briefing fourni, demande-originale.md, decisions/2026-09-08.md et revue_fonctionnelle.md.
Commande réelle :
`python3 ~/.odoo19-agents/scripts/odoo_pack.py diff /work/changelog/2026-09-09_01_revue-des-locations-d-22/studio/pack.json --db lab_client --url http://127.0.0.1:52795`
Résultat conservé dans studio_diff.log : **0 à créer / 0 à modifier / 1 inchangé**.
Inspection XML-RPC exclusivement search_read/version (authentification locale) : ir.model.fields du modèle, ir.model.data du module studio_customization, versions des modules base/web_studio/studio_customization. Comparaison par ID et égalité exacte de tous les attributs de l'inventaire initial. Résultats complets dans studio_diff.log.
Lecture du script build_review.py ; git status --short ; liste des livrables. Aucun apply ni écriture en base effectué par cette voie.

## Résultats
| Contrôle | Preuve | Résultat |
|---|---|---|
| A1 : un seul champ ajouté | Pack records = 1 ; delta inventaire = ID 3740 uniquement | Boolean manuel stocké, x_studio_needs_review |
| Dépendances et règle D-22 | pack.json lignes 37–39 et relecture RPC | x_studio_days,x_studio_kind ; days >= 7 ET kind == rental |
| Champs initiaux réutilisés | Inventaire puis RPC : x_name 3734, x_studio_days 3736, x_studio_kind 3738 | IDs et tous attributs inventoriés identiques ; aucun doublon |
| A3 : références et diff | Référence lab_seed_model résolue vers ir.model 422 ; XML-ID nouveau champ unique et marqué studio/noupdate | Aucune référence unresolved ; diff nul |
| A4 : écrans, droits, envois | Pack limité à ir.model.fields, groups=[], tracking=0 ; build limité au booléen ; XML-ID Studio hors lab_seed_* unique | Aucun objet de vue, accès, règle, automatisation ou envoi livré |
| Versions | RPC : base 19.0.1.3, web_studio 19.0.1.0 installés ; serveur 19.0 | Le champ series du pack vaut 19.0.1.3, cohérent avec version du module base ; aucun manifest custom |
| Cible | source du pack et commande = 127.0.0.1:52795 / lab_client | Contrôle strictement local |

Empreinte SHA-256 du pack contrôlé : `6507bfae09677745a3e6d549a96e36cffb57f0f7a4767d0c4a386917909b49a8`.

## Limites explicites
L'inventaire initial contient les champs et les demandes, pas un historique exhaustif des vues/droits/envois ni de leurs écritures : leur absence de modification globale passée ne se démontre pas par ce seul inventaire. Les preuves statiques du build/pack et les XML-ID présents corroborent le périmètre demandé ; aucune anomalie opposée observée.
Aucun appel distant ni déploiement dans les commandes exécutées par cette voie. L'absence de tout déploiement historique externe n'est pas observable depuis cette copie synthétique ; aucun accès externe n'a été tenté.
Le pack est livré dans le dossier de release, encore non suivi dans git status (changelog/ non suivi) : aucun commit ni publication n'est affirmé. Deux applications et valeurs recalculées doivent être attestées par la voie scénarios ; A5 appartient à l'orchestrateur.
