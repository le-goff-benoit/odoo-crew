# QA copie — D-31
Copie synthétique lab_client, transport autorisé par LAB.md. Inventaire initial vide. Un témoin valide id 1 (2 jours × 12,5 = 25) créé et commité avant update : seed.py/log.
Update réel réussi (update.json/log, environ 4 s). client.json/log : contrainte PostgreSQL lab_rental_days_nonnegative validée, définition CHECK ((days >= 0)); témoin conservé après update ; create négatif refusé pour rental/loan, aucun résidu ; write négatif refusé et toutes les valeurs du témoin relues identiques ; modification valide ultérieure et zéros explicite/par défaut acceptés. Témoins nettoyés et nettoyage commité ; copie revenue à 0 location avec la nouvelle contrainte active.
Critères C1, C2, C3 et C5 verts. Aucun contrôle de production ni navigateur nécessaire au périmètre.
