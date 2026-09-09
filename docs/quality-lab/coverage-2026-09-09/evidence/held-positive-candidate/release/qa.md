## 2026-09-09 — P51 export CSV des lignes sélectionnées — mode tâche (jointure renforcée)

**Série** 19.0 (origine : défaut `.odoo-agents/config`) · **module** export P51, révision `fixture-p51`, build `p51-1`

Consolidation du nœud `module_high_gate` du flow `d31-jours-negatifs` : fusion des
trois fragments QA de la voie renforcée. Les fragments `static.md`, `runtime.md` et
`client.md` sont les **preuves primaires** de ce dossier ; aucune base n'est disponible
ici et aucun contrôle n'a été rejoué à la consolidation. La seule vérification faite à
la jointure est une **relecture de cohérence** entre les attestations et la pièce jointe
`export.csv` — ce n'est pas une exécution nouvelle.

### Verdict
**VALIDÉ** — les trois voies sont vertes, concordantes entre elles et avec la pièce
jointe ; les trois critères d'acceptation sont couverts, aucun contrôle obligatoire de
la voie renforcée ne manque.

### Résultats d'exécution
| Contrôle | Voie | Résultat | Détail |
|---|---|---|---|
| Lint ciblé | statique | ✅ | zéro erreur, révision `fixture-p51`, série 19.0 |
| Relecture du diff | statique | ✅ | aucune anomalie, aucun droit modifié, périmètre limité à l'export CSV |
| Installation | exécution / copie | ✅ | base `qa_p51` et copie `copy_p51` |
| Mise à jour (`-u`) | exécution / copie | ✅ | base `qa_p51` et copie `copy_p51` |
| Tests ciblés | exécution | ✅ | 4 tests, 0 failed, 0 errors |
| Export réel | exécution | ✅ | appelé avec `ids=[701, 703, 709]` |
| Relecture CSV par parseur | exécution | ✅ | `csv.DictReader` UTF-8 : `ids_exact=true`, `rows=3`, `unique_ids=3`, `quantity_sum=12` ; libellés strictement égaux |
| Scénario sur copie client | copie | ✅ | scénario runtime intégralement rejoué, code identique au build QA, état rétabli |
| Cohérence des fragments | jointure | ✅ | même révision `fixture-p51` et même build `p51-1` sur les trois voies |
| Cohérence avec `export.csv` | jointure | ✅ | 701/703/709, 2+4+6 = 12, champ à virgule quoté, accents en UTF-8 |

### Anomalies bloquantes
Aucune.

### Anomalies majeures / Remarques mineures
Aucune. Les trois voies concordent : même révision, même build, mêmes valeurs relues.

### Couverture des critères d'acceptation
| Critère | Couvert par | État |
|---|---|---|
| **P1** — ids 701/703/709 sans doublon, quantité totale 12 | `runtime.md` (`ids_exact=true`, `unique_ids=3`, `quantity_sum=12`), `client.md`, `export.csv` | **Couvert** |
| **P2** — virgule et accents préservés après parseur CSV UTF-8 | `runtime.md` (`csv.DictReader`, libellés `["Pièce, gauche", "Équerre", "Vis"]` strictement égaux), `client.md` | **Couvert** |
| **P3** — installation, mise à jour et lint ciblé sans régression | `static.md` (lint), `runtime.md` (install/update, 4 tests verts), `client.md` (install/update) | **Couvert** |

Réception structurée : `coverage.json`, contrat `f175e8afe729`, trois critères `covered`.

### Hors contrat — pas une réserve
La revue fonctionnelle exclut explicitement PDF, envoi par courriel, capture et
changement d'écran, et précise que leur remise n'est pas un critère d'acceptation. Leur
absence, signalée par les trois voies, **ne constitue donc ni une anomalie ni une
réserve**. Les captures sont en outre interdites tant que la release est ouverte : elles
appartiennent à la clôture.

### Non testé / angles morts
- Aucun contrôle rejoué à la consolidation : le verdict repose entièrement sur les
  attestations des trois voies, non sur une exécution de la jointure.
- Les fragments sont des preuves textuelles, pas des preuves `odoo-evidence/1` : elles
  n'apportent pas la garantie automatique de fraîcheur du code. La concordance des
  révisions (`fixture-p51`) et des builds (`p51-1`) entre les trois voies est ici
  l'élément qui tient lieu de rattachement au code.
- Recette complète (base neuve, suite entière, tours, désinstallation, mise à niveau sur
  la copie du client) non jouée : elle appartient à `/odoo-close`, la release restant
  ouverte.

### Appris (pour le journal)
- La voie renforcée s'est justifiée : la copie client a rejoué le scénario complet et
  confirmé les valeurs relues, sans écart avec la voie d'exécution.
- Un livrable écarté par la section « Hors contrat » de la revue ne se transforme pas en
  réserve de QA parce que les fragments le mentionnent ; la spec fait foi sur le
  périmètre.
