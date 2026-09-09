# Briefing — work

- **Série** : **19.0** (origine : défaut) · sources `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Racine** : `/work`
- **Release** : aucune release ouverte — s'ouvre après le verdict de l'analyste ou du support (`odoo-release.sh open <projet> "<titre>"`)
- **Instances déclarées** : Aucun environnement déclaré pour work. → odoo_instance.py add /work

## Formes attendues en 19.0

**Différences avec le guide 19.0** : `ir.model.access.csv` + `ir.rule`
Formes en vigueur : `invisible="expr"` (plus d'`attrs`/`states`) · `_compute_display_name` (plus de `name_get`) · `<list>` (plus de `<tree>`) · `<chatter/>` · `self.env._()` disponible · `@api.readonly` disponible · `models.Constraint` (plus de `_sql_constraints`) · objet `Domain` · `res.groups.privilege` (plus de `category_id`) · `res.users.group_ids` (et non `groups_id`) · `self.env.cr` obligatoire (plus de `self._cr`) · `hr.version` (plus de `hr.contract`)

## Modules (relevé)

*(relevé vide — relancer le scan)*

## Ce que le projet sait déjà (PROJECT.md, écrit à la main)

## Compréhension métier
Projet entièrement synthétique pour le banc.

## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.

## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.

## Journal — 2 entrée(s), les 2 dernières

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.


## Leçons du dispositif applicables en 19.0 (LESSONS.md)

- **L1 — La série d'un module n'est jamais supposée, elle est lue** [universelle] — avant de lire ou d'écrire une ligne, établir la série cible du module et n'appliquer que les règles de cette série.
- **L2 — « Odoo 19 » ne désigne pas une seule version** [hébergement Odoo Online / SaaS — voir `PLATEFORMES.md`] — pour un projet Odoo Online / SaaS, viser la dernière `saas~19.x`, pas la 19.0 ; vérifier la forme de la sécurité dans les sources de **la** série visée.
- **L3 — Un contrôle qui se trompe de série est pire que pas de contrôle** [universelle] — tout motif ajouté à `odoo_lint.py` porte sa portée (`since` / `before`) et est vérifié par comptage dans les sources des deux séries concernées avant d'être considéré comme vrai.
- **L4 — Une option qui n'existe pas est ignorée sans erreur** [universelle] — vérifier toute option Odoo dans les sources de la série avant de la lancer, et ne jamais détruire avant d'avoir prouvé que la réparation marche.
- **L5 — Reproduire dans l'outil du système cible, jamais dans le sien** [universelle] — reproduire avec l'outil du système cible ; quand un test contredit une preuve prise sur ce système, suspecter le test avant de se rétracter.
- **L6 — Un relevé qui avale les sources vendorisées fabrique de la dette imaginaire** [universelle] — un relevé ne recense que le code dont le projet est responsable ; toute copie de sources Odoo en est écartée, et le nombre d'écartés est annoncé pour que l'omission reste visible.
