# QA — PASS (ancienne portée)

Seule la création d’un brouillon vide a été vérifiée le 14 septembre. Les sélections mixtes, données existantes, saisies manuelles et parcours ultérieurs n’ont pas été contrôlés.

---

# QA de tâche — préparation périodique, duplication et reliquat (décision N-17)

**Date** 2026-09-16 · **module** `lab_preparation` · **série** 19.0 · **niveau** renforcé
(données existantes). Contrat : `revue_fonctionnelle.md`. Verdict généré depuis la couverture :
`qa_tache_preparation_n17.md` + `qa_coverage.json`. Le verdict de l'ancienne portée ci-dessus
n'est pas réécrit : il reste ce qu'il était.

## Verdict consolidé : **VERT sur les 12 critères**, avec deux réserves nommées

Trois voies exécutées et fusionnées ici (fragments intégraux dans `preuves/`) :

| Voie | Résultat | Preuve |
|---|---|---|
| Statique (lint + revue du diff) | conforme **sur le diff**, mais lint du module rouge sur une dette antérieure | `preuves/module_high_static_qa.md`, `preuves/lint.txt` |
| Exécution (rouge → vert, base neuve, mise à jour, XML-RPC, shell) | vert | `preuves/module_high_runtime_qa.md`, `preuves/tests_*.txt`, `preuves/parcours_copie_*.txt` |
| Copie client (reprise des données existantes) | vert | `preuves/module_client_copy_qa.md`, `preuves/cohorte_*.json`, `preuves/write_date_apres_reprise.json` |

Rouge d'abord établi : 9 échecs sur 11 tests sur le code d'origine
(`RECETTE … install=ko tests="9 failed, 0 error(s) of 11 tests"`), puis 0 échec après correction,
sur base neuve (`install=ok`) comme en mise à jour (`update=ok`).
Reprise : sur `lab_client`, l'enregistrement automatique corrompu passe de 999 à 7 ; les deux
saisies manuelles et le `done` ne sont **pas écrits du tout** (`write_date` d'origine conservée).

## Réserves à porter jusqu'à la clôture

1. **Lint du module rouge — dette antérieure.** `__manifest__.py` n'a pas de clé `author` ;
   elle manquait déjà à `HEAD`, hors de ce diff. Non corrigée ici (le rôle interdit de reprendre
   la dette sans demande). **À trancher avant `/odoo-close`** : c'est une erreur bloquante du lint.
2. **Idempotence : portée exacte.** Rejouer le cron conserve toutes les valeurs et n'écrit aucun
   enregistrement hors périmètre, mais réécrit les drafts automatiques avec la même valeur, donc
   leur `write_date` change à chaque passage. Conforme à la lettre de N-17 ; à signaler si la
   piste d'audit compte.

## Hypothèse portée par un critère
C10 repose sur l'hypothèse **H1** de la revue : `action_remainder()` sans reste positif clôt quand
même la source. C'est le seul point de N-17 qui supporte deux lectures — à confirmer par le métier.

## Ce qui n'est pas prouvé
Aucun rendu d'écran (le module ne livre ni vue ni menu), aucun droit d'un autre utilisateur
(aucun groupe livré ; seul l'admin synthétique a été exercé), aucun déploiement.
Recette complète de release et désinstallation : à `/odoo-close`.

## Réception documentaire
Effectuée par l'orchestrateur lui-même, **sans sous-agent disponible dans cette campagne** :
cette relecture n'est donc **pas indépendante** et le garde `prepare-reception`, qui exige une
réception indépendante, n'a pas été activé. Le garde de couverture (`bind-criteria` / `qa-report`),
lui, l'a été : 12 critères liés, empreintes vérifiées.
