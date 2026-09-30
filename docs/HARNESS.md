# Travailler avec un contexte ciblé et une mémoire durable

Le principal porte le résultat. Les programmes tiennent les empreintes, verrous,
publications et événements ; les rôles apportent les compétences utiles. Les
protections du graphe et d’accès aux instances restent en vigueur.

## Une entrée pour les opérations courantes

Depuis `~/.odoo19-agents/scripts/` :

```bash
python3 odoo_work.py prepare /projet --release release-id --task T01 --query "objet métier"
python3 odoo_work.py start /projet --release release-id --task T01
python3 odoo_work.py decision /projet --release release-id --file decision.json
python3 odoo_work.py receive /projet --release release-id --task T01 \
  --proof preuve.json --acceptance reception.md --memory consolidation.md --knowledge lecture.json
python3 odoo_work.py preflight /projet --proof preuve.json --environment environnement.json
```

`prepare` réunit état, contexte et collecte des retours. `start` réserve la tâche
et ouvre son flow via le moteur existant. `receive` appelle la réception du plan :
flow terminé, critères, sources, environnement des contrôles prescrits, dépendances
et preuves doivent être valides. `--check-proofs` conserve les contrats multi-contrôles.
Les commandes `odoo_flow.py` restent utilisées pour claim, complete et les portes
humaines ; cette façade ne les contourne pas.

`preflight` explique un refus de réutilisation et vérifie les sources/logs ainsi que
l’identité d’environnement fournie. Il ne mesure pas l’état vivant d’une base :
les données de départ et la pertinence des contrôles restent à établir. Un code
inchangé ne suffit pas à prouver une configuration ou une base inchangées.

Le briefing est ciblé par défaut. `--query` précise le besoin ; `--full-memory`
conserve la lecture intégrale et `--full-journal` les archives du journal.
Les décisions structurées **et** les rubriques de règles/contraintes de PROJECT
sont obligatoires, exceptions comprises. Si elles dépassent le budget, le rendu
l’annonce. Le budget ne constitue jamais un score de couverture métier.

## Décisions entre releases

Une contribution `decision`, `state: accepted`, avec `reviewed_by`, `review`,
`sources`, `scope` et éventuelles `exceptions`, publiée par `odoo_knowledge.py`
ou `odoo_work.py decision`, alimente aussi `.odoo-agents/DECISIONS.json`.
Identifiant projet : `<release>--<id>`. Une proposition reste une proposition.
L’état de réalisation initial est `unknown`, jamais un déploiement inféré.
Pour un plan, `affects_tasks` et `impact_reason` restent requis.

Une nouvelle décision peut donner `supersedes_project: "ancienne-release--K01"`.
Le prédécesseur devient historique. Un remplacement concurrent est refusé avant
publication ; une répétition identique est idempotente, y compris après interruption
entre contribution et projection. Les sources des décisions courantes sont
vérifiées ; les sources historiques remplacées ne bloquent plus leur successeur.
Un successeur périmé ne ressuscite pas l’ancienne règle.

La reprise de l’existant est volontaire : relire source et exceptions, puis publier
une contribution acceptée. Ni un journal ni sa date ne prouvent un arbitrage.
Les règles de PROJECT restent obligatoires même avec un registre partiel ; lors
d’une migration complète, retirer explicitement la rubrique devenue historique.
Aucune base vectorielle ni deuxième système de notes n’est requis.

## Ajouts de mémoire

`prepare-reception --memory .odoo-agents/PROJECT.md=+projet-ajout.md --memory
.odoo-agents/JOURNAL.md=+journal-ajout.md` fige seulement les fragments proposés.
La réception reste sourcée. Sous verrou, `publish-memory` préserve le contenu
antérieur, accepte les ajouts indépendants et reconnaît les fragments déjà publiés.
Une modification de la base, du fragment ou des preuves bloque la publication.
Le mode historique `=draft` conserve la comparaison et le remplacement intégraux.
Un fragment ne sert pas à faire coexister deux règles contradictoires : remplacer
explicitement la décision structurée.

Une correction documentaire conserve les tests valides. Les motifs de reprise se
consignent avec leur source : défaut métier, contrat, environnement, preuve
périmée, documentation ou fournisseur. La limite existante des reprises du graphe
n’est pas modifiée ; un incident technique ne se présente pas comme défaut métier.

## Retours automatiques

Collecte à la réception/réouverture/report d’une tâche, aux issues QA retry/blocked,
au scellement, au point réalisé et à la clôture, ainsi qu’à la publication d’une
observation de déploiement. `prepare` rattrape également les retours antérieurs.
Après une entrée de journal tardive :

```bash
python3 odoo_feedback.py collect /projet --release release-id
python3 odoo_feedback.py show /projet --release release-id
python3 odoo_feedback.py record /projet --release release-id \
  --kind human_correction --source changelog/release-id/retour.md --text "citation exacte"
python3 odoo_feedback.py triage /projet --id IDENTIFIANT --status reviewed \
  --reviewer responsable --reason "contre-exemple et essai à traiter par /odoo-improve"
```

Les observations sont immuables dans `.odoo-agents/feedback/events/`, identifiées
par leur contenu. Leur extrait reste consultable quand le journal évolue. Le tri
est séparé dans `triage.json` ; les rapports sous `reports/` sont reconstruisibles.
Les événements du journal sans release explicite restent au niveau projet.
Les textes identiques sont regroupés en conservant les occurrences. Les retours
après clôture se collectent sans modifier les artefacts scellés.

Une collecte en échec laisse un avertissement visible et une reprise possible ;
elle n’invalide pas les tests produit. La collecte ne consomme aucun appel modèle.
La qualification et la synthèse restent le travail explicite de `/odoo-feedback`,
puis `/odoo-improve` pour adopter une règle générale avec contre-épreuve. Une
routine LLM autonome ne s’installe pas sans budget ; aucun classement de modèles
ni gain de temps ne découle du nombre d’événements collectés.

## Tricorder

L’accueil **Travail** montre les tâches reçues, les points à examiner, la suite et
la dernière clôture. **Nouvelle demande** ou **Reprendre** présente action, projet,
release et agent avant lancement dans un nouveau terminal contextualisé. Les
sessions existantes gardent leur contexte. Les graphes, quotas et autres instruments
restent accessibles sous **Détails**. **Mémoire** expose décisions et retours sourcés.
Tricorder lance le CLI fournisseur ; Crew et l’agent appliquent les contrôles.
