# SYN-42 — Diagnostic support

Le défaut est confirmé dans les pièces synthétiques : après le changement de prix, le montant reste à 30 au lieu de 36. L'écart est de 6 pour la ligne étudiée. Le nombre de lignes réellement concernées est inconnu.

Le calcul personnalisé ne se déclenche pas sur le changement du prix. Les montants affichés peuvent donc être faux après une modification du prix. Avant de les utiliser, l'utilisateur doit vérifier quantité × prix et suspendre la validation de la ligne en cas d'écart. Aucune donnée n'a été réparée.

La prochaine action revient au développeur, avec le support : reproduire le défaut sur une copie locale avec le test proposé, puis préparer la correction. Les lignes gratuites doivent rester autorisées, y compris après confirmation. L'analyste devra cadrer toute reprise des montants déjà enregistrés avant son exécution.

Le diagnostic s'appuie sur le code local, les sources Odoo de la bonne version et la trace fournie. Le briefing et les contrôles de conservation des fichiers ont été exécutés ; aucun test Odoo ni accès à une base client n'a eu lieu. Le test proposé reste à exécuter. Aucun correctif n'a été appliqué.

Les preuves, le scénario de test et le brouillon de réponse sont dans [diagnostic.md](diagnostic.md). Les mémoires proposées sont dans [PROJECT.md](PROJECT.md) et [JOURNAL.md](JOURNAL.md).
