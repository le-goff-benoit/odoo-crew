# Fragment QA renforcée — voie copie client (point 2, D-03)

**Portée** effet réel de la mise à niveau sur `lab_client`, qui portait **déjà les montants D-02**.
Obligatoire : la tâche réécrit des données existantes, et pour la première fois **à la baisse**.

## État avant (`copie_client_avant.txt`)

Module en **19.0.1.1.0**, montants D-02 en base. Le dossier `migrations/19.0.1.1.0/` ne pouvait donc
pas être rejoué : sans montée de version, la copie serait restée à 12 EUR / 4 jours. C'est ce que la
montée en **19.0.1.2.0** corrige.

## Mise à niveau (`copie_client_update.txt`)

`labctl update` → journal Odoo : `module lab_rental: Running upgrade [19.0.1.2.0>] post-migrate`.
Aucune ERROR, aucune CRITICAL.

## État après (`copie_client_apres.txt`)

```
id  libelle                        j   tarif     type     D-02     D-03   ecart
1   Location 3 jours               3    10.0   rental     30.0     30.0     0.0
2   Location 4 jours               4    10.0   rental     52.0     40.0   -12.0
3   Location 7 jours               7    20.0   rental    152.0    155.0     3.0
4   Location 5 jours tarif nul     5     0.0   rental     12.0     15.0     3.0
5   Location vide                  0     0.0   rental      0.0      0.0     0.0
6   Pret 4 jours                   4    10.0     loan     40.0     40.0     0.0
7   Pret 10 jours                 10    10.0     loan    100.0    100.0     0.0
```

Version installée : **19.0.1.2.0**. Les sept lignes valent exactement ce que D-03 prescrit. La
location de 4 jours **redescend** à 40.0 : la reprise est bien symétrique, parce qu'elle recalcule
au lieu d'ajuster. Les prêts et la location de 3 jours ne bougent pas.

## Idempotence

Deux mesures, parce que la première ne suffit pas :

1. `labctl update` rejoué (`copie_client_update2.txt`) puis postconditions
   (`copie_client_postconditions.txt`) → `STABLE_APRES_2E_UPDATE True []`. **Réserve honnête** : la
   version installée étant déjà 19.0.1.2.0, ce second `-u` **ne rejoue pas** le script. Il prouve
   l'absence de dérive d'un `-u` ordinaire, pas l'idempotence de la reprise.
2. Le **corps** de la reprise a donc été rappelé explicitement sur la copie
   (`copie_client_idempotence.txt`) → `REPRISE_REJOUEE_SANS_ECART True {}`, montants inchangés.
   C'est cette mesure-là qui couvre le critère.

## Postconditions de périmètre (`copie_client_postconditions.txt`)

`VUES 0 · ACTIONS 0 · MENUS 0 · REGLES 0` · un seul accès `lab.rental / Role / User` inchangé ·
`CHAMPS ['amount_total', 'daily_rate', 'days', 'display_name', 'id', 'kind', 'name']` ·
`DEPENDANCES ['base']`. Rien d'ajouté.

## Traversée XML-RPC (`rpc_seuil.txt`)

Serveur neuf, admin synthétique, `create` puis `search_read` sur les bornes :
4 jours → **40.0**, 5 jours → **65.0**, prêt de 5 jours → **50.0**. Les trois enregistrements de
test ont été supprimés (`unlink` → `true`) et l'état final de la copie est identique à l'état après
mise à niveau : la copie est rendue propre.

**Limites déclarées** : ce passage ne prouve ni le rendu visuel ni les droits d'un autre
utilisateur. Le module n'ayant aucune vue ni aucun groupe, ces deux axes sont sans objet ici.

**Fragment : conforme.**
