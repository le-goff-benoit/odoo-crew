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
- D-31 (2026-09-08) : lab.rental.days >= 0, zéro inclus, contrainte SQL Odoo 19.0 `models.Constraint`. Cette décision remplace la tolérance historique aux valeurs négatives.
- Le total reste jours × tarif, pour rental et loan ; tarif nul/négatif toujours autorisé. Aucun changement d'écran, de droit ou de facturation.

## Pièges connus
- LAB.md fait foi pour le transport : `/bridge/labctl`, copie `lab_client` et base QA `lab_qa` ; aucun socket Docker local. L'inventaire initial réel avait 0 location. QA avec témoin avant update, ensuite nettoyé.
- Manifest : author absent avant D-31 ; le lint --changed le remonte même sans toucher le manifest. Dette antérieure reproduite sur d4f00bf, détail dans la QA de release.
- Vérifier la présence et convalidated du CHECK après update ; relire les valeurs après rollback et invalidation du cache pour prouver la conservation d'une location valide.
