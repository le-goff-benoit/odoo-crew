
— briefing : 7 Ko. Détail : `/work/.odoo-agents/`, `/home/blegoff/.odoo19-agents/LESSONS.md`, `/home/blegoff/.odoo19-agents/SERIES_MATRIX.md`.
# Briefing — work

- **Série** : **19.0** (origine : __manifest__.py) · sources `/home/blegoff/odoo-sources/19.0` + `19.0-enterprise`
- **Racine** : `/work`
- **Release** : `changelog/2026-09-09_01_frais-de-preparation-des-locations` (base git `a1476be7b1`)
  1. Frais de préparation 12 EUR sur les locations de 4 jours et plus (D-02) [VALIDÉ — lint 0, 10/10 tests ciblés, reprise de données prouvée sur lab_client, 12/12 critères]
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
Le métier distingue deux natures d'engagement sur `lab.rental` : la **location** (`rental`), qui
supporte les frais, et le **prêt** (`loan`), toujours gratuit quelle que soit sa durée. Le forfait de
préparation couvre un coût fixe de remise en état, indépendant du tarif et de la durée : il ne se
proratise pas et ne se cumule pas. Montants hors taxes, monnaie unique EUR.

## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-02** (Alice Martin, 08/09/2026) : `amount_total = days × daily_rate + 12 EUR` si
  `kind = rental` **et** `days >= 4` (borne **inclusive**, Q1) ; prêts **exclus** quelle que soit la
  durée (Q2). Forfait **fixe**, jamais proportionnel. Remplace **D-01** (7 %), encore visible au
  journal du 2026-08-01 — ne pas la réimplémenter.
- Écartés du périmètre le 09/09/2026, à rouvrir seulement sur demande du client : `Monetary` +
  `currency_id` sur `amount_total` (D-02 fixe une monnaie unique), contrainte de positivité sur
  `days` / `daily_rate` (changerait l'écran de saisie), paramétrage du seuil et du montant.

## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- **`amount_total` est stocké** : changer le corps de `_compute_amount_total` ne réécrit rien en
  base. Vérifié le 09/09/2026 sur `lab_client` — après `-u`, une location de 4 jours restait à 40.0.
  Toute évolution de la règle s'accompagne d'un `migrations/<version>/post-migrate.py` qui rappelle
  le compute, et la version du manifest monte **avec** la tâche, pas à la clôture.
- La mémoire du projet contient une décision périmée (D-01, 7 %). Toujours confronter le journal aux
  fichiers de `decisions/` avant de coder.

## Journal — 3 entrée(s), les 3 dernières

## 2026-08-01 — Ancienne conception
**Appris** : D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Frais de préparation des locations (D-02)
**Demande** : appliquer D-02 sur `lab_rental` — total calculé et stocké, sans écran ni facturation.
**Fait** : `_compute_amount_total` délègue à `_preparation_fee()` (12 EUR fixes si `kind = rental`
et `days >= 4`) ; 10 tests métier ; reprise `migrations/19.0.1.1.0/post-migrate.py` ; manifest en
19.0.1.1.0. Release `2026-09-09_01`, point 1, **restée ouverte**.
**Verdict** : VALIDÉ — lint 0 erreur, 10/10 tests ciblés (install et update), 12/12 critères reçus,
reprise prouvée sur `lab_client` (3 lignes sur 7, +12.0 exactement, idempotente).
**Appris** :
- Une mise à niveau ne recalcule **pas** un champ stocké dont seul le corps du compute a changé :
  constaté sur `lab_client` (une location de 4 jours restait à 40.0). Tout changement de règle sur
  `amount_total` exige un script de reprise, sinon c'est vert en test et faux chez le client.
- Le dossier de migration porte la version cible : la montée de version ne peut pas attendre la clôture.
- D-01 (7 %) est morte mais vit encore au journal du 2026-08-01 ; un test de non-régression interdit
  désormais tout forfait proportionnel.
**Reste ouvert** : confirmer `author` du manifest ; clôture et recette complète (`/odoo-close`) ;
hors périmètre assumé — `Monetary`, contrainte de positivité, paramétrage du seuil.


## Appris sur ce projet (historique sourcé, à confronter aux décisions actuelles)

- (2026-08-01 — Ancienne conception) D-01 : frais de préparation de 7 % pour toutes les locations. Cette décision est historique, remplacée par D-02.
- (2026-09-08 — Arbitrage) la décision récente remplace les anciennes règles incompatibles.
- (2026-09-09 — Frais de préparation des locations (D-02)) Une mise à niveau ne recalcule **pas** un champ stocké dont seul le corps du compute a changé : constaté sur `lab_client` (une location de 4 jours restait à 40.0). Tout changement de règle sur `amount_total` exige un script de reprise, sinon c'est vert en test et faux chez le client.
- (2026-09-09 — Frais de préparation des locations (D-02)) Le dossier de migration porte la version cible : la montée de version ne peut pas attendre la clôture.
- (2026-09-09 — Frais de préparation des locations (D-02)) D-01 (7 %) est morte mais vit encore au journal du 2026-08-01 ; un test de non-régression interdit désormais tout forfait proportionnel.

## Leçons du dispositif applicables en 19.0 (LESSONS.md)

- **L1 — La série d'un module n'est jamais supposée, elle est lue** [universelle] — avant de lire ou d'écrire une ligne, établir la série cible du module et n'appliquer que les règles de cette série.
- **L2 — « Odoo 19 » ne désigne pas une seule version** [hébergement Odoo Online / SaaS — voir `PLATEFORMES.md`] — pour un projet Odoo Online / SaaS, viser la dernière `saas~19.x`, pas la 19.0 ; vérifier la forme de la sécurité dans les sources de **la** série visée.
- **L3 — Un contrôle qui se trompe de série est pire que pas de contrôle** [universelle] — tout motif ajouté à `odoo_lint.py` porte sa portée (`since` / `before`) et est vérifié par comptage dans les sources des deux séries concernées avant d'être considéré comme vrai.
- **L4 — Une option qui n'existe pas est ignorée sans erreur** [universelle] — vérifier toute option Odoo dans les sources de la série avant de la lancer, et ne jamais détruire avant d'avoir prouvé que la réparation marche.
- **L5 — Reproduire dans l'outil du système cible, jamais dans le sien** [universelle] — reproduire avec l'outil du système cible ; quand un test contredit une preuve prise sur ce système, suspecter le test avant de se rétracter.
- **L6 — Un relevé qui avale les sources vendorisées fabrique de la dette imaginaire** [universelle] — un relevé ne recense que le code dont le projet est responsable ; toute copie de sources Odoo en est écartée, et le nombre d'écartés est annoncé pour que l'omission reste visible.
