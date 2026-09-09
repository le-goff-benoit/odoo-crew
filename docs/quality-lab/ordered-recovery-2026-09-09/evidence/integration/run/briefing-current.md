# Briefing — project

- **Série** : **19.0** (origine : __manifest__.py) · sources `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Racine** : `/tmp/odoo-ordered-recovery-20260909/integration/run/project`
- **Release** : `changelog/2026-09-09_01_quantite-positive-a-la-confirmation` (base git `sans-git`)
- **Instances déclarées** : Aucun environnement déclaré pour project. → odoo_instance.py add /tmp/odoo-ordered-recovery-20260909/integration/run/project
- **Inbox** (`inbox/`, déposé par l'humain) : vide
- **Hors ligne** : bases locales et versions déployées non interrogées.

## Formes attendues en 19.0

**Différences avec le guide 19.0** : `ir.model.access.csv` + `ir.rule`
Formes en vigueur : `invisible="expr"` (plus d'`attrs`/`states`) · `_compute_display_name` (plus de `name_get`) · `<list>` (plus de `<tree>`) · `<chatter/>` · `self.env._()` disponible · `@api.readonly` disponible · `models.Constraint` (plus de `_sql_constraints`) · objet `Domain` · `res.groups.privilege` (plus de `category_id`) · `res.users.group_ids` (et non `groups_id`) · `self.env.cr` obligatoire (plus de `self._cr`) · `hr.version` (plus de `hr.contract`)

## Modules (relevé)

*(relevé vide — relancer le scan)*

## Ce que le projet sait déjà (PROJECT.md, écrit à la main)

# Projet synthétique de qualification 19.0

## Compréhension métier
La quantité peut être nulle pendant la préparation ; une confirmation doit garantir une quantité positive par tous les canaux. Le montant est quantity × unit_price.

## Décisions actées
Module existant lab_qualification, voie module, aucune interface ou permission nouvelle. Jeu initial valide de trois lignes, copie locale restaurée depuis ordered_seed. Écritures et tests uniquement sur ordered_copy ; référence conservée. Aucun redressement automatique.

## Pièges connus
Une garde dans le seul bouton ne couvre pas les imports ni les écritures directes. Les preuves backend ne valent pas recette complète de release.

## Journal — 1 entrée(s), les 1 dernières

## 2026-09-09 — Préparation
Demande : qualifier un invariant à la confirmation sur Odoo 19.0.
Fait : copie synthétique effectivement restaurée, trois identités et valeurs conservées ; analyse indépendante terminée.
Verdict : module requis, QA renforcée ; développement et réception encore à réaliser.
Appris : vérifier les canaux create/write/load et la contrainte effective.
Reste ouvert : tâche et release.


## Leçons du dispositif applicables en 19.0 (LESSONS.md)

- **L1 — La série d'un module n'est jamais supposée, elle est lue** [universelle] — avant de lire ou d'écrire une ligne, établir la série cible du module et n'appliquer que les règles de cette série.
- **L2 — « Odoo 19 » ne désigne pas une seule version** [hébergement Odoo Online / SaaS — voir `PLATEFORMES.md`] — pour un projet Odoo Online / SaaS, viser la dernière `saas~19.x`, pas la 19.0 ; vérifier la forme de la sécurité dans les sources de **la** série visée.
- **L3 — Un contrôle qui se trompe de série est pire que pas de contrôle** [universelle] — tout motif ajouté à `odoo_lint.py` porte sa portée (`since` / `before`) et est vérifié par comptage dans les sources des deux séries concernées avant d'être considéré comme vrai.
- **L4 — Une option qui n'existe pas est ignorée sans erreur** [universelle] — vérifier toute option Odoo dans les sources de la série avant de la lancer, et ne jamais détruire avant d'avoir prouvé que la réparation marche.
- **L5 — Reproduire dans l'outil du système cible, jamais dans le sien** [universelle] — reproduire avec l'outil du système cible ; quand un test contredit une preuve prise sur ce système, suspecter le test avant de se rétracter.
- **L6 — Un relevé qui avale les sources vendorisées fabrique de la dette imaginaire** [universelle] — un relevé ne recense que le code dont le projet est responsable ; toute copie de sources Odoo en est écartée, et le nombre d'écartés est annoncé pour que l'omission reste visible.
