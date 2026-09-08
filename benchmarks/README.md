# Banc d’essai qualité Odoo

Ce laboratoire évalue des demandes synthétiques indépendantes des projets client.
Le pilote contient trois dossiers exécutables : B03 (qualification métier), B06
(verdict QA et droits), B10 (évolution des décisions et transmission du contexte).
Les sept autres cas sont un backlog explicite, pas des tests opérationnels.

## Exécuter

Python 3.10+, Linux avec bubblewrap, CLI Codex et Claude déjà authentifiées.
L’adaptateur Codex attend une installation npm avec Node dans le même préfixe.
L’adaptateur Claude attend le binaire installé localement. Le réseau fournisseur
est nécessaire ; les identifiants sont montés en lecture seule et jamais copiés
vers les résultats. Leur renouvellement éventuel se fait hors du laboratoire.

```bash
python3 scripts/odoo_bench.py validate
python3 scripts/odoo_bench.py plan --config benchmarks/configs/pilot-local.example.json --output /tmp/odoo-quality-runs
python3 scripts/odoo_bench.py run /tmp/odoo-quality-runs/IDENTIFIANT
python3 scripts/odoo_bench.py status /tmp/odoo-quality-runs/IDENTIFIANT
python3 scripts/odoo_bench.py stop /tmp/odoo-quality-runs/IDENTIFIANT
python3 scripts/odoo_bench.py resume /tmp/odoo-quality-runs/IDENTIFIANT
```

Copier la configuration et choisir explicitement modèle et effort. Les valeurs
fournies sont les réglages locaux du pilote, aucune recommandation universelle.
Un plan fige demandes, rôles, corrigés et leurs empreintes. L’exécution est
séquentielle, limitée à 600 secondes par réponse. Le terminal affiche un battement
toutes les cinq secondes ; `state.json` et `report.md` permettent de suivre la
campagne depuis un autre terminal. Un verrou empêche deux exécuteurs concurrents.
`resume` lance seulement les essais encore en attente : un essai interrompu,
échoué ou terminé n’est jamais rejoué automatiquement, car il peut avoir coûté.

Le processus ne voit que le dossier temporaire vide, les outils système et son
authentification ; le dossier est fourni par stdin. Le dépôt, les projets clients
et la grille de correction ne sont pas montés. Les outils de l’assistant sont
désactivés. Ce mode mesure une réponse sur dossier, pas le routage natif des skills,
la lecture effective d’un briefing, ni du code exécuté dans Odoo.

## Corriger une réponse

Un succès technique reste « non évaluée ». Après lecture de `answer.md`, produire
un JSON avec l’empreinte de la réponse, le nom de l’évaluateur et **tous** les
critères du `case.json` figé. Exemple de structure (à compléter intégralement) :

```json
{
  "reviewer": "nom et méthode de revue, limites ou conflit éventuel",
  "answer_sha256": "empreinte de state.json",
  "criteria": {
    "reject": {"grade": "pass", "evidence": "citation ou localisation précise"}
  }
}
```

```bash
python3 scripts/odoo_bench.py review /tmp/odoo-quality-runs/IDENTIFIANT B06-codex /tmp/review.json
```

Jugements autorisés : `pass`, `fail`, `uncertain`. Une erreur critique donne
`rejected`, tous les critères réussis donnent `accepted`, le reste demande une
revue. Une dimension absente vaut **non mesurée**, jamais 100 %. Le code exige
une preuve renseignée ; sa pertinence reste une responsabilité de l’évaluateur.
Conserver les désaccords et faire arbitrer les cas ambigus. Une correction par
l’assistant qui conçoit le banc reste exploratoire : ce n’est pas un juge aveugle.

## Adapter et apprendre

1. Relier une proposition du document d’analyse à un défaut observable et à une
   dimension : réponse, développement, QA, connaissance métier.
2. Écrire un dossier synthétique et sa rubrique **avant** les réponses. Prévoir
   ambiguïtés, contradictions, droits et décisions qui changent dans le temps.
3. Figer la référence, puis une seule variation des consignes. Garder identiques
   modèle, effort, dossier et environnement pour mesurer l’effet des instructions.
4. Comparer ensuite modèles et efforts à consignes constantes. Répéter les essais
   et alterner leur ordre ; le pilote à une répétition ne permet pas de classement.
5. Garder des cas réservés hors des itérations d’ajustement. Une amélioration qui
   récite le corrigé sans généraliser doit échouer à ces cas.
6. Promouvoir seulement après non-régression sur les critères critiques et gains
   documentés. La vitesse et les tokens sont secondaires à la qualité métier.

La suite ajoute B10 v2/B11, trois variantes avec ordre contrebalancé, B12
génération de code, un oracle Odoo et un correcteur masqué. Voir
[le mode opératoire](../docs/quality-lab/OPERATIONS.md). Les résultats bruts restent
locaux. Ne publier que des dossiers synthétiques et des rapports vérifiés sans
secrets ni informations client. Aucune modification automatique des rôles actifs.
