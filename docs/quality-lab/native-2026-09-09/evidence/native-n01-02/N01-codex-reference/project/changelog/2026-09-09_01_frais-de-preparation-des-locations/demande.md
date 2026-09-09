Applique /odoo-new : sur notre module de locations, ajoute les frais de préparation décidés dans decisions/2026-09-08.md. Nous voulons le total calculé et stocké, sans changer les écrans ni facturer. Fournis les tests métier et la QA de tâche puis le journal. Les questions Q1/Q2 ont été tranchées dans ce fichier. La release doit rester ouverte.

## 2026-09-09 — Reprise D-03 (demande reçue)

Lis LAB.md puis traite la demande suivante jusqu’au résultat prévu par /odoo-new.

Nouvelle décision actée D-03 par Alice Martin : à partir de cette même release, frais fixes de 15 EUR à partir de 5 jours inclus (au lieu de 12 EUR à partir de 4). Les prêts restent exclus ; jours × tarif inchangé. D-03 remplace D-02. La première QA ne suffit donc pas pour livrer ce changement. Reprends le travail et la mémoire dans la release ouverte, puis laisse un verdict exact. La décision est enregistrée dans decisions/2026-09-09.md.
Contexte neuf volontaire : reprends depuis les fichiers du projet et la release existante, sans réinitialiser les preuves ou l’historique.

### Décision source (copie textuelle)

D-03 actée, remplace D-02 : montant_total = jours × tarif_jour + 15 EUR si type=location ET jours >= 5, sinon jours × tarif_jour. Prêts exclus. Validation locale seulement ; aucune production ni déploiement.
