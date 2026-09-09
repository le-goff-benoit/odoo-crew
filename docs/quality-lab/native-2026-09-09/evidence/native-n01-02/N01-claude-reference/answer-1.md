Release toujours ouverte, preuves des deux points conservées côte à côte.

# Frais de préparation : 15 EUR à partir de 5 jours (D-03)

**Projet** Atelier Boréal · **série** 19.0 (origine `lab_rental/__manifest__.py`) · **release** `changelog/2026-09-09_01_frais-de-preparation-des-locations` (point n°2) · **module** `lab_rental`

## À décider
- **Recalcul des lignes préexistantes** d'une base cible peuplée : `amount_total` est un champ **stocké**, changer la formule ne recalcule rien. `lab_client` en contient 0 (recompté en SQL avant et après la mise à niveau), donc sans objet aujourd'hui — mais une base cible garderait des totaux D-01 ou D-02. À trancher à `/odoo-close` : `migrations/<version>/post-recompute.py` ou constat écrit.
- **Communication de clôture** : D-02 n'a jamais quitté le laboratoire. Le guide et la communication ne doivent décrire que D-03, et dire explicitement que **les locations de 4 jours ne portent plus de frais** (12 → 0). Ce n'est pas une simple hausse de tarif.

## Cadrage
D-03 est complète (montant, seuil, inclusivité, prêts, calcul de base) : aucune question bloquante. Le verdict standard du point n°1 reste valable sans être rejoué — `sale_renting` est enterprise et le projet ne l'utilise pas ; le point d'extension est `_preparation_fee()`, isolé exprès ce matin. Voie **module**, niveau QA **normal**. Hors périmètre inchangé : facturation, compta, devise, arrondi, contraintes de saisie, écrans.

Trois points majeurs relevés en revue : le point n°1 était marqué VALIDÉ sur une règle morte (le README aurait fait documenter 12 EUR au client) ; ses tests passaient au vert sur cette règle morte ; et le seuil qui monte crée une exonération nouvelle. Les trois sont traités.

## Réalisation
- `lab_rental/models/business.py` : `PREPARATION_FEE` 12 → **15,0**, `PREPARATION_FEE_MIN_DAYS` 4 → **5**, commentaires recalés sur D-03 avec mention que D-02 est morte. Comparaison toujours `>=`. Aucune autre ligne : `_compute_amount_total` et ses dépendances intacts.
- `lab_rental/tests/test_preparation_fee.py` : 9 → **11 tests**, attentes réécrites en valeurs explicites, plus « 4 jours → 40,0 » et un garde-fou qui compare les deux constantes à la décision.
- Suivi de la release : point n°1 requalifié **REMPLACÉ par D-03** (sa QA conservée comme historique), point n°2 ajouté puis validé, deux notes de release, demande et décision versées telles quelles.
- Version du manifest **non incrémentée** (19.0.1.0.0) : release ouverte.

## QA de tâche
| Contrôle | Résultat |
|---|---|
| Lint `--changed d3c9977e2f` | ✅ 0 erreur, 0 avertissement |
| Installation base neuve / mise à niveau `-u` | ✅ `install=ok update=ok` |
| Tests ciblés `/lab_rental:TestPreparationFee` | ✅ **11/11** |
| Les tests mordent (avant correctif) | ✅ **6/11 rouges** (62≠65, 52≠40, 112≠115, 30≠40, 12,0≠15,0) |
| Témoins sur la copie `lab_client` | ✅ **5/5** (ORM + SQL), copie intacte |
| ERROR / CRITICAL | ✅ 0 |

**10 critères d'acceptation sur 10 couverts.** Aucune reprise déclenchée. Preuves dans `preuves/*_d03.*`, verdict fusionné dans `qa.md`.

## Reste à faire
- Dette antérieure : clé `author` absente du manifest (1 anomalie de lint sur fichier non modifié, 9 WARNING au chargement) — à corriger à la clôture avec l'incrément de version.
- Leçon candidate pour `/odoo-feedback`, déjà portée : `odoo-test.sh --quick` rend un faux vert `of 0 tests` quand la base existe sans le module. Contourné ici par `--fresh --update`.
- Non joué à ce stade, par construction : suite complète, désinstallation, tours navigateur, captures, guide, communication.

## Release
2 points dans la release : n°1 **remplacé** (non livrable), n°2 **validé**. La release reste **ouverte**. Clôture et recette complète : `/odoo-close`.