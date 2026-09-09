# QA — jointure des trois voies renforcées

## 2026-09-09 — T41 transfert interne entre stocks de A — mode tâche (risque élevé : droits)

**Série** 19.0 (origine : `.odoo-agents/config`) · **révision** `fixture-t41` · **release** `2026-09-09_02_transfert` (ouverte)

> **Nature des preuves.** Cette section est une **consolidation de fragments existants**
> (`static.md`, `runtime.md`, `client.md`), produits avant cette reprise. Aucune base et
> aucune exécution Odoo n'étaient disponibles ici : **aucun contrôle n'a été rejoué**.
> Les résultats ci-dessous sont ceux attestés par les fragments, cités comme tels.

### Verdict
**VALIDÉ** — les trois critères obligatoires du contrat sont couverts par des résultats
attestés dans les fragments ; le refus du gestionnaire B est prouvé en exécution dans une
session non-administrateur, et la partie du fragment client jouée sous administrateur est
écartée comme non probante.

### Résultats repris des fragments (aucun rejeu)

| Contrôle | Résultat attesté | Voie / source |
|---|---|---|
| Relecture du diff (règle multi-société, ACL) | présentes et syntaxiquement valides, aucun défaut constaté | statique — `static.md` |
| Lint du diff | 0 erreur | statique — `static.md` |
| Installation puis mise à jour (base jetable `qa_t41`, build `t41-1`) | terminées | exécution — `runtime.md` |
| Tests | 0 failed, 0 errors of 3 tests | exécution — `runtime.md` |
| Scénario T1, gestionnaire A réel (uid=41, sociétés=[A], interne + gestionnaire stock) | ids=[101,102,103], transfert=501, quantity=3, opérations créées=1, exacts=True, uniques=True | exécution — `runtime.md` |
| Installation et mise à jour sur la copie (`copy_t41`, build `t41-1` identique) | OK | copie client — `client.md` |
| T1 rejoué sur la copie | transfert 501, quantité 3, les trois identifiants | copie client — `client.md` |
| Refus du gestionnaire B (uid=42, superutilisateur=False, interne + gestionnaire stock, sociétés=[B]) | AccessError capturée et vérifiée à la lecture **et** à l'appel du vrai transfert | copie client — `client.md` |
| État des données après les deux refus | quantités avant/après=[1,1,1], transferts avant/après=[501], comparaison complète égale après chaque refus | copie client — `client.md` |

### Couverture des critères d'acceptation

Texte intégral des critères de `revue_fonctionnelle.md`, un résultat attendu par ligne.

**T1** — « Le transfert des trois unités par le gestionnaire A crée une seule opération de quantité 3, liée aux trois identifiants attendus sans doublon. »

| Résultat attendu | Preuve rattachée | État |
|---|---|---|
| une seule opération | `runtime.md` : opérations créées=1 (exécution, gestionnaire A réel uid=41) | prouvé |
| de quantité 3 | `runtime.md` : transfert=501, quantity=3 ; confirmé sur la copie (`client.md`) | prouvé |
| liée aux trois identifiants attendus | `runtime.md` : ids=[101,102,103], identifiants exacts=True | prouvé |
| sans doublon | `runtime.md` : identifiants uniques=True | prouvé |

**T2** — « Le gestionnaire B, avec ses droits et sociétés autorisées ordinaires, reçoit AccessError à la lecture et au transfert de ces unités ; les quantités et opérations restent inchangées après les deux refus. »

| Résultat attendu | Preuve rattachée | État |
|---|---|---|
| AccessError à la **lecture** | `client.md`, contrôle complémentaire : session uid=42, superutilisateur=False, sociétés=[B], `odoo.exceptions.AccessError` capturée et vérifiée | prouvé |
| AccessError au **transfert** | `client.md`, même session : appel du **vrai** transfert des unités [101,102,103], `AccessError` capturée et vérifiée | prouvé |
| quantités inchangées après les deux refus | `client.md` : quantités avant/après=[1,1,1], comparaison complète égale après chaque refus | prouvé |
| opérations inchangées après les deux refus | `client.md` : transferts avant/après=[501], comparaison complète égale après chaque refus | prouvé |

**T3** — « Le module s'installe et se met à jour sur la copie ; le lint du diff n'introduit aucun écart. »

| Résultat attendu | Preuve rattachée | État |
|---|---|---|
| s'installe sur la copie | `client.md` : installation OK sur `copy_t41` | prouvé |
| se met à jour sur la copie | `client.md` : mise à jour OK sur `copy_t41` | prouvé |
| lint du diff sans écart | `static.md` : lint du diff 0 erreur, révision `fixture-t41` | prouvé |

**Satisfaction** : T1 satisfait (4/4 résultats prouvés) · T2 satisfait (4/4) · T3 satisfait (3/3). **3 critères sur 3.**

### Éléments écartés du décompte

Ils figurent dans les fragments mais ne prouvent aucun résultat attendu ; ils sont
nommés ici pour qu'aucune reprise ne les recompte comme preuve.

- **Scénario administrateur du fragment copie client** — uid=1, superutilisateur=True,
  contexte société B, lecture autorisée et transfert possible. Le fragment le dit
  lui-même : *« Ce scénario ne représente pas le gestionnaire B »*. Un superutilisateur
  contourne ACL et règles d'enregistrement : ce scénario ne peut ni prouver ni infirmer
  T2. Il est **neutre**, non un échec — les données ont été remises dans leur état
  initial après ce contrôle, et l'état relevé ensuite ([1,1,1] / [501]) est cohérent
  avec l'état d'après-T1. T2 ne repose pas sur lui, mais sur la session uid=42.
- **« T2, lecture du code : règle société présente »** (copie client) et **« règle
  multi-société et ACL présentes »** (statique) — conformité de lecture. La voie statique
  précise elle-même qu'elle *« ne prouve pas les refus en exécution »*. Utile comme
  faisceau, sans valeur de preuve pour T2.
- **Titres de voies** (« terminé », « VERT proposé ») — non retenus comme preuves ; seuls
  les résultats détaillés le sont.

### Cohérence entre les voies
Les trois voies portent la même révision `fixture-t41` ; `qa_t41` et `copy_t41` déclarent
le même build `t41-1`. T1 est concordant entre la voie exécution et la copie client
(transfert 501, quantité 3, mêmes identifiants). Aucune contradiction entre fragments.

### Anomalies bloquantes
Aucune.

### Anomalies majeures / Remarques mineures
Aucune. Aucun défaut n'est constaté par les fragments.

### Non testé / angles morts
- **Rien n'a été rejoué dans cette reprise** : ni lint, ni installation, ni test, ni
  scénario. Le verdict vaut pour la révision `fixture-t41` et le build `t41-1` ; toute
  modification du code invalide ces preuves et impose de rejouer la voie concernée.
- Hors contrat, donc hors décompte : aucun écran, PDF ni capture (la revue les exclut
  explicitement) ; aucune facturation.
- Réservé à la clôture (`/odoo-close`) : suite complète du module, base neuve, tours,
  désinstallation, mise à niveau sur la copie du client, recette navigateur.
- Non couvert par le contrat T41 et donc non évalué : le comportement d'un gestionnaire B
  disposant de droits élargis, et le transfert entre les deux sociétés A et B.

### Appris (pour le journal)
- Un scénario joué sous administrateur (superutilisateur) ne prouve jamais un refus de
  droits : seule la session du profil réellement visé le fait. Le fragment copie client
  contenait les deux ; la jointure ne retient que la seconde.
