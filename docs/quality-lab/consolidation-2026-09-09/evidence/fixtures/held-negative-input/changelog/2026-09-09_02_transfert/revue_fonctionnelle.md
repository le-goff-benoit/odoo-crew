# T41 — contrat entièrement arbitré
Le gestionnaire de la société A peut transférer les trois unités sélectionnées entre les deux stocks de A. Le gestionnaire B ne doit ni transférer ni consulter ces unités. Aucune facturation. Aucun écran, PDF ni capture dans le contrat. La tâche touche aux droits : QA renforcée avant réception, release ouverte.

## Critères obligatoires
- **T1** — Le transfert des trois unités par le gestionnaire A crée une seule opération de quantité 3, liée aux trois identifiants attendus sans doublon.
- **T2** — Le gestionnaire B, avec ses droits et sociétés autorisées ordinaires, reçoit AccessError à la lecture et au transfert de ces unités ; les quantités et opérations restent inchangées après les deux refus.
- **T3** — Le module s'installe et se met à jour sur la copie ; le lint du diff n'introduit aucun écart.

La release reste ouverte. Aucune question de périmètre n'attend de réponse.
