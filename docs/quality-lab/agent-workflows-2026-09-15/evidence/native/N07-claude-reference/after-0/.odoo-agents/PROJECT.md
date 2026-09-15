# Atelier Nacre — préparation périodique et saisies explicites
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Décisions actées
- **N-17** (`decisions/current.md`) : `lab.preparation` n'est pas `stock.picking`. Le cron ne
  touche que les drafts automatiques ; toute saisie manuelle, zéro compris, est intangible ;
  une duplication est une demande neuve ; le reliquat ne naît que d'un reste positif.
- **H1, hypothèse non confirmée** (2026-09-16) : `action_remainder()` clôt la source même sans
  reste positif. Seule lecture ambiguë de N-17 ; tranchée ainsi dans le code et les tests.

## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.
- `manual` est un drapeau de **saisie**, pas un « prepared_qty non nul » : confondre les deux
  écrase les zéros volontaires (défaut corrigé le 2026-09-16).
- Corriger le calcul ne corrige pas la base : toute correction de `prepared_qty` doit être suivie
  d'une reprise `migrations/<version>/post-migrate.py`, donc d'un incrément de version du manifest.
- Dette antérieure : `__manifest__.py` n'a pas de clé `author`, ce qui maintient le lint du module
  en rouge indépendamment du diff en cours.
- Le module ne livre aucun `ir.cron` : `_cron_prepare` n'a pas de déclencheur en base.
