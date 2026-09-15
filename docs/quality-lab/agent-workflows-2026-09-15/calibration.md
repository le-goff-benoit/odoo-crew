# Calibration ORM — N06 et N07

Deux cas synthétiques Odoo **19.0**, exécutés avec le `Lab` natif existant. Aucun
appel modèle dans cette calibration. Les projets ne contiennent aucune donnée
client et les modèles sont génériques, sans prétendre tester `stock.picking`
ou les modules privés des clients.

| Cas | Mécanisme | Oracle indépendant |
|---|---|---|
| N06 | Reprise des brouillons, positions finales 100/200, total hors lignes annulées, références déjà émises figées, société active | Sept invariants, dont utilisateur ordinaire multi-société, règle d’accès mono-société et idempotence. |
| N07 | Préparation périodique, zéro manuel et quantité partielle, duplication et reliquat puis cron | Douze invariants : reprise existante, valeurs manuelles, état figé, remise à zéro lors de copy, quantité résiduelle, absence de reliquat vide et rejeu stable. |

Les contrats sont entièrement arbitrés dans `cases/N06|N07/project/decisions/current.md`.
Une ancienne QA volontairement limitée reste visible dans chaque release ; elle
ne constitue pas une réception du contrat ajouté. N07 est réservé comme cas
inédit de transfert par rapport à N06 ; les résultats ne changent pas sa grille.

## Rejouer sans modèle

```bash
python3 benchmarks/native/oracles/N06_calibrate.py \
  --output /tmp/native-workflows-calibration-new --cases N06 N07
python3 -m unittest tests.laboratoire.test_native_workflow_cases -v
```

Chaque variante reçoit sa base Docker propre : installation du module défectueux,
amorçage des données existantes, modification candidate, `update`, reprise ORM
réellement exécutée puis oracle. Les variantes négatives modifient le candidat,
jamais l’oracle. Les oracles, références correctes et scripts de calibration sont
hors du projet transmis à l’agent natif.

## Campagne locale

Dossier d’archives : `/tmp/native-workflows-N06-N07-calibration-first/`.
Chaque sous-dossier conserve `setup.log`, `seed.log`, les appels réels au pont
(`bridge-events.json` et logs), le projet candidat et `oracle-000.log`.

La calibration ne mesure pas la qualité d’un agent, ses jetons ou son temps de
raisonnement. Elle valide seulement que les invariants choisis acceptent la
référence et rejettent les mutations. Le banc ne comporte ici ni navigateur,
ni PDF, ni migration entre versions, ni ordonnanceur cron asynchrone : les
méthodes de traitement périodique sont exécutées dans le vrai ORM Odoo 19.
N06 teste des droits utilisateurs réels ; N07 est un parcours fonctionnel sur
modèle synthétique sous le compte du shell. Les durées incluent Docker, base
neuve, installation, update, reprise et oracle.

L’analyseur de calibration refuse un oracle vide ou partiel, une exception de
runtime et une mutation qui échoue seulement sur un contrôle sans rapport avec
son défaut injecté : **4 tests unitaires verts**.


## Résultats finaux

**8/8 attentes satisfaites**, sans incident : les deux références passent et les six mutants sont rejetés par le contrôle métier ciblé. Tous les oracles terminent avec un code0 ; un booléen métier faux matérialise chaque rejet.

| Cas | Variante | Verdict attendu obtenu | Durée |
|---|---|---|---|
| N06 | reference | témoin accepté | 37.595s |
| N06 | issued_rewritten | mutant rejeté | 51.688s |
| N06 | other_company_rewritten | mutant rejeté | 47.891s |
| N06 | wrong_final_positions | mutant rejeté | 27.561s |
| N07 | reference | témoin accepté | 34.937s |
| N07 | zero_loses_manual_marker | mutant rejeté | 52.824s |
| N07 | copy_inherits_state | mutant rejeté | 55.868s |
| N07 | remaining_ignored | mutant rejeté | 40.815s |

Les résultats sont relus contre la liste complète des sept/douze contrôles dans `calibration-verification.json`. Le corpus final possède ses empreintes dans `final-corpus.sha256.json`. Le mot de passe admin/admin des bases jetables est explicitement initialisé pour le transport RPC du Lab ; la calibration métier passe par le shell, sans revendiquer une qualification RPC nouvelle.

[Preuves synthétiques compactes versionnées](evidence/orm/N06-N07/results.json) : résultats, logs des huit oracles, événements du pont, vérification et empreintes du corpus.
