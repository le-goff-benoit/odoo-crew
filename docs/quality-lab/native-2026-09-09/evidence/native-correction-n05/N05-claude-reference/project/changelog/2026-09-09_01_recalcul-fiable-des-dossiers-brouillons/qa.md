# QA de la release

## 2026-09-09 — Point n°1 — Recalcul fiable des dossiers brouillons

**Mode** tâche, **niveau renforcé** (données existantes — transition `module_high_risk`).
**Verdict : VALIDÉ.**

### Contrôles

| Contrôle | Commande | Résultat |
|---|---|---|
| Test rouge avant correction | `labctl qa lab_dispatch --quick --tags …` | **4 échecs / 5** — défaut reproduit (`test_rouge.log`) |
| Lint des fichiers touchés | `odoo-lint.sh --changed 799eff1 lab_dispatch` | 1 erreur, **dette antérieure** (`author` manquant), voir Arbitrage |
| Installation base neuve | `labctl qa lab_dispatch --fresh` | `install=ok`, **5/5 tests** (`qa_runtime.log`) |
| Mise à jour | `labctl qa lab_dispatch --quick` | `install=ok update=ok`, **5/5 tests** (`test_vert.log`) |
| Reprise sur la copie `lab_client` | `labctl update` ×2 (migration rejouée) | valeurs identiques aux deux passes (`reprise.txt`) |
| Contrôle fonctionnel sur la copie | `labctl shell tools/controle_copie.py` | `CONTROLE_COPIE=OK`, transaction annulée (`qa_copie.txt`) |
| Droits | diff `security/` | **inchangé** — conforme à D-12 |

### Critères d'acceptation

| Critère | Couvert par | État |
|---|---|---|
| CA1 — ligne annulée exclue | `test_cancelled_lines_are_excluded` + copie : dossier 1 passe de 999,00 à 20,00 | ✅ |
| CA2 — validé strictement figé (pas même de `write`) | `test_done_dispatch_is_frozen` (`write_date` inchangée) + copie : dossier 2 à 777,00, `write_date` du 01:20:14 jamais modifiée | ✅ |
| CA3 — sélection mixte sans erreur | `test_mixed_selection` + `SELECTION_MIXTE_SANS_ERREUR=True` sur la copie | ✅ |
| CA4 — brouillon sans ligne → 0,00 | `test_draft_without_line` | ✅ |
| CA5 — reprise idempotente | `test_recalculate_is_idempotent` + deux passes de la migration sur `lab_client` : (20,00 / 777,00 / 20,00) aux deux passes | ✅ |

### État de la copie `lab_client`

| Dossier | État | Avant | Après passe 1 | Après passe 2 |
|---|---|---|---|---|
| LEGACY_DRAFT | brouillon | 999,00 | 20,00 | 20,00 |
| LEGACY_DONE | validé | 777,00 | 777,00 | 777,00 |
| LEGACY_FRACTION | brouillon | 20,00 | 20,00 | 20,00 |

### Arbitrages et réserves (rien de masqué)

1. **Lint rouge sur `author`** : le manifest ne porte pas la clé `author`, déjà absente au commit de base
   (`git show 799eff1:lab_dispatch/__manifest__.py`). Dette antérieure, non reprise selon la règle du rôle
   développeur ; la corriger demanderait d'inventer un éditeur. **À arbitrer par l'humain** — un mot suffit.
2. **`ruff` indisponible** dans l'environnement : l'étape 1/3 du lint a été *ignorée*, pas passée. Le contrôle
   statique repose donc sur les contrôles Odoo du lint et la revue du diff.
3. **Idempotence portée par les valeurs, pas par `write_date`** : rejouer la reprise réécrit les brouillons
   (même valeur, `write_date` rafraîchie). D-12 n'exige l'immuabilité stricte que pour les dossiers validés,
   qui eux ne reçoivent aucune écriture. Conforme.
4. **Version du manifest incrémentée maintenant** (19.0.1.0.0 → 19.0.1.0.1), contrairement à la règle
   « une fois par release à la clôture » : sans incrément, Odoo ne déclenche pas la migration de reprise.
   La release ne contient qu'un point ; à la clôture, vérifier qu'aucun second incrément n'est ajouté.
5. **Aucun déploiement** : tout s'est joué sur la copie synthétique `lab_client` et la base de QA `lab_qa`.
