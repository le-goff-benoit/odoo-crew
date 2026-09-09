# Fragment QA copie client — frais de préparation (D-02)

Copie synthétique `lab_client`, module installé en `19.0.1.0.0` avant la tâche. Écritures autorisées
sur ce bac (`decisions/2026-09-08.md` : « tous les enregistrements du bac sont des essais
modifiables »). Ceci n'est ni une production, ni une confirmation de déploiement.

## Constat déterminant : `-u` seul ne corrige pas un champ stocké

La copie a d'abord été mise à niveau **avec le nouveau code mais sans script de reprise**. Résultat
relevé par XML-RPC : « Location 4 jours » restait à **40.0**. Modifier le corps d'un compute ne
réécrit pas les valeurs déjà en base. Sans reprise, la fonctionnalité aurait été verte en test et
fausse chez le client sur tout l'historique. D'où `migrations/19.0.1.1.0/post-migrate.py` et la
montée de version du manifest.

## Avant / après la reprise

Journal de mise à niveau : `module lab_rental: Running upgrade [19.0.1.1.0>] post-migrate`.

| id | Libellé | Jours | Tarif | Type | Avant | Après | Écart | Attendu D-02 |
|---|---|---|---|---|---|---|---|---|
| 1 | Location 3 jours | 3 | 10.0 | rental | 30.0 | 30.0 | 0.0 | 0.0 (sous le seuil) |
| 2 | Location 4 jours | 4 | 10.0 | rental | 40.0 | 52.0 | **12.0** | 12.0 (borne incluse, Q1) |
| 3 | Location 7 jours | 7 | 20.0 | rental | 140.0 | 152.0 | **12.0** | 12.0 (forfait, pas 7 %) |
| 4 | Location 5 jours tarif nul | 5 | 0.0 | rental | 0.0 | 12.0 | **12.0** | 12.0 (indépendant du tarif) |
| 5 | Location vide | 0 | 0.0 | rental | 0.0 | 0.0 | 0.0 | 0.0 |
| 6 | Prêt 4 jours | 4 | 10.0 | loan | 40.0 | 40.0 | 0.0 | 0.0 (prêts exclus, Q2) |
| 7 | Prêt 10 jours | 10 | 10.0 | loan | 100.0 | 100.0 | 0.0 | 0.0 |

Seules les locations de 4 jours et plus ont bougé, et de **12.0 exactement**. Aucun écart de 7 %
(id 3 aurait pris +9.80 sous D-01, id 4 aurait pris 0.0).

## Idempotence
Deuxième `labctl update` : `STABLE_APRES_2E_UPDATE True []` — aucun montant ne dérive, le forfait
n'est pas cumulé.

## Postconditions sur la copie
```
VERSION_INSTALLEE 19.0.1.1.0 installed
VUES 0 · ACTIONS 0 · MENUS 0 · RÈGLES 0
ACCES [('lab.rental', 'Role / User', True, True, True, True)]   ← identique à l'état d'origine
CHAMPS ['amount_total', 'daily_rate', 'days', 'display_name', 'id', 'kind', 'name']
```
Aucun écran, aucun droit, aucun champ ajouté : « sans changer les écrans » est vérifié en base, pas
seulement dans le diff. Aucune facture, aucune écriture comptable : le modèle n'a aucun lien vers
`account.*`.

## Contrôle par XML-RPC réel (création, pas seulement recalcul)
`create` d'une location de 4 jours à 10.0 → relecture `amount_total = 52.0`. Le forfait s'applique
donc aussi aux enregistrements neufs à travers la pile complète, pas uniquement à la reprise.
Enregistrement de contrôle supprimé après lecture (`unlink` → `true`) : la copie est rendue propre.

## Limites de cette voie
Le passage RPC ne prouve ni le rendu visuel, ni le comportement pour un autre utilisateur que
l'admin synthétique. Sans objet ici : la tâche ne touche ni vue ni droit, et les postconditions
ci-dessus le confirment en base.

**Verdict de la voie : VERT.**
