# Fragment QA — voie copie client (données existantes)

Copie synthétique `lab_client`, seule base autorisée par D-12 et par la demande.
Preuves : `preuves/02_reprise_copie.md`, `preuves/06_controle_final_copie.txt`.

## Reprise des brouillons existants

Déclenchée par la mise à niveau du module (`/bridge/labctl update`), qui exécute
`migrations/19.0.1.0.1/post-migrate.py` :
`odoo.upgrade.lab_dispatch.19.0.1.0.1.post-migrate: reprise des brouillons, 2 dossier(s) corrigé(s)`.

| Dossier | État | Avant | Après | Attendu D-12 | Verdict |
|---|---|---|---|---|---|
| `LEGACY_DRAFT` | brouillon | 999.0 | **20.0** | 20.0 (ligne 3×30 annulée exclue) | ✅ |
| `LEGACY_FRACTION` | brouillon | 20.004 | **20.0** | 20.0 | ✅ |
| `LEGACY_DONE` | validé | 777.0 | **777.0** | figé, aucune écriture | ✅ |

`LEGACY_DONE` : `write_date` toujours `2026-09-09 01:32:28.761716`, identique à l'état
initial relevé avant toute intervention. Le dossier validé n'a donc pas seulement gardé sa
valeur : il n'a **pas été écrit du tout**. Son état n'a pas non plus été modifié.

## Idempotence

Second appel de `_reprise_snapshot_brouillons()` sur la même copie :
`REJEU dossiers corriges = 0 ids = []`. Le `diff` entre l'état après migration et l'état
après rejeu est vide, `write_date` comprises.

## Sélection mixte sur données réelles

`env['lab.dispatch'].search([]).action_recalculate()` sur les 3 dossiers (2 brouillons +
1 validé) : aucune exception, aucune valeur ni `write_date` modifiée (les brouillons étaient
déjà justes, le validé est ignoré).

## Effets de bord

- Les 5 lignes `lab.dispatch.line` sont intactes (`write_date` toutes à l'état initial) :
  la reprise n'a touché aucune ligne.
- Aucun autre modèle écrit ; aucun changement de droits (`ir.model.access.csv` non modifié).
- Module `lab_dispatch` en état `installed`, `latest_version = 19.0.1.0.1`.
- Aucune écriture hors de `lab_client` : la base QA `lab_qa` est séparée, aucune autre base
  n'a été touchée. Aucun accès production, aucun déploiement.

**Fragment : VERT.**
