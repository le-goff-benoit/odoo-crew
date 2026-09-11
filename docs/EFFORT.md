# Minutes d'agent prévues et mesurées

`/odoo-estimate` chiffre le travail des agents par tâche, puis
`scripts/odoo_effort.py` rapproche la prévision de l'exécution. Un lot de travail
est une tâche identifiée ; une release regroupe plusieurs tâches. Il n'y a
ni charge humaine, ni barème commercial, ni conversion en heures de consultant.

`effort.json`, versionné dans la release, conserve tâches, révisions et mesures.
`estimation.md` présente la prévision ; `bilan-effort.md`, `bilan-effort.json`
et `bilan-effort.csv` sont les vues du réalisé. `report` régénère ces quatre fichiers.
Les traces de conversation restent à leur emplacement local : ne les copie
pas dans la release. Le registre en conserve la provenance utile à la mesure.

## Préparer la prévision

### Veille et reprise (outils du 11 septembre 2026)

Les nouveaux `start` enregistrent deux horloges Linux et l’identité du démarrage.
`stop` mesure le temps éveillé, avec `suspended_seconds` séparé ; fermer la fenêtre
ne remet pas les horloges à zéro. Les attentes pendant que le poste est éveillé
restent incluses. Après reboot, changement de namespace ou borne ancienne sans
horloge, l’arrêt devient `interrupted`, durée inconnue, sans compter la nuit.
Le cockpit peut demander `report_data(..., live=True)` : aperçu uniquement,
aucune modification du registre. Les exports `report` restent déterministes.

Les compteurs natifs sont indépendants : une valeur absente reste `null` mais
n’efface plus les autres. Les entrées normalisées incluent le cache, à ne pas
additionner une seconde fois. Le calcul tarifaire exige toujours tous les champs
nécessaires. Une dernière ligne JSONL en cours est ignorée avec avertissement ;
une corruption interne est refusée. Les anciennes durées natives ne permettent
pas de déduire une suspension et ne sont pas corrigées arbitrairement.

### Initialisation

Depuis le référentiel, pour une release avec `plan.json` :

```bash
python3 scripts/odoo_effort.py init /chemin/projet/changelog/RELEASE
python3 scripts/odoo_effort.py estimate /chemin/projet/changelog/RELEASE --file estimation.json
python3 scripts/odoo_effort.py report /chemin/projet/changelog/RELEASE
```

`init` reprend les tâches de `plan.json` s'il existe. Sans plan, il prépare le
registre ; `estimate --file` crée les tâches grâce aux champs `task` et `title`.
Garder des identifiants stables et un résultat compréhensible par tâche.
La tâche spéciale `RELEASE` porte recette et consolidation communes, comptées
une seule fois.

Exemple de fichier d'estimation, avec des nombres **illustratifs**, à remplacer
par une évaluation du périmètre réel :

```json
{
  "lines": [{
    "task": "T01",
    "title": "Corriger le calcul et son test de régression",
    "agent": "odoo-developer",
    "optimistic_minutes": 6,
    "likely_minutes": 10,
    "pessimistic_minutes": 20,
    "assumptions": ["Cause reproduite", "Base de QA disponible"],
    "basis": "Jugement initial ; aucun historique comparable mesuré",
    "confidence": "low"
  }]
}
```

Une ligne porte le temps d'un rôle sur une tâche, outils et tests compris.
Ajouter les autres rôles nécessaires et les reprises plausibles ; ne pas
confondre QA ciblée et recette complète. Le point central PERT vaut
`(optimistic_minutes + 4 × likely_minutes + pessimistic_minutes) / 6`.
La fourchette exprime l'incertitude du périmètre et de l'environnement ; elle
ne constitue pas un intervalle statistique garanti.

Pour changer une prévision, conserver la raison et la révision antérieure :

```bash
python3 scripts/odoo_effort.py estimate /chemin/projet/changelog/RELEASE \
  --file estimation-revisee.json --reason "Critère ajouté par la décision D-03"
```

Ne pas réécrire une prévision après exécution pour la rapprocher du réalisé.
Sans estimation antérieure, signaler l'absence et chiffrer séparément la suite.

## Mesurer chaque passage d'agent

L'orchestrateur est le seul écrivain. Avant le travail, ouvrir une mesure avec
la session réelle de l'exécutant, déjà identifiable ; le modèle peut être encore
inconnu. Conserver l'identifiant d'entrée retourné :

```bash
python3 scripts/odoo_effort.py start /chemin/projet/changelog/RELEASE \
  --task T01 --agent odoo-developer --provider codex --source /chemin/session.jsonl
python3 scripts/odoo_effort.py stop /chemin/projet/changelog/RELEASE \
  --entry IDENTIFIANT_RETOURNE --source /chemin/session.jsonl
```

`start` capture le départ, les compteurs disponibles et la prévision applicable ;
`stop` calcule la différence sur **la même session**. Employer `--provider claude`
pour une trace Claude. Changer de rôle ou de tâche ferme la mesure précédente
et en ouvre une autre. Une reprise garde son entrée propre. Fermer la mesure
avant une attente humaine identifiée, puis en ouvrir une nouvelle au retour au
travail. Le chronomètre n'exclut pas automatiquement les attentes à l'intérieur
d'un tour : leur absence de décompte doit rester une limite déclarée.
Une restauration ou un test pendant lequel l'agent reste mobilisé fait partie
du temps ; l'heure d'ouverture du premier message n'est pas à elle seule une
mesure du temps de travail.

