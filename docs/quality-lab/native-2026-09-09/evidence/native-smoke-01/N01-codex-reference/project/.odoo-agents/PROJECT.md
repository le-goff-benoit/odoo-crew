# Projet work — fiche de contexte

> Lue en premier par les agents Odoo. Le bloc « relevé » est régénéré par `odoo_project_scan.py` ; tout ce qui est en dessous est écrit à la main et conservé.

<!-- odoo-agents:relevé début — régénéré par odoo_project_scan.py -->
## Relevé du 2026-09-09

- **Racine** : `/work`
- **Série Odoo** : **19.0** (déterminée par __manifest__.py)
- **Sources de référence** : `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Stack de QA** : image `odoo-qa:19.0`, base `odoo_qa_19_0`
- branche `master`, 1 commits, dernier : c1c4140 2026-09-09 Dossier synthétique initial
- fichiers les plus touchés sur 6 mois : `lab_rental/__init__.py` (1), `lab_rental/__manifest__.py` (1), `lab_rental/models/__init__.py` (1), `lab_rental/models/business.py` (1), `lab_rental/security/ir.model.access.csv` (1)
- **Changelog** : 1 release(s), dernier `2026-09-09_01_frais-de-preparation-d-02`, **ouvert** : `2026-09-09_01_frais-de-preparation-d-02`

## Modules custom (1)

### `lab_rental`

- version `19.0.1.0.0` — licence `LGPL-3` — auteur ?
- chemin : `lab_rental`
- dépendances : 0 community, 0 enterprise
- modèles créés (1) : `lab.rental`
- sécurité : 1 ligne(s) d'accès, 0 groupe(s) déclaré(s)
- tests : 1 fichier(s) — `test_preparation_fee.py`
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
# Atelier Boréal — frais de préparation des locations
## Compréhension métier
Projet entièrement synthétique pour le banc.
Le modèle autonome lab.rental stocke un montant HT en EUR, sans écrans ni facturation spécifiques.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-02 réalisée : jours × tarif + 12 EUR pour rental dès 4 jours inclus ; prêts exclus. Pas d'arrondi supplémentaire ; jours et tarif positifs ou nuls.
Release 2026-09-09_01_frais-de-preparation-d-02 ouverte, point 1 validé ; version 19.0.1.0.0 conservée jusqu'à la clôture.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
LAB.md fait foi sur le transport : /bridge/labctl, base QA lab_qa et copie synthétique lab_client ; pas d'accès direct au Docker du relevé générique.
La copie ne contenait initialement aucune location : trois fixtures ont été créées avant update puis nettoyées après validation.
Changer la formule stockée ne recalcule pas l'existant avec -u seul : reprise ORM idempotente livrée dans la release, garde lab_client, validée deux fois.
Le mode --quick du banc choisit -u si la base existe même sans module installé : zéro test n'est pas une preuve. Commande validée : labctl qa lab_rental --update --tags /lab_rental:TestPreparationFee (7/7).
