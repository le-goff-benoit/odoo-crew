
— briefing : 6 Ko. Détail : `/work/.odoo-agents/`, `/home/blegoff/.odoo19-agents/LESSONS.md`, `/home/blegoff/.odoo19-agents/SERIES_MATRIX.md`.
# Briefing — work

- **Série** : **19.0** (origine : __manifest__.py) · sources `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Racine** : `/work`
- **Release** : `changelog/2026-09-09_01_frais-de-preparation-des-locations` (base git `93525dd7a9`)
  1. Frais de préparation D-02 : forfait 12 EUR sur les locations de 4 jours et plus (lab_rental) [VALIDÉ SOUS RÉSERVE — 9/9 tests ciblés, reprise prouvée sur lab_client (3/7 repris, +36 EUR), idempotente]
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

## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-02 (08/09/2026, Alice Martin) fait foi sur les frais de préparation** : forfait de
  12 EUR ajouté au total quand `kind = 'rental'` **et** `days >= 4` (borne inclusive, Q1).
  Les prêts en sont exclus sans exception, y compris à 4 jours et plus (Q2). Hors taxes,
  EUR unique, aucun arrondi supplémentaire. D-02 **annule D-01** (7 % proportionnel) : tout
  frais en pourcentage dans ce projet est une régression.
- Le total (`lab.rental.amount_total`) est un champ **calculé et stocké**, hors facturation
  et hors comptabilité : il ne déclenche aucune écriture comptable.

## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- `amount_total` étant **stocké**, tout changement de sa formule réécrit les
  enregistrements existants au `-u` du module. Ce n'est pas un changement de code
  inoffensif : il se valide sur la copie `lab_client` avec un comptage avant/après.
- Le module n'a **aucune vue**. « Ne pas changer les écrans » y est donc gratuit — mais la
  valeur affichée change pour l'utilisateur : c'est cela que la communication doit dire.

## Journal — 3 entrée(s), les 3 dernières

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation D-02 (release 2026-09-09_01, point n°1)
**Demande** : appliquer D-02 sur `lab_rental` — 12 EUR sur les locations de 4 jours et plus,
total calculé et stocké, sans toucher aux écrans ni à la facturation.
**Fait** : formule + `_preparation_fee()` dans `models/business.py`, 9 tests métier,
reprise `migrations/19.0.1.1.0/post-migrate.py`, manifest 19.0.1.0.0 → 19.0.1.1.0 (+ `author`,
dette antérieure qui bloquait le lint).
**Verdict** : VALIDÉ SOUS RÉSERVE (QA renforcée, 3 voies). Lint 0 erreur ; install ok,
update ok, 9/9 tests ciblés ; sur `lab_client`, 3 enregistrements repris sur 7 (+36,00 EUR),
prêts et locations courtes intacts, reprise idempotente. 12/12 critères couverts.
**Appris** : changer la formule d'un champ **stocké** ne réécrit aucune ligne déjà en base —
mesuré, pas supposé : après `-u` sans reprise, les sept totaux de `lab_client` étaient
inchangés. Il faut un `post-migrate` **et** l'incrément de version qui le déclenche, sans
quoi le script ne s'exécute jamais. Et une hypothèse technique posée en revue fonctionnelle
se vérifie sur la copie avant d'être écrite comme un fait : celle-ci était fausse.
**Reste ouvert** : valeur `author = Camptocamp` du manifest, supposée, à confirmer.
Release **volontairement laissée ouverte** : recette complète, désinstallation, guide et
communication client à la clôture (`/odoo-close`).


## Appris sur ce projet (historique sourcé, à confronter aux décisions actuelles)

- (2026-08-01 — Ancienne conception) D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.
- (2026-09-08 — Arbitrage) la décision récente remplace les anciennes règles incompatibles.
- (2026-09-09 — Frais de préparation D-02 (release 2026-09-09_01, point n°1)) changer la formule d'un champ **stocké** ne réécrit aucune ligne déjà en base — mesuré, pas supposé : après `-u` sans reprise, les sept totaux de `lab_client` étaient inchangés. Il faut un `post-migrate` **et** l'incrément de version qui le déclenche, sans quoi le script ne s'exécute jamais. Et une hypothèse technique posée en revue fonctionnelle se vérifie sur la copie avant d'être écrite comme un fait : celle-ci était fausse.

## Leçons du dispositif applicables en 19.0 (LESSONS.md)

- **L1 — La série d'un module n'est jamais supposée, elle est lue** [universelle] — avant de lire ou d'écrire une ligne, établir la série cible du module et n'appliquer que les règles de cette série.
- **L2 — « Odoo 19 » ne désigne pas une seule version** [hébergement Odoo Online / SaaS — voir `PLATEFORMES.md`] — pour un projet Odoo Online / SaaS, viser la dernière `saas~19.x`, pas la 19.0 ; vérifier la forme de la sécurité dans les sources de **la** série visée.
- **L3 — Un contrôle qui se trompe de série est pire que pas de contrôle** [universelle] — tout motif ajouté à `odoo_lint.py` porte sa portée (`since` / `before`) et est vérifié par comptage dans les sources des deux séries concernées avant d'être considéré comme vrai.
- **L4 — Une option qui n'existe pas est ignorée sans erreur** [universelle] — vérifier toute option Odoo dans les sources de la série avant de la lancer, et ne jamais détruire avant d'avoir prouvé que la réparation marche.
- **L5 — Reproduire dans l'outil du système cible, jamais dans le sien** [universelle] — reproduire avec l'outil du système cible ; quand un test contredit une preuve prise sur ce système, suspecter le test avant de se rétracter.
- **L6 — Un relevé qui avale les sources vendorisées fabrique de la dette imaginaire** [universelle] — un relevé ne recense que le code dont le projet est responsable ; toute copie de sources Odoo en est écartée, et le nombre d'écartés est annoncé pour que l'omission reste visible.

---
## Situation propre à ce run (D-03)

- Contexte neuf volontaire : reprise depuis les fichiers du projet, sans réinitialiser
  les preuves ni l'historique. Le run précédent (`frais-preparation.json`) est TERMINÉ
  et reste intact.
- Release **déjà ouverte** : `changelog/2026-09-09_01_frais-de-preparation-des-locations`
  (base git `93525dd7a9`), point n°1 = D-02, VALIDÉ SOUS RÉSERVE. D-03 sera le **point n°2**
  de cette même release, comme demandé (« à partir de cette même release »).
- Décision nouvelle : `decisions/2026-09-09.md` — D-03, Alice Martin, remplace D-02 :
  forfait **15 EUR** à partir de **5 jours inclus** (au lieu de 12 EUR à partir de 4).
  Prêts toujours exclus ; `jours × tarif_jour` inchangé.
- État du code lu : `PREPARATION_FEE = 12.0`, `PREPARATION_FEE_MIN_DAYS = 4` dans
  `lab_rental/models/business.py` ; reprise `migrations/19.0.1.1.0/post-migrate.py`
  déjà **exécutée** sur `lab_client` ; manifest en `19.0.1.1.0`.
- Point dur anticipé : la reprise de D-02 ne se rejouera pas (version installée =
  version du manifest). Une nouvelle reprise exige un **nouveau dossier de version**
  et un nouvel incrément du manifest.
- Données existantes touchées (champ stocké recalculé sur `lab_client`) → transition
  **`module_high_risk`** obligatoire, QA renforcée immédiate.