Pour les sous-agents, recueillir la référence de leur propre session ; ne pas
leur faire écrire simultanément `effort.json`. Ne pas compter deux fois les
mêmes compteurs via la session parente et celle du sous-agent. Si la session
ne permet pas une attribution fiable, laisser les jetons non attribués.
Une session enfant dédiée peut être importée après sa fin. Pour l'orchestrateur,
annoncer la borne d'observation : les jetons et le coût de son dernier message
ne sont pas encore disponibles au moment où il produit son propre bilan.

Une trace existante peut alimenter le bilan sans inventer de chronométrage :

Si un chronomètre a été oublié pendant une interruption et que sa fin réelle
n'est pas établie, `interrupt <release> --entry ID --reason "…"` conserve
l'entrée et sa provenance, sans secondes ni jetons inventés. L'heure de cette
déclaration est une borne administrative, pas une durée de travail. Ne pas
utiliser `stop` à la reprise pour compter l'attente. Un nouveau passage peut
ensuite démarrer ; la période perdue reste inconnue et réservée contre les
doubles attributions. Aucune ancienne entrée n'est supprimée.

Sans plan ni estimation antérieure, déclarer d'abord la tâche avec
`add-task <release> --task T01 --title "Travail déjà exécuté"`. Cette commande
ne crée aucune prévision et ne remplace pas le titre d'une tâche existante.

```bash
python3 scripts/odoo_effort.py import-usage /chemin/projet/changelog/RELEASE \
  --task T01 --agent odoo-tester --provider claude --source /chemin/session.jsonl \
  --since 2026-09-09T09:00:00Z --until 2026-09-09T09:10:00Z
```

Omettre la fenêtre seulement pour une session dédiée à cette tâche et à ce
rôle. Un intervalle de messages importés ne prouve pas l'occupation continue
de l'agent. Documenter les trous de mesure, les sessions interrompues et les
traces indisponibles ; ni minutes ni jetons manquants ne valent zéro.

## Coût IA et clôture

Les jetons d'entrée, de sortie et de cache restent distingués suivant ce que
la source expose. Un coût **déclaré** provient d'un montant présent dans la
source ; un coût **calculé** applique des tarifs techniques datés aux catégories
mesurées. Ne pas les additionner pour une même consommation. Sans tarif fiable
ou avec des catégories incomplètes, présenter le coût comme indisponible ou
partiel, avec la raison. Zéro est réservé à une valeur réellement établie.

Les tarifs sont facultatifs et fournis localement :

```bash
python3 scripts/odoo_effort.py rates /chemin/projet/changelog/RELEASE --file tarifs-ia.json
python3 scripts/odoo_effort.py report /chemin/projet/changelog/RELEASE
```

Format du fichier, avec modèle, source et nombres **illustratifs** à remplacer
par une référence tarifaire réelle avant utilisation :

```json
{
  "cards": [{
    "provider": "codex",
    "model": "modele-a-renseigner",
    "effective_at": "2026-09-09T00:00:00Z",
    "currency": "USD",
    "basis": "api_equivalent",
    "source": "Référence tarifaire à renseigner",
    "scope": "Périmètre de facturation à renseigner",
    "input_per_million": 1,
    "cached_input_per_million": 0.1,
    "cache_write_input_per_million": 1.25,
    "output_per_million": 4
  }]
}
```

`effective_at` est une date ISO avec fuseau. `basis` vaut `api_equivalent` pour
une valorisation aux prix API, ou `contract` pour un tarif contractuel applicable ;
une valorisation API ne prouve pas la somme facturée pour un abonnement.
Aucun tarif n'est appliqué par défaut. Les cartes importées sont conservées en
copies historiques immuables. Le bilan présente les coûts par entrée, puis les
sous-totaux par devise et nature, sans additionner des devises ou des bases
de valorisation différentes. Il ne s'agit pas de tarifs client ; la commande
ne contacte aucun fournisseur, API ou modèle pour obtenir les prix ou les usages.

À la clôture, mesurer aussi recette et consolidation, puis produire le bilan.
Fermer le dernier chronomètre de consolidation **avant** le bilan final et le
sceau. `check-closure <release>` est un contrôle en lecture seule : code 1 si
des chronomètres sont actifs, sinon liste des rôles/tâches non mesurés et
sous-total connu. Le nouveau scellement exige ce contrôle, sans invalider les
sceaux historiques ni exiger de reconstituer les durées manquantes.
Relire par tâche et rôle : prévision initiale, révisions motivées, réalisé,
reprises incluses, écart comparable, jetons, coûts déclarés ou calculés et
couverture des mesures. Distinguer les **minutes d'agent cumulées** de la
**durée calendaire** : deux agents mobilisés dix minutes simultanément
représentent vingt minutes d'agent sur dix minutes écoulées. Les chevauchements
et périodes sans mesure doivent rester visibles ; ne pas soustraire du cumul
un chevauchement réel pour faire baisser le travail effectué.

Une ancienne release sans traces ni prévision reste clôturable si sa QA est
verte : signaler les absences sans reconstruire une estimation initiale.
Référencer le bilan dans le README et noter dans le journal les causes d'écart
utiles à une prochaine estimation. Comparer des tâches de périmètre, de voie,
de modèle et d'environnement proches ; l'historique améliore les prévisions
d'exécution des agents, jamais un chiffrage de travail humain.

Références pour distinguer prix techniques et abonnement :
[tarification API OpenAI](https://developers.openai.com/api/docs/pricing) et
[tarification Codex](https://learn.chatgpt.com/docs/pricing), consultées le
9 septembre 2026. Aucun prix de ces pages n'est recopié comme valeur par défaut.
