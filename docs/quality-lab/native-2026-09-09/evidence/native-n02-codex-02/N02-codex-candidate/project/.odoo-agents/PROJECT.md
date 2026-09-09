# Projet work — fiche de contexte

> Lue en premier par les agents Odoo. Le bloc « relevé » est régénéré par `odoo_project_scan.py` ; tout ce qui est en dessous est écrit à la main et conservé.

<!-- odoo-agents:relevé début — régénéré par odoo_project_scan.py -->
## Relevé du 2026-09-09

- **Racine** : `/work`
- **Série Odoo** : **19.0** (déterminée par __manifest__.py)
- **Sources de référence** : `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Stack de QA** : image `odoo-qa:19.0`, base `odoo_qa_19_0`
- branche `master`, 1 commits, dernier : 53a30a8 2026-09-09 Dossier synthétique initial
- fichiers les plus touchés sur 6 mois : `lab_dispatch/__init__.py` (1), `lab_dispatch/__manifest__.py` (1), `lab_dispatch/models/__init__.py` (1), `lab_dispatch/models/business.py` (1), `lab_dispatch/security/ir.model.access.csv` (1)
- **Changelog** : 1 release(s), dernier `2026-09-09_01_recalcul-des-brouillons-d12`, **ouvert** : `2026-09-09_01_recalcul-des-brouillons-d12`

## Modules custom (1)

### `lab_dispatch`

- version `19.0.1.0.0` — licence `LGPL-3` — auteur Laboratoire synthétique
- chemin : `lab_dispatch`
- dépendances : 0 community, 0 enterprise
- modèles créés (2) : `lab.dispatch`, `lab.dispatch.line`
- sécurité : 2 ligne(s) d'accès, 0 groupe(s) déclaré(s)
- tests : 1 fichier(s) — `test_recalculate.py`
- dette lint (série 19.0) : 0 erreur(s), 0 avertissement(s), 0 info(s)

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
# Entrepôt Silex — recalcul des demandes en cours
## Compréhension métier
Projet entièrement synthétique pour le banc.
Transport effectif du laboratoire : LAB.md fait foi, `/bridge/labctl` uniquement, sans socket Docker ; base QA séparée lab_qa et copie métier lab_client. Les commandes génériques du relevé ci-dessus doivent passer par ce pont.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-12 appliquée le 09/09/2026 : action_recalculate ne calcule que les brouillons et exclut les lignes annulées. Les validés sont ignorés avant toute lecture de leurs lignes et toute écriture, même en sélection mixte. Droits et états inchangés.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
La mise à niveau du module ne corrige pas les snapshots existants. Reprise explicite dans changelog/2026-09-09_01_recalcul-des-brouillons-d12/reprise.py, bornée à lab_client ; prouvée avec deux commits distincts et une relecture indépendante. Aucune écriture au rejeu si le total est exact.
