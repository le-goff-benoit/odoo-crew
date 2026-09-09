## 2026-09-09 — D-12 — QA de tâche sensible

**VALIDÉ** — lab_dispatch, Odoo 19.0 (manifest), version 19.0.1.0.0. Six critères satisfaits, reprise persistée et idempotente sur lab_client synthétique.

| Contrôle | Résultat | Preuve |
|---|---|---|
| Test rouge avant correction | 6 échecs, 0 erreur ; 110 au lieu de 20 et de 777 | red-final.json / red-final.log |
| Lint des 5 fichiers touchés | Ruff officiel + contrôles Odoo : 0 erreur, 0 avertissement | lint-final.json / lint-final.log |
| Installation finale sur QA fraîche | OK, 16 s au total | qa-runtime.json / qa-runtime.log |
| Tests ciblés (toute la suite actuelle du module) | 6/6, zéro erreur, échec ou skip | qa-runtime.log |
| Mise à niveau du module déjà installé sur la copie | OK | client-update.json / client-update.log |
| Première reprise avec commit | 1 brouillon : 999 → 20 ; validé : 777 → 777 | reprise-1.json / reprise-1.log |
| Rejeu dans un autre processus, avec commit | 0 dossier modifié, write_date compris | reprise-2.json / reprise-2.log |
| Relecture dans un troisième processus | 20/777 persistés, états et lignes préservés | client-final.json / client-final.log |
| Comparaison automatique des transactions et de l'inventaire initial | OK | verify_reprise.py / verify-reprise.log |

### Critères d'acceptation
| Critère | Couverture | État |
|---|---|---|
| C1 : exclure les annulées | test_draft_excludes_cancelled ; reprise réelle | OK |
| C2 : validé strictement ignoré | test_done_keeps_snapshot ; test_done_does_not_read_lines_or_write ; comparaison inventaires | OK |
| C3 : sélection mixte | test_mixed_selection | OK |
| C4 : aucune ligne / tout annulé / sélection vide | test_empty_and_cancelled_lines | OK |
| C5 : reprendre seulement les brouillons existants | reprise-1 + inventaire initial/final | OK |
| C6 : idempotence | test_recalculate_is_idempotent ; reprise-2 ; verify_reprise | OK |

### Relecture et remarques
Filtrage des brouillons avant lecture des lignes ; aucune élévation de droits, modification d'état, SQL ou compute automatique. Le script appelle l'action corrigée et s'arrête si la base n'est pas lab_client. Aucun droit changé.
L'absence préexistante d'author bloquait le lint : métadonnée synthétique renseignée, version conservée. Ruff manquait sur l'hôte : installé dans `.tools/venv`, ignoré par Git. Lint de reprise vert avec `builtins = ["env"]` et `--ignore T201`, adaptations explicites au shell qui fournit env et émet le rapport sur stdout.
Deux avertissements génériques du banc dans la QA : `--without-demo all` interprété True en 19.0 et valeur par défaut de http-interface ; zéro warning lié au module. Référentiel et transport laissés intacts.
Aucune anomalie bloquante restante. Le premier passage rouge et le premier lint en échec sont conservés comme historiques ; seules les preuves finales vertes servent au verdict. `green-dev` précède l'ajout d'author et n'est pas la preuve finale.

### Non exécuté / limites
Sources 19.1 absentes : comparaison au futur standard non vérifiable. Aucun navigateur, tour, désinstallation, document client ou recette complète de clôture : cette tâche ne change aucun écran et la release reste ouverte. Aucun déploiement. La QA sensible des données existantes est exécutée intégralement sur la copie synthétique autorisée.

### Rejeu et mémoire
Commande locale autorisée : `/bridge/labctl shell /work/changelog/2026-09-09_01_recalcul-des-brouillons-d12/reprise.py`. Une mise à niveau seule ne reprend pas les snapshots ; ce script est l'opération explicite de reprise, pas une migration automatique.
Appris : D-12 remplace D-11 ; préserver le snapshot validé impose de l'exclure avant tout calcul. L'idempotence est contrôlée entre transactions persistées, pas seulement dans le cache ORM.
Commit proposé (non créé) : `[FIX] lab_dispatch: preserve validated snapshots and repair draft totals`.
