# Continuation et retour d’enfant — essais natifs du 15 septembre 2026

Référence Crew `72702f4`. Codex CLI 0.154.0, Claude Code 2.1.269.
Modèles principaux demandés : Astra et Opus. Un parcours par fournisseur,
timeout 90 s par session, données synthétiques. Scripts d’essai conservés ici ;
fixture reproductible `tests/fixtures/orchestration_probe.py`.

## Résultats observés

| Parcours | Codex | Claude |
|---|---|---|
| Principal termine après A en annonçant B ; Stop demande de poursuivre | A → B → C lancées et réceptionnées, 24,460 s | A → B → C lancées et réceptionnées, 14,631 s |
| Un enfant rend son assertion ; le principal attend, réceptionne A puis continue | Session persistante : enfant revenu puis A → B → C, 39,957 s | Enfant revenu puis A → B → C, 30,387 s |

Les fichiers [continuation.json](continuation.json), [child-first.json](child-first.json)
et [child-persistent.json](child-persistent.json) conservent événements de lancement,
réceptions, métadonnées des hooks et empreintes des preuves/logs. Chaque réception
exige une vraie assertion subprocess et une preuve immuable. Aucun enfant ne
modifie le plan, ne réceptionne une tâche ni ne lance son successeur.

L’essai injecte volontairement l’arrêt après A. Le principal reprend les outils
après le garde, sans nouveau message humain. `SubagentStart` et `SubagentStop`
sont observés avec identité parent/enfant dans les deux transports.

## Limites et décision

- **Adopté :** état d’autorisation explicite, continuation Stop bornée, observation
  des fins d’enfants et retour natif au parent qui attend dans une session ouverte.
- Le premier essai enfant Codex avec `--ephemeral` échoue avant création :
  `no thread with id`. L’incident est conservé ; une reprise en session persistante
  corrige le transport. Les lancements ordinaires Tricorder sont persistants.
- **Non qualifié :** réveiller un parent déjà fermé/déconnecté. Aucun superviseur
  du cockpit ne recrée une session et aucune autorisation ne découle d’un événement.
- Pour Codex, le banc approuve explicitement les hooks générés et relus pour cette
  invocation avec `--dangerously-bypass-hook-trust`. L’application ne pose pas ce
  drapeau : la confiance native de l’utilisateur reste nécessaire au premier usage.
- La fixture clôt son graphe synthétique avec un marqueur `probe_only` ; elle
  qualifie réception et continuation, **pas** les étapes métier Odoo, la recette,
  les migrations ou le déploiement. Les durées ne classent pas les fournisseurs.
- Les attentes humaines, pauses, quotas et interruptions sont couverts par les
  tests déterministes ; aucun incident réel de quota n’est provoqué.

Sources : [hooks Codex](https://learn.chatgpt.com/docs/hooks),
[hooks Claude](https://code.claude.com/docs/en/hooks).
