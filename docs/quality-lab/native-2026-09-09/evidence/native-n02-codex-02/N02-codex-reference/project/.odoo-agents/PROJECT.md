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
- **Changelog** : 1 release(s), dernier `2026-09-09_01_recalcul-des-brouillons`, **ouvert** : `2026-09-09_01_recalcul-des-brouillons`

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
## Compréhension métier
Projet entièrement synthétique pour le banc.
Deux dossiers initiaux : LEGACY_DRAFT et LEGACY_DONE, chacun avec une ligne active et une annulée. Le snapshot validé est historique ; il ne doit pas être aligné sur les lignes.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-12 : action_recalculate traite uniquement les brouillons et exclut les lignes annulées. Sélections mixtes acceptées, validés ignorés sans écriture ni recalcul. Aucune modification de droits ou d'état.
Reprise locale réalisée le 09/09/2026 : brouillon 999 → 20, validé conservé à 777 ; second passage sans modification. Release 2026-09-09_01_recalcul-des-brouillons ouverte, point 1 validé (qa.md).
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
LAB.md fait foi sur le transport : utiliser /bridge/labctl ; les bases effectives sont lab_client (copie synthétique) et lab_qa (tests), malgré les noms génériques du relevé automatique ci-dessus.
Sur ce banc, --quick peut annoncer un succès avec zéro test lorsque la base existe mais que le module n'est pas installé ; installer sans --quick, puis vérifier le nombre réel de tests.
Corriger l'action ne reprend pas le Float stocké. Le script explicite et rejouable de la release est limité à lab_client ; l'update seul ne l'exécute pas.
Lint : ruff 0.16.6 disponible dans /work/.venv-lint/bin ; une dette préexistante hors diff demeure (auteur absent du manifest).
