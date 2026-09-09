
— briefing : 6 Ko. Détail : `/work/.odoo-agents/`, `/home/blegoff/.odoo19-agents/LESSONS.md`, `/home/blegoff/.odoo19-agents/SERIES_MATRIX.md`.
# Briefing — work

- **Série** : **19.0** (origine : __manifest__.py) · sources `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Racine** : `/work`
- **Release** : `changelog/2026-09-09_01_frais-de-preparation-des-locations` (base git `d3c9977e2f`)
  1. Frais de préparation : forfait 12 EUR sur les locations de 4 jours et plus (D-02) [VALIDÉ — 9/9 tests ciblés, lint vert, mise à niveau OK]
- **Instances déclarées** : Aucun environnement déclaré pour work. → odoo_instance.py add /work
- **Inbox** (`inbox/`, déposé par l'humain) : vide

## Formes attendues en 19.0

**Différences avec le guide 19.0** : `ir.model.access.csv` + `ir.rule`
Formes en vigueur : `invisible="expr"` (plus d'`attrs`/`states`) · `_compute_display_name` (plus de `name_get`) · `<list>` (plus de `<tree>`) · `<chatter/>` · `self.env._()` disponible · `@api.readonly` disponible · `models.Constraint` (plus de `_sql_constraints`) · objet `Domain` · `res.groups.privilege` (plus de `category_id`) · `res.users.group_ids` (et non `groups_id`) · `self.env.cr` obligatoire (plus de `self._cr`) · `hr.version` (plus de `hr.contract`)

## Modules (relevé)

*(relevé vide — relancer le scan)*

## Ce que le projet sait déjà (PROJECT.md, écrit à la main)

## Compréhension métier
Projet entièrement synthétique pour le banc.
Le module `lab_rental` porte un modèle propre au projet (`lab.rental`, dépend de `base`
seul) : ce n'est pas du `sale_renting` (standard enterprise). Deux natures d'engagement
cohabitent sur le même modèle, distinguées par `kind` : la **location** (facturée) et le
**prêt** (jamais de frais). Le total `amount_total` est un champ calculé **stocké**.

## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-02 (08/09/2026, Alice Martin) — en vigueur** : `amount_total = jours × tarif_jour`,
  plus un forfait de préparation de **12 EUR** si `kind = 'rental'` **et** `days >= 4`.
  Borne inclusive (Q1 : 4 compte). Prêts exclus quelle que soit la durée (Q2).
  Hors taxes, EUR unique, aucun arrondi supplémentaire.
- **D-01 (7 % de frais) est morte** : elle ne subsiste que dans l'entrée de journal du
  2026-08-01. Ne pas la réimplémenter en relisant le journal.
- Périmètre volontairement fermé : pas de facturation, pas de comptabilité, pas de devise,
  pas de contrainte de saisie, aucun écran modifié.

## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- **`amount_total` est stocké** : changer la *formule* ne recalcule pas les enregistrements
  existants. Odoo ne recalcule que sur variation des dépendances (`days`, `daily_rate`,
  `kind`). Toute évolution de la règle tarifaire doit se demander si une base cible contient
  des lignes, et prévoir un script de migration le cas échéant. (Copie `lab_client` au
  2026-09-09 : 0 enregistrement, donc sans objet ce jour-là.)
- Le seuil de 4 jours est **inclusif** ; le piège classique est d'écrire `> 4`.

## Journal — 3 entrée(s), les 3 dernières

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation des locations (D-02)
**Demande** : appliquer D-02 sur `lab_rental` — total calculé et stocké, sans toucher aux écrans ni facturer.
**Fait** : `_compute_amount_total` ajoute un forfait isolé dans `_preparation_fee()` (12 EUR si `kind='rental'` et `days >= 4`, borne incluse) ; 9 tests métier dans `tests/test_preparation_fee.py` sur un socle `LabRentalCommon`. Aucun champ, aucune vue, aucune ligne de sécurité.
**Verdict** : VALIDÉ — lint ciblé vert, `install=ok update=ok`, 9/9 tests, 8/8 critères, comportement confirmé sur la copie `lab_client` (ORM et SQL). Release `2026-09-09_01` **laissée ouverte**.
**Appris** :
- Les tests ont été prouvés rouges (4/9) sur l'ancienne formule avant d'être verts : un test qui n'a jamais échoué ne prouve rien.
- `odoo-test.sh --quick` rend `✅ tests OK` avec `of 0 tests` quand la base existe sans le module : il fait `-u`, et `--fresh` n'y change rien puisqu'il recrée la base. Chemin complet (`-i`) obligatoire dans ce cas. **Leçon candidate pour `/odoo-feedback`.**
- Un champ calculé **stocké** ne se recalcule pas quand la formule change : c'est la reprise de données à ne pas oublier (ici sans objet, 0 enregistrement).
**Reste ouvert** : recalcul des lignes préexistantes d'une base cible peuplée (script de migration à trancher à la clôture) ; clé `author` absente du manifest (dette antérieure) ; incrément de version, recette complète et livrables client à `/odoo-close`.


## Leçons du dispositif applicables en 19.0 (LESSONS.md)

- **L1 — La série d'un module n'est jamais supposée, elle est lue** [universelle] — avant de lire ou d'écrire une ligne, établir la série cible du module et n'appliquer que les règles de cette série.
- **L2 — « Odoo 19 » ne désigne pas une seule version** [hébergement Odoo Online / SaaS — voir `PLATEFORMES.md`] — pour un projet Odoo Online / SaaS, viser la dernière `saas~19.x`, pas la 19.0 ; vérifier la forme de la sécurité dans les sources de **la** série visée.
- **L3 — Un contrôle qui se trompe de série est pire que pas de contrôle** [universelle] — tout motif ajouté à `odoo_lint.py` porte sa portée (`since` / `before`) et est vérifié par comptage dans les sources des deux séries concernées avant d'être considéré comme vrai.
- **L4 — Une option qui n'existe pas est ignorée sans erreur** [universelle] — vérifier toute option Odoo dans les sources de la série avant de la lancer, et ne jamais détruire avant d'avoir prouvé que la réparation marche.
- **L5 — Reproduire dans l'outil du système cible, jamais dans le sien** [universelle] — reproduire avec l'outil du système cible ; quand un test contredit une preuve prise sur ce système, suspecter le test avant de se rétracter.
- **L6 — Un relevé qui avale les sources vendorisées fabrique de la dette imaginaire** [universelle] — un relevé ne recense que le code dont le projet est responsable ; toute copie de sources Odoo en est écartée, et le nombre d'écartés est annoncé pour que l'omission reste visible.
