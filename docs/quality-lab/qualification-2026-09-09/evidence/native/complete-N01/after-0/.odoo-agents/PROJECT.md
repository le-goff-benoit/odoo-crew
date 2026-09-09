# Atelier Boréal — frais de préparation des locations
<!-- odoo-agents:relevé fin -->
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
