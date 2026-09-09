# Estimer et mesurer le travail des agents

`/odoo-estimate` prépare ou révise le temps d'exécution des agents pour une
release identifiée. Un **lot de travail** correspond à une tâche du plan ; la
release regroupe ces tâches. Le résultat est exprimé en minutes d'agent, sans
conversion en travail humain ni prix d'offre. Cette commande n'exécute pas le plan.

Lis le briefing, la revue et `plan.json` s'il existe, puis
`~/.odoo19-agents/docs/EFFORT.md` pour les commandes et formats. Sans plan,
`init` prépare le registre et `estimate --file` crée les tâches d'après les
champs `task` et `title`, sans créer de plan exécutable pour le chiffrage.

Pour chaque tâche, identifie les rôles effectivement nécessaires : analyse,
implémentation ou Studio, QA, orchestration et réception selon son périmètre.
La recette complète et la consolidation utilisent la tâche spéciale `RELEASE` :
ne les répète pas dans chaque QA de tâche. Une même conversation peut assurer
plusieurs rôles successifs ; le rôle mesuré est celui du travail exécuté.

Estime une fourchette optimiste / probable / pessimiste par couple tâche–agent.
Le point central est `(optimiste + 4 × probable + pessimiste) / 6`.
Appuie chaque ligne sur le périmètre, les critères, les modules et tests concernés,
l'état de la copie locale et les reprises plausibles. Donne les hypothèses,
la base de comparaison et le niveau de confiance. Cherche d'abord dans les
`bilan-effort.json` des releases comparables ; sans référence mesurée, indique
« jugement initial » et une confiance faible, sans inventer de durée historique.

Le temps comprend les outils et tests pendant lesquels l'agent reste mobilisé.
Le travail humain n'est pas estimé. Le chronomètre n'isole pas automatiquement
les attentes humaines : ferme-le avant une attente identifiée. Les tâches
indépendantes peuvent se chevaucher : la somme des minutes d'agent n'est pas
le délai de livraison. Ne promets pas un délai fondé sur un parallélisme hypothétique.

Initialise `effort.json`, puis enregistre les lignes avec
`odoo_effort.py estimate <release> --file <estimation.json>`. Présente
`estimation.md`, les hypothèses qui expliquent la fourchette et les manques de
mesure. Aucun tarif client n'est nécessaire. Un coût IA n'est chiffrable qu'à
partir d'un montant sourcé ou de jetons mesurés et de tarifs techniques datés.

Avant l'exécution, l'orchestrateur démarre la mesure par tâche et rôle avec
`start`, puis la ferme avec `stop` sur la même session ; voir `docs/EFFORT.md`.
La session doit être identifiable, même si le modèle n'est pas encore connu.
Les sous-agents rendent leur référence de session à l'orchestrateur, seul
écrivain du registre ; une session enfant dédiée peut être importée après sa
fin. Indique la borne d'observation : les jetons et le coût du dernier message
de l'orchestrateur ne sont pas disponibles dans son propre bilan.
À chaque reprise, conserve une nouvelle entrée mesurée.
Si le périmètre change, révise l'estimation avec `--reason` avant le nouveau
travail : l'historique et la prévision attachée au départ restent conservés.

Une tâche déjà commencée sans prévision reste « estimation initiale absente » ;
n'en recrée pas une après coup. Estime seulement le travail encore à venir en
le distinguant du réalisé. Sans plan, `add-task` permet de déclarer le travail
passé sans prévision artificielle. L'absence de traces anciennes ou de coût ne bloque
pas la QA : le bilan indique précisément ce qui manque. Termine par une entrée
de journal courte qui référence l'estimation et ses hypothèses principales.
