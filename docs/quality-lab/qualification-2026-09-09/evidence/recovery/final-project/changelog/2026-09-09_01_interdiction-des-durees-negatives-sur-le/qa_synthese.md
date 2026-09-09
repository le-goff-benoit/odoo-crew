# Synthèse QA de tâche — D-31, interdiction des jours négatifs sur `lab.rental`

**Module** `lab_rental` · **série** 19.0 · **release ouverte** `2026-09-09_01` ·
**verdict fusionné : VALIDÉ (pass)** · 8/8 critères couverts.

Rapport machine lié au contrat : `qa.md` · couverture : `coverage.json`.

## Reprise après interruption
Ce verdict est rendu par un second orchestrateur, après l'arrêt contrôlé du
premier au passage QA (`/work/.odoo-agents/recovery-interruption.json`,
`evidence_sha256 f46668512fcf4b5f7477bf250b6f2b14bcf0d670537acc7d50eae4c2a964d16e`,
`git_head 28fbbd6`, bases `lab_client`/`lab_qa` conservées). Les trois
revendications QA laissées par des propriétaires disparus ont été libérées avec
ce motif et cette preuve (`.odoo-agents/flow-artifacts/contrainte-jours-positifs/reprise/interruption.md`),
puis réattribuées à trois testeurs indépendants exécutés dans la même vague,
leurs verrous étant compatibles. Le briefing, la revue fonctionnelle et
l'implémentation, déjà franchis avec leurs preuves, n'ont pas été rejoués.
Aucun critère n'a été retiré, reformulé ni assoupli.

## Les trois voies fusionnées

| Voie | Nœud | Périmètre exclusif | Verdict |
|---|---|---|---|
| Copie client | `module_client_copy_qa` | `lab_client` : mise à jour + XML-RPC réel | pass (C02, C03, C04, C05, C07) |
| Exécution | `module_high_runtime_qa` | `lab_qa` : install neuve, mise à jour, tests | pass (C06, part suite de C08) |
| Statique | `module_high_static_qa` | conformité 19.0 et revue du diff | pass (C01) |

## A8 — la preuve qui manquait
L'implémentation déclarait explicitement **ne pas** avoir de preuve XML-RPC.
Elle est désormais établie par la voie copie client, et je l'ai relue moi-même
appel par appel :

- `create` sur `lab.rental` avec `days=-1` par le **vrai XML-RPC**
  (`qa_client/rpc/01_create_negative.json`) → `outcome=fault`, `fault_code=2`,
  `fault_string` = *« The operation cannot be completed: Le nombre de jours doit
  être positif ou nul. »*. La phrase métier exigée y figure **mot à mot** ; le
  préfixe anglais est le texte du noyau (`odoo/service/model.py::retrying`),
  non traduit dans le contexte de l'appel. Le critère C03 porte sur la présence
  exacte de la phrase, conformément au risque n°1 déjà arbitré dans la revue
  fonctionnelle — ce n'est pas un assouplissement décidé après coup.
- **Conservation des données après rejet** : relecture avant/après par RPC de
  l'enregistrement id 3 → `days=5`, `daily_rate=20.0`, `amount_total=100.0`
  inchangés ; `search_read` par nom rend **un seul** enregistrement, donc ni
  perte, ni doublon, ni enregistrement partiel.
- **Jour nul toujours valide** : `create(days=0)` → id 2 ; `write(days=0)` →
  `true` ; relecture `days=0`, `amount_total=0.0`.
- **Calcul du total inchangé** : 5 × 20 = 100 puis 0 × 20 = 0, constatés par RPC
  et par la suite de tests.

Un `Fault` quelconque n'aurait rien prouvé : le message a été lu, pas seulement
l'échec.

## Réserves consignées, non bloquantes
- **Dette antérieure** : clé `author` absente de `lab_rental/__manifest__.py`,
  vérifiée présente avant la tâche (`git show 28fbbd6:lab_rental/__manifest__.py`).
  Signalée par les voies statique et exécution, **non corrigée** : hors du
  périmètre fixé par la demande.
- **La suite de tests du module ne contient aucun test RPC** — elle couvre le
  niveau ORM. La composante « vrai appel RPC » de C08 est portée par les
  journaux XML-RPC de la voie copie client, pas par les tests. Constat rendu tel
  quel par la voie exécution, sans réécriture des tests.
- **Écritures faites sur la copie synthétique `lab_client`** : enregistrements
  `lab.rental` id 2 (`QA-CLIENT-ZERO-02`) et id 3 (`QA-CLIENT-BASE-03`), laissés
  en place comme preuve. Aucune production concernée, aucun déploiement.
- La preuve RPC n'établit ni le rendu visuel, ni les droits d'un autre
  utilisateur — hors périmètre de la demande, qui interdit de toucher aux écrans
  et aux droits.

## Périmètre tenu
Aucune vue, aucun droit (`security/ir.model.access.csv` inchangé), aucune
modification de `_compute_amount_total`. Le seul changement fonctionnel est la
contrainte SQL `models.Constraint('CHECK(days >= 0)', "Le nombre de jours doit
être positif ou nul.")` sur `lab.rental`, plus les tests et la version du
manifest.

**Release laissée ouverte** : la recette complète se joue à la clôture
(`/odoo-close`), pas ici.
