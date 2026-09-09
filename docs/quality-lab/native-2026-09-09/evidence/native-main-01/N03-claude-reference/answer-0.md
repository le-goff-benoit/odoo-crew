La chaîne est terminée. Voici le compte-rendu.

---

# Indicateur de revue sur les demandes Aster (D-22)

**Projet** work · **série** 19.0 (origine : défaut) · **release** `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast` (point n°1) · **modules** aucun — configuration en base (`studio_customization`)

## À décider

**`x_lab_request` ne porte aucun droit d'accès.** Ni `ir.model.access`, ni `ir.rule`. Ce n'est pas une déduction : un `search_read` en `admin` renvoie *« You are not allowed to access 'Demande Aster' — No group currently allows this operation »*. Autrement dit, l'indicateur est calculé correctement côté serveur, mais **personne, administrateur compris, ne peut aujourd'hui consulter une demande**.

D-22 exclut explicitement tout changement de droits, et la demande dit « ajoute seulement l'indicateur ». Je m'y suis tenu : le pack livré ne crée aucun droit. La conséquence vous revient — soit ces droits sont posés dans une tâche dédiée, soit l'indicateur reste un calcul serveur sans usage.

## Cadrage

Verdict standard : **à développer, mais en configuration** — aucun standard 19.0 ne porte de notion de revue sur ce modèle manuel, en revanche un champ manuel calculé stocké couvre le besoin sans une ligne de Python (`ir_model.py:566-574`, `make_compute` ligne 46). Voie Studio retenue : c'est le profil du projet et votre demande explicite. Aucune question bloquante — D-22 tranche le seuil (7 inclus) et les prêts (exclus). Hors périmètre : droits, écrans, module, déploiement.

## Réalisation

Dans `changelog/2026-09-09_01_…/studio/` :

| Fichier | Rôle |
|---|---|
| `build_needs_review.py` | construction idempotente, contexte `studio=True`, relève l'identifiant externe créé par Odoo |
| `test_needs_review.py` | scénario XML-RPC rejouable, 17 contrôles, crée et nettoie ses données |
| `pack.json` | le livrable versionné — 1 enregistrement, références résolues |
| `created.txt`, `lab_rpc.py`, `controle_d21.py`, `etat_copie.py`, `journal_execution.md` | liste livrée, raccordement, outils de contrôle, journal d'exécution |

Le champ : `x_studio_needs_review`, booléen manuel stocké, `depends = x_studio_days,x_studio_kind`, vrai si `x_studio_days >= 7` **et** `x_studio_kind == 'rental'`. `x_name`, `x_studio_days`, `x_studio_kind` sont utilisés tels quels, XML-ID `lab_seed_*` intacts. Aucune vue, aucune automatisation, aucun droit.

Deux choix techniques méritent d'être signalés :

- Odoo ne marque `noupdate` sur un identifiant externe Studio qu'au **premier write**, pas à la création (`web_studio/models/ir_model_data.py:19-25`) — contrairement à ce qu'affirme notre rôle `studio.md`. Le script rejoue le chemin de Studio pour que le pack ne soit pas exposé à une mise à niveau.
- Le scénario doit vider explicitement les caches de droits, sans quoi le droit temporaire qu'il pose reste invisible.

## QA de tâche

| Contrôle | Résultat |
|---|---|
| Pack ↔ copie, avant écriture | 0 à créer / 0 à modifier / 1 inchangé |
| Deux applications sur base configurée | 0 créé / 0 modifié, deux fois |
| Deux applications **depuis l'absence du champ** | 1 créé, puis 0 créé / 1 inchangé |
| Doublon après double application | 1 champ, 1 identifiant externe, 1 modèle |
| Scénario RPC | **VERT** — 17/17, code retour 0 |
| Contre-épreuve règle D-21 | **ROUGE** — 6 contrôles basculent, le scénario sait échouer |
| Copie rendue propre | 0 donnée de recette, 0 droit, 0 règle |

**Critères d'acceptation : 10/10.** Détail et preuves dans `qa.md`.

Ni `odoo-test.sh` ni `odoo-shot.sh` : un point Studio se prouve par scénario RPC, et aucune vue n'a changé — pas de capture à prendre.

## Reste à faire

- **Les droits d'accès du modèle** (ci-dessus) — le seul vrai point ouvert.
- Aucun écran n'affiche l'indicateur ; c'est voulu, mais il n'est donc visible de personne.
- **Deux leçons candidates** pour `/odoo-feedback` : (1) `studio.md` affirme à tort qu'Odoo marque `noupdate` dès la création d'un enregistrement Studio ; (2) un droit d'accès fraîchement créé reste invisible du processus qui sert les appels tant que `ir.model.access.call_cache_clearing_methods` n'a pas été appelé — constaté sur `create` pendant 8 requêtes consécutives alors que `read` passait.
- Aucun déploiement effectué, conformément à la demande.

## Release

1 point, 1 réalisé. La release reste **ouverte**. Clôture et recette complète : `/odoo-close`.