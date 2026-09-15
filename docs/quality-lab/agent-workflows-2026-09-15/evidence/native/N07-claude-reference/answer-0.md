**Terminé — tâche reçue, release laissée ouverte.**

## Cadrage
Projet `/work`, série **19.0** (lue dans `.odoo-agents/config`), release ouverte `changelog/2026-09-15_01_repair`, module `lab_preparation`, copie synthétique `lab_client`. Revue fonctionnelle contradictoire écrite dans la release (`revue_fonctionnelle.md`) : verdict **à développer**, voie module, **QA renforcée** car la tâche reprend des données existantes. Les quatre défauts sont nommés avec la cohorte qui les prouve (id 1 à `prepared_qty=999`, un zéro manuel écrasé, un `done` écrasé).

## Réalisation (`lab_preparation`)
- `_cron_prepare` borné à `state=draft` **et** `manual=False`, valeur `max(ordered-delivered, 0)`.
- `action_set_manual` marque `manual=True` même à zéro (c'était `bool(quantity)` — la cause du zéro écrasé).
- Duplication : `copy=False` sur `delivered_qty`, `prepared_qty`, `manual`, `state`.
- `action_remainder` : création du reste **seulement s'il est positif**, `parent_id` sur la source, source passée `done` sans que sa `prepared_qty` soit touchée ; recordset vide sinon.
- Reprise : `migrations/19.0.1.1.0/post-migrate.py` + manifest `19.0.1.0.0 → 19.0.1.1.0`.

## QA réellement exécutée (12/12 critères couverts)
- **Rouge d'abord** : 9 échecs sur 11 sur le code d'origine restauré depuis `HEAD` (`preuves/tests_rouge_avant_correction.txt`). Les 2 verts d'emblée sont assumés comme garde-fous, pas comme révélateurs.
- **Vert** : base neuve `install=ok` et mise à jour `update=ok`, 0 échec (`preuves/tests_vert_*.txt`).
- **Copie** : après `post-migrate`, id 1 → 7 ; ids 2, 3, 4 conservent leur **`write_date` d'origine**, donc aucun `write`, pas seulement aucun écart.
- **Parcours réels** : vrai XML-RPC (zéro manuel, reliquat, parent) et vrai shell (zéro, duplication, reliquat, solde sans reste, puis cron). Enregistrements de contrôle supprimés : la copie est à ses 4 lignes de référence.

## À décider
1. **Le lint du module reste rouge** : `__manifest__.py` n'a pas de clé `author`. Dette **antérieure** (absente aussi à `HEAD`), non reprise selon le rôle. Dites-moi si je la corrige maintenant — sinon elle bloquera `/odoo-close`.
2. **Hypothèse H1** : N-17 se lit de deux façons sur `action_remainder()` sans reste positif. J'ai retenu « la source passe quand même `done` » (la condition ne porte grammaticalement que sur la création) et je l'ai écrite dans le code, les tests et `PROJECT.md`. À confirmer par le métier.
3. Idempotence prouvée **sur les valeurs et sur l'absence d'écriture hors périmètre** ; la `write_date` des drafts automatiques est réécrite à chaque tour. J'ai écarté le garde « ne pas réécrire si identique » pour ne pas inventer de comportement.

## Limites et état
Pas d'écran ni de droits d'un autre utilisateur exercés (le module ne livre ni vue ni groupe) ; aucun `ir.cron` livré, hors périmètre N-17 ; **aucun déploiement, aucun commit**. Recette complète, désinstallation et livrables : à `/odoo-close`.

Un détail de pilotage : j'avais ouvert le premier run sur la transition `module` alors que la reprise de données impose `module_high_risk` ; il a été abandonné et rejoué sous `preparation-n17-hr`, sur la voie renforcée (noté dans le README). La réception documentaire a été faite par moi-même, faute de sous-agent : elle **n'est pas indépendante**, et le garde qui l'exige n'a donc pas été activé.

Message de commit proposé : `[FIX] lab_preparation: borner la préparation périodique aux drafts automatiques`.