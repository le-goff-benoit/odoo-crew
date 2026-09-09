# QA copie finale D-03 — VALIDÉ
Preuves dans preuves/d03/ : copy-before.log/json, copy-update.log (4,891 s), copy-validation-final.log et copy-reload.log.
8 essais réellement créés et commités avant changement D-02→D-03, IDs 9–16. Update seul conserve D-02. Même migration livrée exécutée explicitement deux fois : locations 30/52/62/72 → 30/40/65/75, prêts 30/40/50/60 inchangés. Entrées métier et IDs inchangés, SQL/ORM concordants.
Relecture nouvelle session après commit conforme ; seuls les huit essais créés supprimés et nettoyage commité, copie vide comme avant. write_date peut être actualisé par le standard : critère rectifié et incident conservé dans qa.md.
C6 validé. Manifest 19.0.1.0.0 inchangé : déclenchement automatique migration après incrément non testé, prévu à /odoo-close. Aucun déploiement.
