# Fragment QA copie client — lab_client (copie synthétique)

Base : `lab_client`, copie locale synthétique. Aucune autre base touchée ; aucune production
approchée. Module mis à jour avant la reprise (`preuves/02_update_copie.log`).

## Reprise des brouillons existants

| Passe | Résultat | Preuve |
|---|---|---|
| 1 | `REPRISE modifiés=2 inchangés=0 figés=1` — `LEGACY_DRAFT` 999.0 → 20.0, `LEGACY_FRACTION` 20.004 → 20.0 | `preuves/03_reprise_passe1.log` |
| 2 | `REPRISE modifiés=0 inchangés=2 figés=1` — aucune écriture | `preuves/04_reprise_passe2.log` |

L'idempotence est prouvée par exécution réelle, pas par lecture du code : la seconde passe ne
modifie aucun enregistrement. Le piège des 0,004 est franchi : la comparaison exacte a bien
corrigé `LEGACY_FRACTION`, qu'une tolérance à deux décimales aurait laissé faux.

## État final et comportement de l'action (`preuves/08_verif_copie.log`)

| id | nom | état | `snapshot_total` | attendu D-12 |
|---|---|---|---|---|
| 1 | LEGACY_DRAFT | draft | 20.0 | 20.0 ✅ |
| 2 | LEGACY_DONE | done | **777.0** | figé ✅ (ses lignes valent 20.0 : incohérence assumée par Q1) |
| 3 | LEGACY_FRACTION | draft | 20.0 | 20.0 ✅ |

Action jouée sur une **sélection mixte des trois dossiers**, puis `rollback` (aucune écriture
conservée) : aucune erreur levée, les deux brouillons restent à 20.0, `LEGACY_DONE` garde 777.0 et
sa `write_date` **inchangée** — preuve qu'aucun `write` ne l'atteint. Aucun état modifié.

**Observation non bloquante** : recalculer un brouillon déjà conforme met tout de même à jour sa
`write_date`. Sans effet sur D-12 (qui ne porte que sur le total des validés), mais à savoir si un
suivi de modification est branché plus tard.

**Verdict de la voie : VERT.**
