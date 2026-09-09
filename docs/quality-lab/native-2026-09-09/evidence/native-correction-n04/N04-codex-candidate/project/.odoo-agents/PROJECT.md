# Projet work — fiche de contexte

> Lue en premier par les agents Odoo. Le bloc « relevé » est régénéré par `odoo_project_scan.py` ; tout ce qui est en dessous est écrit à la main et conservé.

<!-- odoo-agents:relevé début — régénéré par odoo_project_scan.py -->
## Relevé du 2026-09-09

- **Racine** : `/work`
- **Série Odoo** : **19.0** (déterminée par __manifest__.py)
- **Sources de référence** : `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Stack de QA** : image `odoo-qa:19.0`, base `odoo_qa_19_0`
- branche `master`, 1 commits, dernier : d4f00bf 2026-09-09 Dossier synthétique initial
- fichiers les plus touchés sur 6 mois : `lab_rental/__init__.py` (1), `lab_rental/__manifest__.py` (1), `lab_rental/models/__init__.py` (1), `lab_rental/models/business.py` (1), `lab_rental/security/ir.model.access.csv` (1)
- **Changelog** : 1 release(s), dernier `2026-09-09_01_jours-de-location-non-negatifs`, **ouvert** : `2026-09-09_01_jours-de-location-non-negatifs`

## Modules custom (1)

### `lab_rental`

- version `19.0.1.0.0` — licence `LGPL-3` — auteur ?
- chemin : `lab_rental`
- dépendances : 0 community, 0 enterprise
- modèles créés (1) : `lab.rental`
- sécurité : 1 ligne(s) d'accès, 0 groupe(s) déclaré(s)
- tests : 1 fichier(s) — `test_rental_days.py`
- dette lint (série 19.0) : 1 erreur(s), 0 avertissement(s), 0 info(s)

## Commandes utiles sur ce projet

```bash
python3 /home/blegoff/.odoo19-agents/scripts/odoo_briefing.py /work      # le premier réflexe
export ODOO_ADDONS_DIR=/work
RELEASE=$(/home/blegoff/.odoo19-agents/scripts/odoo-release.sh current /work)
/home/blegoff/.odoo19-agents/scripts/odoo-lint.sh --changed "$(cat $RELEASE/.base)" <module>
/home/blegoff/.odoo19-agents/scripts/odoo-test.sh <module> --update --tags /<module>:<TestClasse>   # QA de tâche
/home/blegoff/.odoo19-agents/scripts/odoo-recette.sh <module> --release "$RELEASE" [--db <copie_client>]   # clôture
```

<!-- odoo-agents:relevé fin -->
# Éole
<!-- odoo-agents:relevé fin -->
## Métier
Coopérative synthétique ; demande et décision D-31 dans decisions/2026-09-08.md.

## Décisions actées
- D-31 — Luc Roy, `decisions/2026-09-08.md`, confirmée par la demande du 2026-09-09 : jours >= 0 par contrainte SQL, zéro inclus ; tarifs et total jours × tarif inchangés, locations et prêts concernés. Remplace la tolérance historique du 2026-08-01 ; aucune question restante.
- Série 19.0 du manifest ; copie synthétique lab_client via /bridge/labctl (LAB.md). Aucun accès production. Inventaire initial : 0 location et aucun CHECK sur lab_rental.

## Pièges connus
- D-31 réalisée dans lab_rental : CHECK days >= 0, testé en création et modification avec CheckViolation, flush protégé, rollback et relecture. Contrainte vérifiée validée après update sur lab_client ; copie remise à zéro location.
- Manifest d'origine sans author : le lint global le remonte même en --changed ; contre-épreuve HEAD dans la release 2026-09-09_01. Ruff sur le diff est vert. Dette antérieure conservée, aucun auteur inventé.
