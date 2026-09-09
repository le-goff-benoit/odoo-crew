# Fragment QA — voie scénarios Studio (point 1)

Rôle : odoo-tester, mode `graph-lane-studio-runtime`. Scénarios rejoués sur `lab_client`.

## Scénario RPC — `test_point1_rpc.py` (XML-RPC réel, admin)
**VERT, 18/18.** Couvre C9, C10, C13 et prouve la limite d'accès (V6).
Rouge avant la construction (V1), vert après.

## Scénario ORM — `test_point1_orm.py` (`/bridge/labctl shell`, superuser)
**VERT, 12/12.** Couvre C1 à C8. Chaque valeur est relue **dans la colonne SQL** après
`flush_recordset()` : c'est ce qui prouve le stockage, pas un simple recalcul de cache.
Valeurs attendues issues de `decisions/2026-09-08.md` (D-22), pas du calcul testé.
Rouge avant la construction (précondition), vert après.

Pourquoi ce transport et non XML-RPC : `x_lab_request` n'a aucune ACL et D-22 interdit
d'en créer ; aucun appel RPC ne peut créer ni relire un enregistrement de ce modèle.
Ce n'est pas un contournement mais la conséquence assumée du périmètre — la limite est
elle-même prouvée (V6) et remontée à l'humain.

## Écran
**Aucune capture** : 0 `ir.ui.view` sur `x_lab_request` avant comme après, aucune vue
créée ni modifiée. La revue le prévoyait (§10, « rien de visible »). Le rendu visuel et
les droits d'un autre utilisateur ne sont donc **pas** couverts par cette voie.

## Propreté de la copie
Données de test « — recette » supprimées : **0 enregistrement restant** sur `x_lab_request`.
`studio_customization` contient les 4 XML-ID `lab_seed_*` d'origine + 1 seul ajout.

Preuves : `studio/preuves/test_point1_rpc.log`, `studio/preuves/test_point1_orm.log`

**Verdict de la voie : VERT.**
