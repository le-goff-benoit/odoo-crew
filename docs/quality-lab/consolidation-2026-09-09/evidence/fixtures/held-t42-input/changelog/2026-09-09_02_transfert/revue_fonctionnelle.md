# T42 — contrat entièrement arbitré
Le gestionnaire de la société A peut transférer les trois unités sélectionnées entre les deux stocks de A. Le gestionnaire B peut consulter ces unités mais ne doit pas les transférer. Aucune facturation. Aucun écran, PDF ni capture dans le contrat. La tâche touche aux droits : QA renforcée avant réception, release ouverte.

## Critères obligatoires
- **T1** — Le transfert des trois unités par le gestionnaire A crée une seule opération de quantité 3, liée aux trois identifiants attendus sans doublon.
- **T2** — Le gestionnaire B, avec ses droits et sociétés autorisées ordinaires, peut lire les trois unités et reçoit AccessError au transfert ; les quantités et opérations restent inchangées après ce refus.
- **T3** — Le module s'installe et se met à jour sur la copie ; le lint du diff n'introduit aucun écart.

La release reste ouverte. Aucune question de périmètre n'attend de réponse.
