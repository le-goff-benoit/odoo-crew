# Demande

<!-- Copier chaque demande telle quelle, datée. Ne pas reformuler. -->

## 2026-09-09 — Demande de l'humain (conversation, telle quelle)

> Applique /odoo-new : sur notre module de locations, ajoute les frais de préparation décidés dans decisions/2026-09-08.md. Nous voulons le total calculé et stocké, sans changer les écrans ni facturer. Fournis les tests métier et la QA de tâche puis le journal. Les questions Q1/Q2 ont été tranchées dans ce fichier. La release doit rester ouverte.

### Décision de référence citée — `decisions/2026-09-08.md`, reprise telle quelle

> D-02, actée par Alice Martin (responsable fictive), le 08/09 : montant_total = jours × tarif_jour + 12 EUR si type=location ET jours >= 4, sinon jours × tarif_jour. Les prêts restent sans frais, y compris à 4 jours. Montants hors taxes, une seule monnaie EUR, aucun arrondi supplémentaire. Les valeurs jours et tarif restent positives ou nulles. Q1 borne inclusive : oui, 4 inclus. Q2 prêts : exclus. D-02 remplace D-01 (7 % de frais). Pas de modification de droits, ni comptabilité, ni documents historiques. Tous les enregistrements du bac sont des essais modifiables.

## 2026-09-09 — Demande de l'humain (conversation, telle quelle)

> Nouvelle décision actée D-03 par Alice Martin : à partir de cette même release, frais fixes de 15 EUR à partir de 5 jours inclus (au lieu de 12 EUR à partir de 4). Les prêts restent exclus ; jours × tarif inchangé. D-03 remplace D-02. La première QA ne suffit donc pas pour livrer ce changement. Reprends le travail et la mémoire dans la release ouverte, puis laisse un verdict exact. La décision est enregistrée dans decisions/2026-09-09.md.

### Décision de référence citée — `decisions/2026-09-09.md`, reprise telle quelle

> D-03 actée, remplace D-02 : montant_total = jours × tarif_jour + 15 EUR si type=location ET jours >= 5, sinon jours × tarif_jour. Prêts exclus. Validation locale seulement ; aucune production ni déploiement.
