# QA copie synthétique — N-17, lab_client 19.0

Update réel : update-confirmed.json/log, code retour 0, module chargé et registre mis à jour, aucun ERROR. Premier update également sorti à 0 ; update.json a été classé failed par le collecteur car --module exige un bilan de tests absent d'une simple update. L'appel a été réattesté sans cette option de tests ; aucune preuve modifiée pour masquer cet incident.
Reprise : repair.json/log. Cohorte vérifiée avant écriture : ids 1,2,3,4 et identités/états/quantités attendus. Une seule quantité modifiée (id 1, 999 → 7). Ids 2,3,4 intégralement préservés, métadonnées d'écriture incluses. Aucun enregistrement créé ou supprimé.
Le deuxième cron garde toutes les valeurs et n'appelle pas write (espion transactionnel). Commit explicite exécuté sur lab_client uniquement.
Relecture dans une nouvelle session : persisted.json/log, valeurs [7,0,2,88], états [draft,draft,draft,done], marqueurs manuels [False,True,True,False], quantités commandées/livrées et parents préservés.
Aucune planification permanente ajoutée. Les tests transactionnels sont dans lab_qa, aucun résidu dans lab_client.
Verdict : VALIDÉ pour A6 et l'update d'A7. Relecture non indépendante. Aucun déploiement.
