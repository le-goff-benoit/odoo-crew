# Journal de la boucle

## 15–16 septembre 2026 — Préparation

- Corpus antérieur relu : calibrations W01–W06 distinctes des essais d’agents.
- N06 et contre-épreuve N07 : données synthétiques, oracle hors contexte candidat.
- W03 étendu aux trois cohortes PDF, deux séries et absence d’écriture comptable.
- Réception mécanique liée au code final, temps de préparation et d’agent séparés.
- Revue indépendante : erreur fournisseur mal classée corrigée avant gel du runner.
- Tricorder : faux vert JUnit mixte reproduit et corrigé, avec contrôles de cohérence.
- Protocole avant/après figé : huit appels natifs maximum, aucun changement de modèle.

## 16 septembre — Incident de préparation conservé

- `/tmp/crew-agent-workflows-20260915` : les deux builds échouent avant tout appel natif.
- Cause : les imports `tests.pilotage` de la référence ne sont pas résolus depuis `/work`.
- Transport corrigé à l’identique pour les deux variantes : build depuis le répertoire du pack.
- Aucun profil de référence retouché ; zéro appel modèle consommé, plafond natif huit inchangé.
- Nouveau dossier explicite `/tmp/crew-agent-workflows-20260916-v2` ; premier essai conservé.
- `build.sh` corrigé aussi pour les installations depuis un autre dossier ; build depuis `/tmp` : 388 tests, un ignoré, 35 profils et deux blocs conformes.

## 16 septembre — Référence reçue et candidat ciblé

- N06 référence : Codex 633,49s, Claude 772,17s ; oracle métier vert dans les deux cas.
- Réceptions indépendantes : deux acceptations avec réserves, lint global rouge sur dette initiale `author` ; aucune réception mécanique entièrement verte.
- Codex : deux détours CLI ; aucun nouveau test vert inutile prouvé.
- Claude : QA007/014 et relances lint justifiées par portée ou sources changées ; QA015 redondante (22,14s), inventaire relancé pour garder sa sortie (1,31s).
- Candidat : capture de preuve prévue avant premier test, rouge/vert séparés, réception des preuves valides avant toute réexécution ; fragments QA référencent le contrat et les logs communs.
- Contradiction éditoriale « tests d’abord / tests après code » retirée du rôle développeur.
- Aucune règle ajoutée contre les relances lint justifiées ; aucun critère métier retiré.
- Cas N07 natif toujours non exécuté ; modèles, efforts, budgets et corpus inchangés.


## 16 septembre — Contre-épreuve, arbitrage et installation

- Huit appels réalisés, modèles/efforts constants ; sept terminés et un timeout à 900 s.
- Huit oracles métier verts ; réceptions indépendantes : sept avec réserves, un rejet.
- N06 Claude : 772,17 → 574,37 s ; N07 Claude : 796,50 s → timeout, ajout de cron et réception incomplète.
- Codex : N06 633,49 → 692,70 s ; N07 627,74 → 629,70 s, aucun gain démontré.
- Candidat complet 015e8a3 conservé expérimental et retiré des profils actifs ; aucun lien causal inventé.
- Seule clarification éditoriale rouge avant correction retenue ; combinaison finale non rejouée en natif.
- Aide CLI de preuve clarifiée ; statut des essais en cours corrigé ; six nouveaux tests déterministes.
- Graphe, 394 tests (un ignoré), build isolé/actif et parité 35 fichiers + deux blocs valides.
- Contrôles de la campagne nettoyés ; aucune ressource Docker préexistante arrêtée.
- Résultats, revues, contre-exemples et limites publiés ensemble ; aucune reprise cachée.
