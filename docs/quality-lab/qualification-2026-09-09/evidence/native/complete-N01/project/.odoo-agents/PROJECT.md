# Atelier Boréal — frais de préparation des locations
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
Le métier distingue deux natures d'engagement sur `lab.rental` : la **location** (`rental`), qui
supporte les frais, et le **prêt** (`loan`), toujours gratuit quelle que soit sa durée. Le forfait de
préparation couvre un coût fixe de remise en état, indépendant du tarif et de la durée : il ne se
proratise pas et ne se cumule pas. Montants hors taxes, monnaie unique EUR.
## Décisions actées
Lire **`decisions/2026-09-09.md`** : c'est la seule qui fasse foi. Les fichiers plus anciens et le
journal décrivent des règles mortes.
- **D-03** (Alice Martin, 09/09/2026, `decisions/2026-09-09.md`) — **en vigueur** :
  `amount_total = days × daily_rate + 15 EUR` si `kind = rental` **et** `days >= 5` (borne
  **inclusive**) ; prêts **exclus** quelle que soit la durée. Forfait **fixe**, jamais proportionnel.
- **Règles mortes, à ne jamais réimplémenter** — toutes trois laissent des traces dans le dépôt :
  - **D-02** (08/09/2026, 12 EUR à partir de 4 jours) : remplacée par D-03 le lendemain, mais elle a
    été **réellement codée, validée et appliquée à `lab_client`**. On la retrouve dans l'historique
    git, le journal du 09/09, le point 1 de la release `2026-09-09_01` et ses preuves.
  - **D-01** (7 % du prix, journal du 2026-08-01) : jamais livrée.
  - Un test de non-régression interdit désormais l'une comme l'autre : forfait ni proportionnel,
    ni de 12 EUR, et aucune location de 4 jours facturée.
- Écartés du périmètre le 09/09/2026, à rouvrir seulement sur demande du client : `Monetary` +
  `currency_id` sur `amount_total` (monnaie unique actée), contrainte de positivité sur
  `days` / `daily_rate` (changerait l'écran de saisie), **paramétrage du seuil et du montant** — ce
  dernier point est à **reproposer** au client : la règle a été réécrite trois fois en deux jours.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- **`amount_total` est stocké** : changer le corps de `_compute_amount_total` ne réécrit rien en
  base. Vérifié le 09/09/2026 sur `lab_client` — après `-u`, une location de 4 jours restait à 40.0.
  Toute évolution de la règle s'accompagne d'un `migrations/<version>/post-migrate.py` qui rappelle
  le compute, et la version du manifest monte **avec** la tâche, pas à la clôture.
- La mémoire du projet contient plusieurs décisions périmées (D-01 à 7 %, D-02 à 12 EUR / 4 jours).
  Toujours confronter le journal aux fichiers de `decisions/` avant de coder, et prendre **le plus
  récent**.
- **Une décision peut être remplacée pendant la release, après réalisation et QA.** Arrivé le
  09/09/2026 avec D-03. Dans ce cas la QA précédente n'est pas « à rejouer » : ses oracles sont
  **faux** (elle attestait 52.0 pour une location de 4 jours, que D-03 fixe à 40.0). Marquer le point
  et ses preuves **PÉRIMÉS** là où on les lit — README de la release et `qa.md` — sans les effacer, et
  interdire à la communication de clôture de mentionner l'étape intermédiaire.
- **La reprise part de l'état déjà migré, pas de l'état d'origine.** `lab_client` portait déjà les
  montants D-02 quand D-03 est arrivée : certains montants devaient **baisser** (52.0 → 40.0). Un
  `add_to_compute` le fait par construction ; un script écrit comme « ajouter le forfait » n'aurait
  pas su retirer.
- **Un post-migrate n'est pas rejoué à version inchangée.** Un second `-u` prouve donc l'absence de
  dérive, **pas** l'idempotence de la reprise : celle-ci se mesure en rappelant le corps du script.
  Corollaire déjà connu : la version du manifest monte **avec** la tâche, jamais à la clôture.
