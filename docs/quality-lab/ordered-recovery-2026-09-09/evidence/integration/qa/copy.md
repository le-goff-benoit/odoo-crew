# QA de la copie indépendante — 2026-09-09

**Module** `lab_qualification` · **série** 19.0 (origine : manifest, briefing fourni) · **mode** QA de tâche renforcée, voie copie.

**VALIDÉ pour cette voie, sur copie synthétique restaurée.** Aucune donnée client réelle, aucune écriture QA et aucun nouvel update ou test Odoo.

## Opération fraîche réellement exécutée

`python3 integration/qa/verify.py`, enveloppé par le helper public `reference/scripts/odoo_evidence.py run --project integration/run/project --scope lab_qualification --output integration/qa/verification.evidence.json -- python3 integration/qa/verify.py`.

La preuve structurée `verification.evidence.json` porte `result=passed`, sortie 0, durée **0,217 seconde**, module inchangé avant/après. Elle porte une vérification de preuves et des lectures live, **pas une nouvelle suite de tests Odoo**. Les 88 contrôles et les références SHA-256 sont dans `verification.json`.

L'inventaire QA est une nouvelle lecture par **psql dans PostgreSQL réel**, séquentiellement pour ordered_copy puis ordered_seed. Chaque commande exécute `BEGIN READ ONLY`, les SELECT, puis `ROLLBACK`; le serveur retourne `read_only: on`. La requête complète est conservée dans `inventory-readonly.sql` et les argv/durées dans `live-ordered_copy.command.json` et `live-ordered_seed.command.json`. Aucun appel à update/tests sur la référence, aucun commit, aucun nettoyage de ressources. Les inventaires ORM développeur et bootstrap restent des preuves réutilisées ; la nouvelle observation QA est SQL.

## Valeurs observées et comparaison indépendante

`live-ordered_copy.log:1` et `live-ordered_seed.log:1` sont comparés séparément aux inventaires initiaux `../evidence/inventory-ordered_copy-20260909-183801-79429f03.inventory.json` et `../evidence/inventory-ordered_seed-20260909-183759-07173621.inventory.json` (pas simplement à un résumé développeur).

| ID | Nom | État | Quantité | Prix | Montant | Copie et référence |
|---|---|---|---:|---:|---:|---|
| 1 | ordered-seed-draft-zero | draft | 0 | 10 | 0 | Identiques aux originaux |
| 2 | ordered-seed-draft-positive | draft | 3 | 10 | 30 | Identiques aux originaux |
| 3 | ordered-seed-confirmed-positive | confirmed | 3 | 10 | 30 | Identiques aux originaux |

Exactement trois enregistrements dans chaque base ; aucun confirmé invalide. Module installé id346, version stockée 19.0.1.0.0 dans les deux bases. Cette version identique **ne distingue pas** l'update : c'est le schéma live qui fait foi.

| Schéma live | ordered_copy | ordered_seed |
|---|---|---|
| `lab_qualification_quantity_nonnegative` | `CHECK ((quantity >= 0))`, convalidated true | Identique, convalidated true |
| `lab_qualification_confirmed_quantity_positive` | `CHECK ((((state)::text <> 'confirmed'::text) OR (quantity > 0)))`, convalidated true | Absente |
| PK / FK initiales | Présentes et validées | Présentes et validées |

La présence effective et validée de la nouvelle CHECK dans la copie, avec le vrai `-u` et les tests verts, couvre AC10. La référence conserve les trois données et son schéma initial. Elle n'est pas qualifiée de nouvelle installation du code final.

AC11 : aucun script de reprise, hook, write de migration ou correction historique dans le diff. L'update n'a modifié aucune des valeurs valides du jeu initial. Aucun historique invalide n'existe dans ce jeu : cette branche conditionnelle n'a pas été exercée et aucun succès sur une autre base contenant un confirmé nul n'est revendiqué. Ce périmètre correspond à la demande `demande.md:20` et à l'hypothèse de `revue_fonctionnelle.md:77` ; une telle anomalie nécessiterait une nouvelle réception et une décision séparée, sans correction automatique.

## Incidents du script de vérification QA

Deux erreurs de cadrage du vérificateur ont été corrigées sans toucher au module : la première comparaison utilisait le hash brut du fichier au lieu du hash structuré du contrat (`attempt1-contract-hash.evidence.log`, échec avant lecture DB) ; la vérification utilise maintenant le helper cible `odoo_coverage.contract`. Ensuite l'option `--module` du wrapper réclamait un bilan de tests Odoo absent par conception (`live-verification.evidence.json`, script sorti 0 avec 88 checks, wrapper failed). La preuve finale emploie uniquement `--scope`, conformément à une vérification générique. Les deux tentatives sont conservées pour traçabilité ; elles ne sont ni un défaut métier ni des tests Odoo rouges supplémentaires. Aucune preuve de tests neuve fabriquée.

## Limites

Ce résultat est une preuve locale de données synthétiques après restauration effective par dump/restore ; pas une restauration client, pas une recette complète, pas une livraison distante. Les valeurs sont prouvées stables ; aucune affirmation de zéro écriture SQL pendant l'update développeur n'est faite. La QA fraîche, elle, est strictement en transaction READ ONLY. Ressources laissées disponibles pour l'orchestrateur.
