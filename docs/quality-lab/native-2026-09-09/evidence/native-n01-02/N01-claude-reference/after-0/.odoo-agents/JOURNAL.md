# Journal

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
