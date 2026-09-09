# Briefing — work

- **Série** : **19.0** (origine : __manifest__.py) · sources `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Racine** : `/work`
- **Release** : `changelog/2026-09-09_01_frais-de-preparation-des-locations` (base git `ace91a8b81`)
  1. Calcul stocké des frais de préparation D-02 et reprise des essais [VALIDÉ — TestPreparation 8/8, lint et update/reprise copie OK]
- **Instances déclarées** : Aucun environnement déclaré pour work. → odoo_instance.py add /work
- **Inbox** (`inbox/`, déposé par l'humain) : vide

## Formes attendues en 19.0

**Différences avec le guide 19.0** : `ir.model.access.csv` + `ir.rule`
Formes en vigueur : `invisible="expr"` (plus d'`attrs`/`states`) · `_compute_display_name` (plus de `name_get`) · `<list>` (plus de `<tree>`) · `<chatter/>` · `self.env._()` disponible · `@api.readonly` disponible · `models.Constraint` (plus de `_sql_constraints`) · objet `Domain` · `res.groups.privilege` (plus de `category_id`) · `res.users.group_ids` (et non `groups_id`) · `self.env.cr` obligatoire (plus de `self._cr`) · `hr.version` (plus de `hr.contract`)

## Modules (relevé)

- `lab_rental` · version `19.0.1.0.0` · dépendances : 0 community, 0 enterprise · modèles créés (1) : `lab.rental` · tests : 1 fichier(s) · dette lint (série 19.0) : 1 erreur(s), 0 avertissement(s), 0 info(s)

## Ce que le projet sait déjà (PROJECT.md, écrit à la main)

# Atelier Boréal — frais de préparation des locations

## Compréhension métier
Projet entièrement synthétique pour le banc. Modèle autonome lab.rental, module lab_rental dépendant uniquement de base ; montants HT en EUR.

## Décisions actées
D-02 (decisions/2026-09-08.md) remplace D-01 : jours × tarif + 12 EUR uniquement pour les locations dès 4 jours inclus ; prêts exclus ; aucun arrondi supplémentaire. Entrées positives ou nulles, sans écran ni facture. Release à laisser ouverte.

## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.

Le total est déjà stocké : changer le compute seul ne reprend pas les anciennes valeurs. Migration prévue en 19.0.1.0.1 ; incrément du manifest différé à la clôture et migration exécutée explicitement sur la copie pendant cette tâche.

Laboratoire : le transport effectif est /bridge/labctl (LAB.md), bases lab_qa et lab_client ; les commandes Docker génériques du relevé ne sont pas applicables ici. Vérifier le nombre de tests : --quick sur une base sans module installé peut annoncer du vert avec zéro test.

## Journal — 3 entrée(s), les 3 dernières

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation D-02
**Demande** : appliquer D-02 au total stocké de lab_rental, sans écran ni facture ; laisser la release ouverte.
**Fait** : forfait 12 EUR dès 4 jours pour les locations, prêts exclus ; contraintes non négatives, 8 tests métier et migration idempotente 19.0.1.0.1.
**Verdict** : VALIDÉ — lint complet vert, installation/mise à jour QA, 8/8 tests sans skip ; update, double reprise et relecture SQL/ORM sur copie synthétique réussis, essais nettoyés.
**Appris** : D-02 remplace D-01 (7 %) ; un compute stocké modifié seul ne recalcule pas l'existant.
**Candidate dispositif** : --quick choisit -u sur une base existante sans vérifier que le module est installé ; un résumé vert avec 0 test doit être refusé. Installation explicite nécessaire ici.
**Preuves** : changelog/2026-09-09_01_frais-de-preparation-des-locations/qa.md et preuves/.
**Reste ouvert** : release (1/1 point réalisé), incrément du manifest et déclenchement automatique de migration à vérifier à /odoo-close ; auteur absent du manifest, dette préexistante.


## Leçons du dispositif applicables en 19.0 (LESSONS.md)

- **L1 — La série d'un module n'est jamais supposée, elle est lue** [universelle] — avant de lire ou d'écrire une ligne, établir la série cible du module et n'appliquer que les règles de cette série.
- **L2 — « Odoo 19 » ne désigne pas une seule version** [hébergement Odoo Online / SaaS — voir `PLATEFORMES.md`] — pour un projet Odoo Online / SaaS, viser la dernière `saas~19.x`, pas la 19.0 ; vérifier la forme de la sécurité dans les sources de **la** série visée.
- **L3 — Un contrôle qui se trompe de série est pire que pas de contrôle** [universelle] — tout motif ajouté à `odoo_lint.py` porte sa portée (`since` / `before`) et est vérifié par comptage dans les sources des deux séries concernées avant d'être considéré comme vrai.
- **L4 — Une option qui n'existe pas est ignorée sans erreur** [universelle] — vérifier toute option Odoo dans les sources de la série avant de la lancer, et ne jamais détruire avant d'avoir prouvé que la réparation marche.
- **L5 — Reproduire dans l'outil du système cible, jamais dans le sien** [universelle] — reproduire avec l'outil du système cible ; quand un test contredit une preuve prise sur ce système, suspecter le test avant de se rétracter.
- **L6 — Un relevé qui avale les sources vendorisées fabrique de la dette imaginaire** [universelle] — un relevé ne recense que le code dont le projet est responsable ; toute copie de sources Odoo en est écartée, et le nombre d'écartés est annoncé pour que l'omission reste visible.
