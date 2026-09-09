[4/4 journal] entrée écrite · `PROJECT.md` : 3 pièges ajoutés · release laissée ouverte

# Recalcul fiable des dossiers brouillons

**Projet** Entrepôt Silex · **série** 19.0 (manifest) · **release** `changelog/2026-09-09_01_recalcul-fiable-des-dossiers-brouillons` (point n°1, VALIDÉ, **release ouverte**) · **module** `lab_dispatch`

## À décider
1. **`author` manquant dans le manifest** — lint rouge, dette antérieure au commit de base (`git show 799eff1:lab_dispatch/__manifest__.py` le confirme). Je ne l'ai pas corrigée : la remplir demande d'inventer un éditeur. Un mot de votre part et je la ferme avant la clôture.
2. **Version incrémentée maintenant** (19.0.1.0.0 → 19.0.1.0.1) au lieu de la clôture : sans incrément, Odoo ne déclenche jamais la migration de reprise. À ne pas ré-incrémenter à la clôture.

## Cadrage
Aucune question bloquante : D-12 tranche Q1 (validés figés) et Q2 (lignes annulées exclues). Aucun équivalent standard (`grep` sur les 625 addons 19.0 : rien) → correctif de custom, voie module. J'ai lu « strictement inchangé » au sens fort : on **saute** le dossier validé, on ne le réécrit pas avec la même valeur. D-11 (journal du 2026-08-01) est actée obsolète. Hors périmètre : recalcul des validés, droits, toute base hors copie synthétique, déploiement.

## Réalisation
- `models/business.py` — `filtered(state == 'draft')` + exclusion des lignes `cancelled`.
- `migrations/19.0.1.0.1/post-migrate.py` (nouveau) — reprise idempotente des seuls brouillons.
- `tests/{__init__,common,test_recalculate}.py` (nouveaux) — 5 tests, un par critère.
- `__manifest__.py` — version 19.0.1.0.1.

## QA de tâche (niveau **renforcé** — données existantes)
| Contrôle | Résultat |
|---|---|
| Test rouge avant correction | **4 échecs / 5** — 110,00 au lieu de 20,00, validé écrasé |
| Base neuve `--fresh` | `install=ok`, 5/5 tests |
| Mise à jour `--quick` | `install=ok update=ok`, 5/5 tests |
| Reprise sur `lab_client` (migration rejouée 2×) | 999,00 → **20,00** ; validé **777,00 intact**, `write_date` jamais modifiée ; valeurs identiques aux deux passes |
| Contrôle sélection mixte sur la copie | `CONTROLE_COPIE=OK`, transaction annulée |
| Droits | `security/` inchangé |
| Lint `--changed` | 1 erreur — `author`, dette antérieure (voir « À décider ») |

Critères d'acceptation : **5/5 couverts** (détail dans `qa.md`).

## Reste à faire
- Les deux points « À décider » ci-dessus.
- **Contrôle incomplet, non masqué** : `ruff` est absent de l'environnement, l'étape 1/3 du lint a été *ignorée*, pas passée. Le statique repose sur les contrôles Odoo et la revue du diff.
- Idempotence prouvée **sur les valeurs** : rejouer la reprise rafraîchit la `write_date` des brouillons (valeur identique). D-12 n'exige l'immuabilité stricte que pour les validés — respectée.
- Leçon candidate pour `/odoo-feedback` : « corriger le calcul d'un champ stocké ne corrige pas les données ; la reprise impose un incrément de version » — déjà dans `PROJECT.md`, mérite peut-être `LESSONS.md`.

## Release
1 point, 1 réalisé. Rien n'a été commité, aucune capture ni guide produit. Clôture et recette complète : `/odoo-close`.