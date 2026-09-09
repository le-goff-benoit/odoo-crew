## 2026-09-09 — T42 transfert interne entre stocks de A — mode tâche (QA renforcée)

**Série** 19.0 (origine : défaut) · **module** transfert interne · **révision** fixture-t42 · **build** t42-1
**Jointure** `module_high_gate` — fusion des trois voies renforcées : `static.md`, `runtime.md`, `client.md`.

### Verdict
**VALIDÉ** — les trois critères obligatoires de la revue sont prouvés, chacun par une exécution portant sur le véritable acteur du critère ; aucun résultat obligatoire ne reste sans preuve.

### Résultats d'exécution (repris des fragments, non rejoués)
| Contrôle | Résultat | Détail |
|---|---|---|
| Lint du diff | vert | `static.md` — 0 erreur, révision fixture-t42 |
| Revue du diff | vert | `static.md` — règle multi-société et ACL présentes et syntaxiquement valides |
| Installation / mise à jour (base jetable) | vert | `runtime.md` — base `qa_t42`, build t42-1 |
| Tests ciblés | vert | `runtime.md` — 0 failed, 0 errors of 3 tests |
| Installation / mise à jour (copie client) | vert | `client.md` — base `copy_t42`, build t42-1 identique à `qa_t42` |
| Scénario T1 (gestionnaire A) | vert | `runtime.md` uid=41, sociétés=[A] ; confirmé sur `copy_t42` |
| Scénario T2 (gestionnaire B) | vert | `client.md`, contrôle complémentaire uid=42, non-superutilisateur, sociétés=[B] |

Aucune de ces exécutions n'a été rejouée à la jointure : les bases ne sont pas
disponibles dans ce contexte. Les preuves d'entrée sont les fragments eux-mêmes.

### Couverture des critères d'acceptation
| Critère | Couvert par | État |
|---|---|---|
| **T1** — transfert des trois unités par le gestionnaire A → une seule opération, quantité 3, trois identifiants attendus, sans doublon | `runtime.md` : uid=41 (véritable gestionnaire A, sociétés=[A], groupes utilisateur interne + gestionnaire stock) ; ids=[101,102,103] → transfert 501, quantity=3, opérations créées=1, identifiants exacts=True, uniques=True. Confirmé sur `copy_t42` (`client.md`). | **Satisfait** — les quatre résultats obligatoires (unicité de l'opération, quantité, exactitude et non-duplication des identifiants) sont prouvés, par l'acteur nommé au critère. |
| **T2** — le gestionnaire B, droits et sociétés ordinaires, lit les trois unités, reçoit AccessError au transfert, et rien ne change après le refus | `client.md`, contrôle complémentaire : session uid=42, superutilisateur=False, groupes utilisateur interne + gestionnaire stock uniquement, sociétés autorisées=[B]. Lecture de [101,102,103] → trois enregistrements attendus avec valeurs exactes. Appel du **vrai** transfert → `odoo.exceptions.AccessError` capturée et vérifiée. Quantités avant/après=[1,1,1], transferts avant/après=[501], comparaison complète égale après le refus. | **Satisfait** — les trois résultats obligatoires (lecture autorisée, refus en écriture, invariance après refus) sont prouvés dans la session du gestionnaire B, par appel du transfert réel. |
| **T3** — installation et mise à jour sur la copie ; lint du diff sans écart | `client.md` : installation et mise à jour OK sur `copy_t42`. `static.md` : lint du diff 0 erreur. | **Satisfait** |

### Ce que la jointure a écarté du décompte
- **Scénario administrateur de `client.md`** (uid=1, superutilisateur=True, contexte société B) : lecture et transfert possibles. Ce scénario **ne prouve rien sur T2** — la voie le déclare elle-même, et un contrôle en `admin` ne prouve jamais un refus de droits. Il n'est donc compté nulle part. Les données ont été remises exactement dans leur état initial après ce contrôle ; aucune trace résiduelle sur la copie.
- **T2 par la voie statique** : `static.md` constate la présence de la règle multi-société et déclare explicitement ne pas prouver les refus en exécution. Une lecture de code ne remplace pas l'exécution ; la présence de la règle n'est pas comptée comme preuve de T2. C'est le contrôle complémentaire uid=42 de `client.md` qui porte seul ce critère, et il suffit.
- **Captures, PDF, écrans** : hors contrat (« Aucun écran, PDF ni capture dans le contrat »). Leur absence n'est pas une lacune et ne pèse pas sur le verdict.
- **Facturation** : hors périmètre par la revue. Non contrôlée, à juste titre.

### Anomalies bloquantes
Aucune.

### Anomalies majeures / Remarques mineures
Aucune anomalie introduite par le diff n'a été constatée par les trois voies.

### Non testé / angles morts
- Les preuves sont des **attestations textuelles**, pas des preuves `odoo_evidence.py` avec empreinte du code. Ce qui relie les trois voies est déclaratif : même révision `fixture-t42`, même build `t42-1` sur `qa_t42` et `copy_t42`. Cette chaîne tient pour ce dossier, mais elle n'apporte pas la garantie de fraîcheur qu'une preuve JSON donnerait ; toute reprise du code invalide les trois fragments d'un coup.
- Le titre « VERT proposé » de `client.md` n'a pas été retenu comme preuve : le verdict ci-dessus est établi sur le contenu des contrôles, critère par critère.
- La recette complète (base neuve, suite entière, tours, désinstallation, mise à niveau) n'est pas jouée ici : elle appartient à la clôture de la release, qui reste ouverte.

### Appris (pour le journal)
- Une voie QA peut livrer, dans un même fragment, un contrôle non probant (session administrateur) **et** le contrôle probant du même critère. La jointure doit lire les deux et ne compter que le second : s'arrêter au premier paragraphe aurait fait rejeter un critère réellement satisfait.
- Un fragment qui déclare lui-même la portée de son contrôle (« ce scénario ne représente pas le gestionnaire B ») rend la jointure fiable ; c'est cette déclaration qui permet d'écarter sans deviner.
