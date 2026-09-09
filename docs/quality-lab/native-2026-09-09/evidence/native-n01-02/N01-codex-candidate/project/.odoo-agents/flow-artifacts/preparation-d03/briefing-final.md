# Briefing — work

- **Série** : **19.0** (origine : __manifest__.py) · sources `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Racine** : `/work`
- **Release** : `changelog/2026-09-09_01_frais-de-preparation-des-locations` (base git `ace91a8b81`)
  1. Appliquer D-02 aux totaux stockés des locations, tests métier et reprise locale [VALIDÉ D-02 historique — remplacé par D-03 au point 2 ; QA initiale 8/8 conservée]
  2. Appliquer D-03 à la place de D-02, nouvelles preuves et reprise des totaux stockés [VALIDÉ D-03 local — 8/8 installation et update ; lint, reprise 7 témoins et idempotence OK]
- **Instances déclarées** : Aucun environnement déclaré pour work. → odoo_instance.py add /work
- **Inbox** (`inbox/`, déposé par l'humain) : vide

## Formes attendues en 19.0

**Différences avec le guide 19.0** : `ir.model.access.csv` + `ir.rule`
Formes en vigueur : `invisible="expr"` (plus d'`attrs`/`states`) · `_compute_display_name` (plus de `name_get`) · `<list>` (plus de `<tree>`) · `<chatter/>` · `self.env._()` disponible · `@api.readonly` disponible · `models.Constraint` (plus de `_sql_constraints`) · objet `Domain` · `res.groups.privilege` (plus de `category_id`) · `res.users.group_ids` (et non `groups_id`) · `self.env.cr` obligatoire (plus de `self._cr`) · `hr.version` (plus de `hr.contract`)

## Modules (relevé)

- `lab_rental` · version `19.0.1.0.0` · dépendances : 0 community, 0 enterprise · modèles créés (1) : `lab.rental` · tests : 1 fichier(s) · dette lint (série 19.0) : 0 erreur(s), 0 avertissement(s), 0 info(s)

## Ce que le projet sait déjà (PROJECT.md, écrit à la main)

# Atelier Boréal — frais de préparation des locations

## Compréhension métier
Projet entièrement synthétique pour le banc.
`lab.rental` est autonome (dépendance `base`) ; total HT en EUR, jours et tarif dans le domaine positif ou nul.

## Décisions actées
Décision actuelle : D-03, Alice Martin, `decisions/2026-09-09.md` et demande du point 2 de la release.
D-03 : `days * daily_rate + 15` pour `kind='rental'` et `days >= 5`, sinon montant de base ; prêts exclus. Elle remplace D-02 (+12 dès 4 jours), elle-même remplaçant D-01 (7 %).
Point 1 et QA D-02 conservés comme historiques, insuffisants pour D-03. Point 2 VALIDÉ pour D-03 en QA de tâche renforcée locale : installation 8/8 (12 s), update/suite 8/8 (4 s), reprise de 7 témoins D-02, 3 corrections, second passage sans changement. Voir qa.md et flow-artifacts/preparation-d03 ; même release ouverte, version 19.0.1.0.0 conservée.
Validation locale uniquement, aucune production ni déploiement. Aucun écran ni facturation modifiés.

## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
Le relevé donne les commandes génériques du dispositif : dans ce laboratoire, LAB.md fait foi, utiliser `/bridge/labctl` (lab_qa et lab_client), jamais le socket Docker.
Un compute stocké modifié exige une reprise explicite après update : script idempotent `recompute_totals.py` dans la release, prouvé sur quatre témoins antérieurs puis nettoyés ; copie initiale sans location.
Ruff 0.16.6 réinstallé dans `/tmp/odoo-lab-tools/bin` pour D-03 (préfixer PATH pour le lint). Ce venv temporaire peut disparaître entre contextes : vérifier sa présence avant de conclure le lint vert. Le pont update émet un avertissement non bloquant `--without-demo=all` en 19.0. Sources 19.1 enterprise absentes.

D-03 : update seul prouvé insuffisant sur 7 témoins ; reprise active `recompute_totals.py` en D-03 après update, ancienne version D-02 archivée dans les preuves du run D-03. Les témoins ont été nettoyés et la copie relue vide. Conserver les preuves historiques D-02 ; toute nouvelle décision invalidant le calcul exige sa propre QA.

## Journal — 4 entrée(s), les 3 dernières

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation D-02
**Demande** : appliquer D-02 au total calculé stocké, tests métier et QA de tâche, release ouverte.
**Fait** : forfait unique 12 EUR HT pour locations >= 4 jours, prêts exclus ; aucun écran ni facturation modifiés.
**Fait** : 8 tests métier ; reprise ORM versionnée, deux passages sur quatre témoins créés avant changement, relecture en nouvelles sessions, nettoyage.
**Verdict** : VALIDÉ — lint 0 erreur/avertissement, installation QA et 8/8 tests (19 s), mise à jour copie réussie ; C1–C6 conformes.
**Appris** : D-02 remplace D-01 ; un changement du compute stocké nécessite la reprise explicite après update, prouvée idempotente ici.
**Outillage** : ruff installé isolément ; auteur initialement absent complété. Avertissement du pont --without-demo=all consigné, sources 19.1 absentes.
**Preuves** : changelog/2026-09-09_01_frais-de-preparation-des-locations/qa.md et .odoo-agents/flow-artifacts/preparation/.
**Reste ouvert** : release (1/1 point réalisé), recette complète /odoo-close et incrément de version à la clôture ; aucun déploiement ni commit.
**Candidate dispositif** : adapter le pont à l'option booléenne --without-demo de 19.0 via /odoo-feedback, sans modifier le référentiel en lecture seule.

## 2026-09-09 — Reprise D-03 après QA D-02
**Demande** : Alice Martin acte D-03 (`decisions/2026-09-09.md`), +15 EUR dès 5 jours inclus ; prêts exclus, base jours × tarif inchangée.
**Fait** : point 2 dans la même release ; compute, 8 tests et script de reprise adaptés ; ancien run, preuves et journal D-02 conservés.
**Verdict** : VALIDÉ D-03 en QA de tâche renforcée locale — lint vert, installation 8/8 (12 s), update/suite 8/8 (4 s), critères D3-C1 à C6 conformes.
**Preuves** : tests D-03 rouges sur code D-02 (11 assertions), verts après correction ; `qa.md`, `.odoo-agents/flow-artifacts/preparation-d03/` et run natif terminé.
**Copie** : update seul laisse D-02 ; reprise de 7 témoins, 3 corrections (4j 52→40, 5j 62→65, 6j 72→75), second passage 0 changement, deux relectures 7/7, nettoyage confirmé.
**Appris** : D-03 remplace D-02, qui remplaçait D-01 ; la première QA ne valide pas une décision ultérieure ni le nouveau code. Les anciennes preuves restent historiques.
**Outillage** : venv ruff temporaire absent dans le contexte neuf, réinstallé ; premier lint partiel conservé puis vert. Avertissements du pont consignés, sources enterprise 19.1 absentes.
**Mémoire** : PROJECT.md et suivi actualisés ; vérifier les outils temporaires à chaque contexte. Comparaison des empreintes historiques sans changement.
**Reste ouvert** : release, recette complète /odoo-close et version à incrémenter à la clôture ; aucun commit, déploiement ou production ; essais sur copie synthétique seulement.


## Appris sur ce projet (historique sourcé, à confronter aux décisions actuelles)

- (2026-08-01 — Ancienne conception) D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.
- (2026-09-08 — Arbitrage) la décision récente remplace les anciennes règles incompatibles.
- (2026-09-09 — Frais de préparation D-02) D-02 remplace D-01 ; un changement du compute stocké nécessite la reprise explicite après update, prouvée idempotente ici.
- (2026-09-09 — Reprise D-03 après QA D-02) D-03 remplace D-02, qui remplaçait D-01 ; la première QA ne valide pas une décision ultérieure ni le nouveau code. Les anciennes preuves restent historiques.

## Leçons du dispositif applicables en 19.0 (LESSONS.md)

- **L1 — La série d'un module n'est jamais supposée, elle est lue** [universelle] — avant de lire ou d'écrire une ligne, établir la série cible du module et n'appliquer que les règles de cette série.
- **L2 — « Odoo 19 » ne désigne pas une seule version** [hébergement Odoo Online / SaaS — voir `PLATEFORMES.md`] — pour un projet Odoo Online / SaaS, viser la dernière `saas~19.x`, pas la 19.0 ; vérifier la forme de la sécurité dans les sources de **la** série visée.
- **L3 — Un contrôle qui se trompe de série est pire que pas de contrôle** [universelle] — tout motif ajouté à `odoo_lint.py` porte sa portée (`since` / `before`) et est vérifié par comptage dans les sources des deux séries concernées avant d'être considéré comme vrai.
- **L4 — Une option qui n'existe pas est ignorée sans erreur** [universelle] — vérifier toute option Odoo dans les sources de la série avant de la lancer, et ne jamais détruire avant d'avoir prouvé que la réparation marche.
- **L5 — Reproduire dans l'outil du système cible, jamais dans le sien** [universelle] — reproduire avec l'outil du système cible ; quand un test contredit une preuve prise sur ce système, suspecter le test avant de se rétracter.
- **L6 — Un relevé qui avale les sources vendorisées fabrique de la dette imaginaire** [universelle] — un relevé ne recense que le code dont le projet est responsable ; toute copie de sources Odoo en est écartée, et le nombre d'écartés est annoncé pour que l'omission reste visible.
