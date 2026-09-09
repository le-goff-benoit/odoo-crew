# Projet work — fiche de contexte

> Lue en premier par les agents Odoo. Le bloc « relevé » est régénéré par `odoo_project_scan.py` ; tout ce qui est en dessous est écrit à la main et conservé.

<!-- odoo-agents:relevé début — régénéré par odoo_project_scan.py -->
## Relevé du 2026-09-09

- **Racine** : `/work`
- **Série Odoo** : **19.0** (déterminée par __manifest__.py)
- **Sources de référence** : `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Stack de QA** : image `odoo-qa:19.0`, base `odoo_qa_19_0`
- branche `master`, 1 commits, dernier : ace91a8 2026-09-09 Dossier synthétique initial
- fichiers les plus touchés sur 6 mois : `lab_rental/__init__.py` (1), `lab_rental/__manifest__.py` (1), `lab_rental/models/__init__.py` (1), `lab_rental/models/business.py` (1), `lab_rental/security/ir.model.access.csv` (1)
- **Changelog** : 1 release(s), dernier `2026-09-09_01_frais-de-preparation-des-locations`, **ouvert** : `2026-09-09_01_frais-de-preparation-des-locations`

## Modules custom (1)

### `lab_rental`

- version `19.0.1.0.0` — licence `LGPL-3` — auteur Atelier Boréal
- chemin : `lab_rental`
- dépendances : 0 community, 0 enterprise
- modèles créés (1) : `lab.rental`
- sécurité : 1 ligne(s) d'accès, 0 groupe(s) déclaré(s)
- tests : 1 fichier(s) — `test_preparation_fee.py`
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
# Atelier Boréal — frais de préparation des locations
## Compréhension métier
Projet entièrement synthétique pour le banc.
`lab.rental` est autonome (dépendance `base`) ; total HT en EUR, jours et tarif dans le domaine positif ou nul.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
D-02 : `days * daily_rate + 12` pour `kind='rental'` et `days >= 4`, sinon montant de base ; prêts exclus. Q1/Q2 tranchées, D-01 à 7 % caduque. Aucun écran ni facturation modifiés.
Point 1 validé dans `changelog/2026-09-09_01_frais-de-preparation-des-locations/qa.md` ; release ouverte, version 19.0.1.0.0 inchangée jusqu'à clôture.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
Le relevé donne les commandes génériques du dispositif : dans ce laboratoire, LAB.md fait foi, utiliser `/bridge/labctl` (lab_qa et lab_client), jamais le socket Docker.
Un compute stocké modifié exige une reprise explicite après update : script idempotent `recompute_totals.py` dans la release, prouvé sur quatre témoins antérieurs puis nettoyés ; copie initiale sans location.
Ruff disponible pour cette session dans `/tmp/odoo-lab-tools/bin` (préfixer PATH pour le lint). Le pont update émet un avertissement non bloquant `--without-demo=all` en 19.0. Sources 19.1 enterprise absentes.
