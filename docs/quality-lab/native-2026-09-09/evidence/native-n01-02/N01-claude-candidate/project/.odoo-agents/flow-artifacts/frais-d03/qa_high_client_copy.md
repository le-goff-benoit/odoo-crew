# Fragment QA — voie COPIE CLIENT (D-03, point n°2)

Mode `graph-lane-client-copy`. Copie synthétique locale `lab_client`, écriture
autorisée sur cette copie. **Aucune production, aucun déploiement** (D-03 :
« validation locale seulement »).

## Pourquoi cette voie est obligatoire ici

`amount_total` est stocké, et le point n°1 de cette même release a **déjà écrit**
les valeurs D-02 en base. D-03 ne se contente pas d'ajouter : il **corrige des
valeurs que la release a produites**, et dans les deux sens.

## Le piège, vérifié avant travaux

Version du module installée sur `lab_client` mesurée **avant** toute
modification : **`19.0.1.1.0`**, égale à celle du manifest
(`preuves/d03_copie_client_avant.txt`). La reprise du point n°1
(`migrations/19.0.1.1.0/post-migrate.py`) **ne pouvait donc pas se rejouer** : un
script de `migrations/` ne s'exécute que si la version installée est strictement
inférieure à celle du manifest.

**C'est exactement pourquoi la QA du point n°1 ne suffit pas pour livrer D-03.**
Livré sans nouvel incrément, le changement aurait laissé les sept totaux à leurs
valeurs D-02 — sans la moindre erreur dans les logs.

Corrigé par `migrations/19.0.1.2.0/` + manifest `19.0.1.2.0`.

## La reprise s'est-elle réellement exécutée ? — CA11

Preuve dans le log de `labctl update`, pas déduite du résultat
(`preuves/d03_copie_client_update.txt`) :

```
odoo.modules.migration: module lab_rental: Running upgrade [19.0.1.2.0>] post-migrate
```

Version installée après mise à jour : **`19.0.1.2.0`**.

## Mesure avant / après — CA9

Prédiction écrite dans la revue **avant** la modification (simulation en lecture
seule, `preuves/d03_copie_client_avant.txt`), puis confrontée au réel.

| id | enregistrement | jours | avant (D-02) | après (D-03) | attendu | delta |
|---|---|---|---|---|---|---|
| 1 | Location 5 jours × 10 | 5 | 62,00 | **65,00** | 65,00 ✅ | +3,00 |
| 2 | Location 4 jours × 10 | 4 | 52,00 | **40,00** | 40,00 ✅ | **−12,00** |
| 3 | Location 3 jours × 10 | 3 | 30,00 | 30,00 | 30,00 ✅ | 0 |
| 4 | Location 4 jours tarif nul | 4 | 12,00 | **0,00** | 0,00 ✅ | **−12,00** |
| 5 | Prêt 10 jours × 10 | 10 | 100,00 | 100,00 | 100,00 ✅ | 0 |
| 6 | Prêt 4 jours × 10 | 4 | 40,00 | 40,00 | 40,00 ✅ | 0 |
| 7 | Location 0 jour | 0 | 0,00 | 0,00 | 0,00 ✅ | 0 |

- **Total général : 296,00 → 275,00. Delta net −21,00.**
- **3 enregistrements touchés sur 7**, dont **2 à la baisse**.
- **Prêts inchangés** : contrôle programmatique `prets inchanges = True`.
- **Écarts par rapport à la prédiction : 0.** Les sept valeurs sont celles
  annoncées dans la revue avant d'écrire une ligne.
- Lecture **SQL directe** en fin de contrôle :
  `[(1, 65.0), (2, 40.0), (3, 30.0), (4, 0.0), (5, 100.0), (6, 40.0), (7, 0.0)]`
  — les valeurs sont en base, pas en cache.

Preuve : `preuves/d03_copie_client_apres.txt`.

## Idempotence — CA10

`post-migrate.py` de `19.0.1.2.0` chargé et `migrate()` appelée **deux fois de
plus** : totaux strictement identiques, total général toujours 275,00
(`preuves/d03_copie_client_idempotence.txt`). La forme « réappliquer la formule »
plutôt que « ajouter un delta » est ce qui rend l'idempotence vraie, y compris sur
la correction à la baisse.

## Verdict de la voie

**VERT.** La reprise s'exécute, corrige dans les deux sens, atteint exactement les
valeurs prédites et se rejoue sans dériver.

**Limite à ne pas masquer** : `lab_client` est une copie **synthétique** de sept
enregistrements, peuplée par la QA du point n°1. Elle prouve le mécanisme de
reprise et la correction bidirectionnelle, **pas** le comportement sur un parc réel.
La reprise fait un `search([])` suivi d'un recompute en mémoire : à l'échelle de
centaines de milliers de locations, elle demanderait un traitement par lots.
