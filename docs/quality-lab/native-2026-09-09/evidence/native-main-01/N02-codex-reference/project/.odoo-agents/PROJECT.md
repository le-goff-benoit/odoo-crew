# Projet work — fiche de contexte

> Lue en premier par les agents Odoo. Le bloc « relevé » est régénéré par `odoo_project_scan.py` ; tout ce qui est en dessous est écrit à la main et conservé.

<!-- odoo-agents:relevé début — régénéré par odoo_project_scan.py -->
## Relevé du 2026-09-09

- **Racine** : `/work`
- **Série Odoo** : **19.0** (déterminée par __manifest__.py)
- **Sources de référence** : `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Stack de QA** : image `odoo-qa:19.0`, base `odoo_qa_19_0`
- branche `master`, 1 commits, dernier : 8acff8e 2026-09-09 Dossier synthétique initial
- fichiers les plus touchés sur 6 mois : `lab_dispatch/__init__.py` (1), `lab_dispatch/__manifest__.py` (1), `lab_dispatch/models/__init__.py` (1), `lab_dispatch/models/business.py` (1), `lab_dispatch/security/ir.model.access.csv` (1)
- **Changelog** : 1 release(s), dernier `2026-09-09_01_recalcul-fiable-des-brouillons`, **ouvert** : `2026-09-09_01_recalcul-fiable-des-brouillons`

## Modules custom (1)

### `lab_dispatch`

- version `19.0.1.0.0` — licence `LGPL-3` — auteur ?
- chemin : `lab_dispatch`
- dépendances : 0 community, 0 enterprise
- modèles créés (2) : `lab.dispatch`, `lab.dispatch.line`
- sécurité : 2 ligne(s) d'accès, 0 groupe(s) déclaré(s)
- tests : 1 fichier(s) — `test_recalculate.py`
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
# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- D-12 : total des brouillons = somme quantity × price des lignes non annulées ; validés définitivement figés, même en sélection mixte.
- Reprise explicite locale uniquement, script dans `changelog/2026-09-09_01_recalcul-fiable-des-brouillons/reprise_brouillons.py` ; aucune migration automatique ni version incrémentée avant clôture.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- Le transport réel du laboratoire est `/bridge/labctl` : QA sur lab_qa et copie sur lab_client (les commandes de stack génériques du relevé ne s'appliquent pas ; voir LAB.md).
- `qa --quick` peut produire un faux vert avec zéro test si la base existe mais le module n'est pas installé : faire une installation explicite puis contrôler le nombre de tests.
- La mise à niveau seule ne reprend pas snapshot_total ; exécuter le script autorisé. Preuve obtenue : 999 → 20, validé 777 conservé, second passage sans écriture.
