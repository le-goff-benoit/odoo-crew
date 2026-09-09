Le diagnostic de SYN-42 identifie un bug dans le module : changer le prix seul ne relance pas le calcul du montant. Le scénario fourni conserve 30 au lieu de 36, soit un écart de 6 sur une ligne. Les lignes gratuites doivent rester autorisées, même confirmées.

En attendant la correction, l'utilisateur peut contrôler quantité × prix et mettre de côté les lignes dont le montant est incohérent. Le [diagnostic](diagnostic.md) décrit aussi un contournement technique à vérifier sur une copie.

La prochaine action revient au développeur : exécuter le test préparé sur une base locale, constater l'échec, puis corriger le déclenchement du calcul dans la suite de développement. Le testeur vérifiera aussi les lignes gratuites. Les anciens montants demanderont une analyse distincte avant toute réparation.

Les preuves sont du code local et une trace synthétique fournie. Aucun test Odoo, accès client, changement de code ou recalcul de données n'a été effectué. Le nombre de lignes réellement touchées reste inconnu. Le [test proposé et les critères de correction](diagnostic.md) sont prêts ; les [décisions du projet](PROJECT.md) et le [journal](JOURNAL.md) sont conservés et complétés.
