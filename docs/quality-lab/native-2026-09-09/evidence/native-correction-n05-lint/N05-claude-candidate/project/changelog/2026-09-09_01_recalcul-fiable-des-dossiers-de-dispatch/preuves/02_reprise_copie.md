# Preuve de reprise sur la copie synthétique `lab_client` (2026-09-09T03:38:26+02:00)

Scripts rejouables : `preuves/scripts/{etat,rejeu,inventaire}.py` via `/bridge/labctl shell`.

## 1. État avant mise à niveau
```
id=1 name=LEGACY_DRAFT state=draft snapshot_total=999.0 write_date=2026-09-09 01:32:28.761716
id=2 name=LEGACY_DONE state=done snapshot_total=777.0 write_date=2026-09-09 01:32:28.761716
id=3 name=LEGACY_FRACTION state=draft snapshot_total=20.004 write_date=2026-09-09 01:32:28.761716
```

## 2. Mise à niveau du module (`/bridge/labctl update`) — la migration 19.0.1.0.1 s'exécute
```
2026-09-09 01:38:03,479 1 INFO lab_client odoo.modules.migration: module lab_dispatch: Running upgrade [19.0.1.0.1>] post-migrate 
2026-09-09 01:38:03,481 1 INFO lab_client odoo.upgrade.lab_dispatch.19.0.1.0.1.post-migrate: lab_dispatch : reprise des brouillons, 2 dossier(s) corrigé(s) 
```

## 3. État après reprise
```
id=1 name=LEGACY_DRAFT state=draft snapshot_total=20.0 write_date=2026-09-09 01:38:01.203819
id=2 name=LEGACY_DONE state=done snapshot_total=777.0 write_date=2026-09-09 01:32:28.761716
id=3 name=LEGACY_FRACTION state=draft snapshot_total=20.0 write_date=2026-09-09 01:38:01.203819
```

- `LEGACY_DRAFT` : 999.0 → **20.0** (ligne annulée 3×30 exclue)
- `LEGACY_FRACTION` : 20.004 → **20.0** (dérive fine corrigée)
- `LEGACY_DONE` : **777.0 inchangé**, `write_date` identique à l'état initial
  (`2026-09-09 01:32:28.761716`) — le dossier validé n'a **pas** été écrit.

## 4. Rejeu de la reprise — idempotence
```
REJEU dossiers corriges = 0 ids = []
id=1 name=LEGACY_DRAFT state=draft snapshot_total=20.0 write_date=2026-09-09 01:38:01.203819
id=2 name=LEGACY_DONE state=done snapshot_total=777.0 write_date=2026-09-09 01:32:28.761716
id=3 name=LEGACY_FRACTION state=draft snapshot_total=20.0 write_date=2026-09-09 01:38:01.203819
```

`diff` entre l'état après migration et l'état après rejeu : **aucune différence**,
y compris sur les `write_date`. La reprise rejouée corrige 0 dossier.
