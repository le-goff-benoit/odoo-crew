# Atelier Nacre — préparation périodique et saisies explicites
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique. Lire decisions/current.md.
## Décisions actées
- **N-17** (`decisions/current.md`) fait foi sur `lab.preparation` : cron sur les seuls `draft` non manuels, saisie manuelle conservée y compris zéro, `done` figés, duplication = nouvelle demande, reliquat rattaché à sa source. Ce modèle **n'est pas** `stock.picking` : ne pas raisonner par analogie avec `stock` (backorder, `quantity` calculée).
- **H1** (revue 2026-09-16, release `2026-09-15_01_repair`) : `action_remainder()` ne passe la source en `done` que si un reliquat est créé ; sans reste positif, aucune écriture. Lecture retenue faute de précision de N-17 sur ce cas ; à contredire par l'humain si besoin.
- **H2** : `copy()` ne réinitialise que les quatre champs cités par N-17 ; `name` et `parent_id` suivent l'ORM par défaut.
- **H3** : une action planifiée quotidienne porte `_cron_prepare`, pour que « périodique » soit vrai. Wiring, pas comportement.
- La reprise des données existantes passe par un script de migration versionné qui appelle la méthode du cron : rejouable et idempotent, jamais un script joué à la main.

## Pièges connus
Une ancienne QA ne couvre pas automatiquement ce contrat. La copie est locale, isolée, sans données client.
Un champ `copy=True` par défaut : oublier `copy=False` sur un champ d'exécution fait voyager l'historique dans la duplication (`odoo/orm/models.py:5404`, 19.0).
Le lint du module partait avec une dette : `author` absent du manifest, pas de répertoire `tests/`.
