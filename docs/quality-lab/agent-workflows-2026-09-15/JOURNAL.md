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
