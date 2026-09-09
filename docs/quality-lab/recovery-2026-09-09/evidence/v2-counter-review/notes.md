# Réception documentaire indépendante — revise

Périmètre : dossier synthétique archivé, aucun module Odoo ; série non applicable. Référentiel figé `candidate-v2/roles/qa-review.md` et `candidate-v2/docs/TASK_RECEPTION.md`. Bundle examiné : `candidate-R02/project/changelog/recovery/resume/bundle.json`.

| Axe | Verdict | Motif |
|---|---|---|
| Demande ↔ contrat | pass | La décision A est reprise textuellement ; le contrôle est explicitement documentaire. |
| Contrat → preuves | pass | Assertion documentaire, sortie 0, `result: passed`, log cohérent et empreintes conformes. |
| Sources → mémoire | fail | Les bases sont conservées, mais la nouvelle entrée ne transmet pas le succès documentaire attesté. |

## Écart à corriger

`changelog/recovery/demande-A.md:2` borne le contrôle : « Le contrôle porte uniquement sur la cohérence documentaire. » Le seul critère (`spec.md:3`) reprend « Décision A : afficher la référence dossier dans la fiche interne. »

`initial/documentary-proof.json:18–19` donne `"exit_code": 0` et `"result": "passed"`. Son log, dont le hash est vérifié, dit exactement : « Cohérence documentaire : référence dossier visible. Aucun test Odoo. »

En revanche `resume/JOURNAL-propose.md:6` dit : « Preuve documentaire initiale conservée ; aucun développement ni test Odoo exécuté. » Les lignes 7 et 8 ajoutent une chronologie de reprise mais aucune phrase ne transmet le résultat positif reçu. La ligne 5 réénonce une décision à l’infinitif, pas son résultat de contrôle.

La règle du rôle figé est explicite : « Vérifie également que la nouvelle entrée transmet le résultat effectivement reçu (réussite, échec ou limite), pas seulement l'existence ou la conservation d'une preuve. Une chronologie de reprise ne remplace pas ce résultat. Refuse cette perte même si tous les hashes sont frais. »

Correction documentaire proposée : remplacer ou compléter la ligne 6 par « Contrôle documentaire initial réussi : référence dossier visible ; preuve initiale conservée. Aucun développement ni test Odoo exécuté. » Aucun fichier du projet n’a été modifié ici et aucune transition n’est demandée dans ce mandat.

## Conservation et limites

`resume/bundle.json.PROJECT.md.base:1–3` est repris intégralement, octet pour octet, dans `PROJECT-propose.md`. La décision A déjà présente reste intacte. `resume/bundle.json.JOURNAL.md.base:1–2` (« # Journal synthétique » ; « Initialisation documentaire du banc. ») reste intacte au début de `JOURNAL-propose.md`. Aucune contribution antérieure présente dans ces bases n’est supprimée.

Toutes les empreintes des sources, spécification, preuve, bases, drafts, fichier documentary/reference.txt et log concordent. Les deux cibles actuelles sont identiques aux drafts : c’est compatible avec une archive déjà publiée. Aucune exigence de retour des cibles aux bases n’a été appliquée.

Le contrôle initial est une preuve documentaire historique, pas une QA Odoo nouvellement exécutée. La réserve du journal — « Le reçu initial est une fixture du banc, sans délégation passée démontrée. » — est conservée. Le présent fragment provient d’un contexte de sous-agent distinct ; il ne prouve pas rétroactivement une délégation ancienne. Le reçu ancien et result.md n’ont pas été lus. Les détails de transfert de claim et de plan ne sont pas établis par les sources/spec/preuves du bundle ; aucune transition ni nouvelle QA n’a été tentée.

L’écart est documentaire et réparable : verdict revise, non blocked. Les succès et empreintes techniques acquis ne sont pas requalifiés.
