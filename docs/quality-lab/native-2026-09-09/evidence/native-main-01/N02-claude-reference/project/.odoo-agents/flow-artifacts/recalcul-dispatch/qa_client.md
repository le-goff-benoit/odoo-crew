# Fragment QA copie client — point 1

Copie **synthétique locale `lab_client`** uniquement (aucune autre base autorisée par D-12 ;
aucun accès production, aucun déploiement).

## État avant
`.odoo-agents/flow-artifacts/recalcul-dispatch/inventaire-avant.txt` :
2 dossiers (1 brouillon, 1 validé), 4 lignes dont 2 annulées.
- id=1 `draft` : snapshot 999,00 · attendu 20,00 · brut 110,00 → divergent
- id=2 `done` : snapshot 777,00 · figé par contrat, quel que soit le total de ses lignes

## Mise à niveau du module
`labctl update` sur `lab_client` : registre rechargé, aucune erreur.

## Reprise — passe 1 (`reprise-passe1.txt`)
| Contrôle | Résultat |
|---|---|
| Brouillons divergents détectés | 1 / 1 |
| Enregistrements écrits | **1** (id=1 : 999,00 → 20,00) |
| Validés : total et `write_date` | **strictement intacts** (id=2 reste à 777,00) |
| Brouillons convergés | OUI |

## Reprise — passe 2, rejouée à l'identique (`reprise-passe2.txt`)
| Contrôle | Résultat |
|---|---|
| Brouillons divergents détectés | 0 / 1 |
| Enregistrements écrits | **0** → **idempotence prouvée** |
| Totaux | inchangés (20,00 et 777,00) |

## Contrôle croisé — sélection mixte réelle sur la copie (`copie-selection-mixte.txt`)
`action_recalculate()` appelée sur les 2 dossiers à la fois :
- id=1 `draft` : 20,00 → 20,00, `write_date` modifiée (écriture normale d'un brouillon) ;
- id=2 `done` : 777,00 → 777,00, **`write_date` inchangée** → aucune écriture sur le validé ;
- aucune exception levée.
Contrôle joué puis annulé (`rollback`) : la copie reste dans l'état issu de la reprise.

**Observation mineure** : `action_recalculate` réécrit un brouillon même quand la valeur ne change
pas (`write_date` bouge). Conforme au contrat, qui n'exige la non-écriture que pour les validés ;
c'est le script de reprise qui filtre les divergents pour rester idempotent. À arbitrer si un
tracking est ajouté un jour sur `snapshot_total`.

**Verdict de la voie** : VERT — reprise conforme, idempotente, validés figés.
