# Procédure — orchestration-graph

Chargement conditionnel depuis le profil canonique. Les chemins `docs/…` et
`roles/…` sont relatifs à `~/.odoo19-agents/`.

## Piloter le graphe

Le graphe exécutable est
`~/.odoo19-agents/workflows/odoo-workflow.json`. Après le briefing, ouvre un
run et enregistre le premier nœud :

```bash
FLOW=$(python3 ~/.odoo19-agents/scripts/odoo_flow.py start <racine> \
  --kind development --id <identifiant-court>)
python3 ~/.odoo19-agents/scripts/odoo_flow.py status "$FLOW"
python3 ~/.odoo19-agents/scripts/odoo_flow.py claim "$FLOW" briefing
python3 ~/.odoo19-agents/scripts/odoo_flow.py complete "$FLOW" briefing \
  --outcome development --evidence <fichier-du-briefing>
python3 ~/.odoo19-agents/scripts/odoo_flow.py ready "$FLOW"
```

Choisis `development_complex` seulement si l'analyse a réellement au moins
deux voies indépendantes utiles — standard ambigu, custom existant, copie
client à inventorier. Le graphe ouvre alors trois recherches en lecture seule,
puis une jointure de synthèse. Une demande triviale reste sur `development` :
créer trois agents pour économiser trente secondes coûte plus qu'il ne rapporte.

À chaque nœud :

1. affiche `status` au début d'une vague afin que l'humain voie la position,
   les agents actifs et les nœuds parallélisables ;
2. lis le profil de chaque nœud prêt, puis revendique les nœuds retenus avec
   `claim --owner <nom-explicite>` ; ne masque pas la sortie de la commande ;
3. exécute le rôle toi-même, ou délègue les nœuds d'une même vague quand ils
   sont indépendants et que cela améliore réellement délai ou qualité ;
4. donne à chaque agent le briefing déjà calculé, la demande, le chemin de la
   release, le mode du nœud et un fichier de preuve propre dans
   `.odoo-agents/flow-artifacts/<run>/<nœud>.md` ;
5. vérifie que le fichier de preuve existe, puis toi seul appelles
   `complete --outcome … --evidence <chemin>` ; si l'exécution s'arrête avant
   la preuve, rends le verrou avec `release --reason …` ;
6. laisse `complete` afficher la nouvelle position, puis recommence jusqu'à un
   terminal ou une porte humaine.

Le tableau de bord terminal fait partie du contrat d'orchestration. Il doit
montrer `ORCHESTRATEUR`, `AGENT · <profil>` ou `HUMAIN`, ainsi que `EN COURS`,
`PRÊT`, `ATTENTE HUMAINE` ou l'état terminal. Utilise un propriétaire stable et
lisible (`codex-odoo-tester-1`, `claude-odoo-analyst`, etc.) pour que la ligne
`EN COURS` identifie réellement l'exécutant. Le JSON (`--json`) est réservé à
l'automatisation, pas aux comptes rendus destinés à l'humain.

L'agent principal est le seul à modifier le fichier d'état, à arbitrer une
issue, à fusionner les fragments dans `revue_fonctionnelle.md` ou `qa.md`, et à
écrire le journal. Un agent délégué ne relance pas le graphe et ne délègue pas
à son tour. Au plus trois agents spécialisés travaillent en parallèle. Deux
agents ne modifient jamais le même module, la même base, le même pack Studio
ou le même document partagé.

Une porte humaine n'est jamais revendiquée. Après réception de la réponse,
consigne-la d'abord dans la revue ou le diagnostic, puis appelle `complete`
avec `--human-confirmed --evidence <fichier>`. Ce drapeau atteste seulement
que l'orchestrateur vient de recevoir la décision ; `odoo_instance.py` garde
ses propres confirmations obligatoires pour une écriture en production.

Si la délégation n'est pas disponible, applique le rôle indiqué toi-même. Les
preuves et les transitions sont identiques. **Les fichiers de la release sont
le canal de transmission** : `revue_fonctionnelle.md` → code → `qa.md` ; le
fichier de flow dit seulement où en est l'exécution.
