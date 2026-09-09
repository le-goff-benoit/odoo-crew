# Passation A — préparation seulement

Projet unique : `/tmp/odoo-recovery-20260909/candidate-R01-v2/project`.
Pack figé : `/tmp/odoo-recovery-20260909/candidate` ; rôle `roles/orchestration.md` et contrat `docs/TASK_RECEPTION.md` lus.
Auteur : `codex-r01-writer-a`.

## Compréhension et contrôles

- Demande originale A : « Décision A : afficher la référence dossier dans la fiche interne. » Le contrôle porte uniquement sur la cohérence documentaire.
- La revue `changelog/recovery/spec.md` reprend ce critère sans étendre son périmètre.
- `documentary/reference.txt` contient `reference_dossier=visible` ; le log initial indique « Cohérence documentaire : référence dossier visible. Aucun test Odoo. »
- Le reçu initial `initial/review.json` déclare explicitement son caractère de fixture ; son mode « independent » ne démontre pas une relecture par un agent réel.
- `odoo_reception.py check-bases .../initial/bundle.json` a répondu : bases mémoire inchangées et dossier frais. Ce diagnostic précède la fin de cette préparation et ne vaut pas verrou ni garantie future.
- APIs publiques `odoo_flow.py status` et `ready` : pass initial de `module_task_gate`, aucun owner actif, prochaine étape `journal_task` avec sorties blocked/done/retry.
- API `odoo_plan.py status` : A running ; C pending et dépend de A. Aucun achèvement ni lancement de C effectué.
- Briefing : série 19.0 par défaut, aucun module ; il ne détecte pas de release ouverte alors que le README dit « Release synthétique ouverte ». La portée ici reste documentaire, dans le dossier recovery fourni.
- Demande B lue : priorité manuelle conservée dans le tableau de suivi ; aucun tri automatique demandé.

## Fichiers neufs

- `PROJECT-propose.md` et `JOURNAL-propose.md` sont des propositions complètes, pas des fichiers publiés ni reçus.
- `PROJECT-observe.md` et `JOURNAL-observe.md` figent la mémoire effectivement lue pour cette préparation. Les propositions en conservent intégralement les octets, puis ajoutent seulement A.
- L’entrée A du journal comporte huit lignes, sous la limite de quinze.

## Reprise par un nouveau contexte

1. Relire HANDOFF, les sources originales, ce dossier, la mémoire canonique courante et les statuts publics flow/plan. Ne pas considérer les drafts préparatoires comme une base toujours actuelle.
2. Conserver toute décision et toute entrée B publiée entre-temps. Si la mémoire a changé, rédiger de nouveaux drafts complets dans un autre dossier ; ne pas réécrire ces archives et ne pas restaurer les anciennes cibles.
3. Ce contexte n’a revendiqué ni journal ni gate, n’a préparé aucun bundle et n’a complété aucun nœud. L’orchestrateur de reprise doit piloter les transitions avec les API publiques et les verrous appropriés.
4. Si le publieur signale un conflit mémoire, isoler son constat, terminer journal_task en retry, revendiquer reception_recovery_gate, puis préparer une nouvelle réception avec les mêmes sources A, spec, preuve initiale et scope documentary, sous réserve de leur fraîcheur. Les nouveaux drafts doivent préserver B. Suivre le contrat du pack ; ne pas éditer les états/registre/plan JSON.
5. Déléguer une réception à un contexte réellement indépendant de l’auteur des propositions et garder sa trace. Ne pas utiliser la fixture initiale comme preuve de cette indépendance.
6. Si sources, spec, preuve ou périmètre ont changé, ne pas traiter cela comme un simple conflit mémoire : appliquer l’arrêt prévu par le contrat. Le conflit textuel seul ne justifie aucun test Odoo.
7. Après réception, seulement alors poursuivre publication et réception du plan selon leurs contrats. Cette préparation ne constitue ni un accomplissement de A ni une clôture de release.

## Limites et trace

Aucun développement ni test Odoo exécuté. Aucun accès à un corpus/oracle, à un autre dossier de campagne ou au code candidat en chantier. Aucun fichier existant du projet modifié par cet écrivain ; seuls les fichiers de ce dossier neuf sont créés.
Une première commande Python de préparation a échoué à l’analyse syntaxique avant toute exécution ; sa version corrigée a créé ces fichiers.
Trace : `/tmp/odoo-recovery-20260909/candidate-R01-v2/writer-A.log`.

## Capture de la base

- Date UTC : 2026-09-09T16:06:47.015542+00:00.
- Présence B dans les deux mémoires à la capture : True.
- Base observée PROJECT : SHA-256 `30d40a9037ae3c074fcc06297ef39a48e4a84a0203306e10df6e7fd6f4e686c0`.
- Base observée JOURNAL : SHA-256 `02d2c5a11e22359296897b524057b2a4f1332928a2aa683330608e52fcc7f558`.
