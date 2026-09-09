# QA — release 2026-09-09_02_transfert

## 2026-09-09 — T41 transfert interne de matériel — mode tâche (QA renforcée, jointure des trois voies)

**Série** 19.0 (origine : `.odoo-agents/config`) · **module** transfert T41 · **révision** fixture-t41 · **build** t41-1
**Nœud** `module_high_gate` du flow `d31-jours-negatifs` · **join** `all` sur `module_high_static_qa`, `module_high_runtime_qa`, `module_client_copy_qa`

> Cette section est une **consolidation**. Elle ne rejoue aucun contrôle : elle relit les
> attestations produites par les trois voies (`static.md`, `runtime.md`, `client.md`) et les
> confronte aux critères de `revue_fonctionnelle.md`. Aucune base ni exécution Odoo n'était
> disponible à la jointure ; rien ici n'est présenté comme nouvellement exécuté.

### Verdict
**REFUSÉ** — le critère T2 (refus d'accès du gestionnaire B) n'est prouvé par aucune des trois voies :
le seul scénario joué côté société B l'a été sous administrateur superutilisateur, qui contourne
précisément la règle à vérifier. La tâche touche aux droits : le critère est obligatoire et sa preuve
ne peut pas être reportée à la clôture.

### Preuves d'entrée relues
| Voie | Fichier | Ce qu'elle atteste | Ce qu'elle n'atteste pas |
|---|---|---|---|
| Statique | `static.md` | diff relu (règle multi-société et ACL présentes, syntaxiquement valides), lint du diff 0 erreur | le dit elle-même : ne prouve aucun refus en exécution |
| Exécution | `runtime.md` | base jetable `qa_t41` : install + update, 0 failed / 0 errors of 3 tests, scénario T1 avec le vrai gestionnaire A (uid=41, sociétés=[A]) | aucun appel avec le gestionnaire B |
| Copie client | `client.md` | copie `copy_t41` : install + update, T1 reconfirmé (transfert 501, quantité 3, trois identifiants), données remises dans leur état initial | le scénario « société B » est joué sous uid=1, superutilisateur=True ; aucun appel avec uid=42 |

### Couverture des critères d'acceptation
| Critère (texte intégral) | Résultat attendu | Preuve rattachée | État |
|---|---|---|---|
| **T1** — Le transfert des trois unités par le gestionnaire A crée une seule opération de quantité 3, liée aux trois identifiants attendus sans doublon. | R1.1 une seule opération, quantité 3 | `runtime.md` : uid=41, sociétés=[A], transfert=501, quantity=3, opérations créées=1 ; reconfirmé sur `copy_t41` (`client.md`) | **prouvé** |
| | R1.2 liée aux trois identifiants attendus, sans doublon | `runtime.md` : ids=[101,102,103], identifiants exacts=True, identifiants uniques=True | **prouvé** |
| **T2** — Le gestionnaire B, avec ses droits et sociétés autorisées ordinaires, reçoit AccessError à la lecture et au transfert de ces unités ; les quantités et opérations restent inchangées après les deux refus. | R2.1 AccessError à la **lecture** par le gestionnaire B | aucune : `client.md` a lu sous uid=1 superutilisateur (lecture **autorisée**), `static.md` ne constate qu'une présence de règle, `runtime.md` n'appelle pas B | **non prouvé** |
| | R2.2 AccessError au **transfert** par le gestionnaire B | aucune : `client.md` constate au contraire un transfert **possible** sous administrateur | **non prouvé** |
| | R2.3 quantités inchangées après les deux refus | aucune : les deux refus n'ont pas eu lieu, il n'y a pas d'état « après refus » à comparer | **non prouvé** |
| | R2.4 opérations inchangées après les deux refus | aucune, même raison | **non prouvé** |
| **T3** — Le module s'installe et se met à jour sur la copie ; le lint du diff n'introduit aucun écart. | R3.1 installation sur la copie | `client.md` : `copy_t41`, installation OK | **prouvé** |
| | R3.2 mise à jour sur la copie | `client.md` : `copy_t41`, mise à jour OK | **prouvé** |
| | R3.3 lint du diff sans écart | `static.md` : lint du diff, zéro erreur | **prouvé** |

**Satisfaction** — T1 satisfait, T3 satisfait, **T2 non satisfait** (0 de ses 4 résultats obligatoires prouvé). 2 critères sur 3.

### Anomalies bloquantes
#### B1 — T2 non prouvé : le scénario « société B » a été joué sous administrateur — `client.md`
**Constat** — la voie copie client propose « VERT » alors que son propre texte indique
`uid=1, superutilisateur=True`, lecture autorisée et transfert possible, et qu'aucun appel avec le
gestionnaire B `uid=42` n'a été effectué. Un superutilisateur contourne `ir.rule` : le scénario ne
peut ni confirmer ni infirmer T2.
**Conséquence** — la règle multi-société pourrait être absente, mal cadrée ou inopérante en exécution
sans qu'aucun des trois contrôles ne le voie. Le critère porte sur une **fuite de données entre deux
sociétés** : le laisser non prouvé revient à livrer un risque de droits non évalué.
**Correctif attendu** — rejouer T2 avec le véritable gestionnaire B (`uid=42`, sociétés autorisées
ordinaires, groupes non-admin), sans `sudo()`, et constater `AccessError` sur la lecture **et** sur le
transfert, puis relire quantités et opérations après les deux refus pour prouver R2.3 et R2.4. Un test
Python de droits dans le module est la forme durable de cette preuve.

#### B2 — Un titre de voie tenu pour un verdict — `client.md`, `static.md`
**Constat** — « VERT proposé » et « terminé » sont des états de voie, pas des preuves de critère. La
voie copie client reporte elle-même T2 à la recette de clôture.
**Conséquence** — la tâche touche aux droits : `/odoo-new` interdit le report à la clôture pour ce
niveau de risque. Émettre `pass` ici ferait disparaître le risque du dossier.
**Correctif attendu** — la jointure ne retient que la couverture par résultat ci-dessus ; c'est ce qui
est fait, d'où le refus.

### Anomalies majeures / remarques mineures
Aucune anomalie de code constatée. `static.md` ne relève aucun défaut sur le diff, `runtime.md` aucun
écart sur T1. **Aucun défaut d'implémentation n'est établi** : le manque porte sur la preuve, pas sur
le code connu.

### Non testé / angles morts
- **T2 dans son intégralité** : aucun appel avec `uid=42` sur aucune des trois voies.
- L'attribution des 3 tests verts de `runtime.md` n'est pas détaillée ; rien n'indique qu'ils couvrent
  les droits, ils ne sont donc pas comptés pour T2.
- Conformément au contrat : aucun écran, PDF ni capture — hors périmètre, hors décompte.
- Reprise impossible à cette jointure : aucune base ni exécution Odoo disponible dans ce contexte.
  L'issue enregistrée est donc `blocked`, l'arrêt prévu quand la reprise ne peut pas être jouée —
  et non `retry`, qui renverrait vers une correction de code qu'aucune preuve ne justifie.

### Appris (pour le journal)
- Un contrôle de droits joué sous `admin` / superutilisateur ne prouve rien : il prouve seulement que
  l'administrateur passe. Sur un critère de refus, l'identité de l'appelant fait partie de la preuve.
- Une voie QA propose une couleur ; seule la jointure, critère par critère et résultat par résultat,
  rend le verdict. Candidate à `LESSONS.md` si le motif se reproduit sur un autre projet.
