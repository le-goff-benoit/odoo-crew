# Implémentation N-17

Odoo 19.0, lab_preparation/models/business.py : copy=False sur les quatre champs de progression ; saisie explicitement manuelle même à zéro ; reliquat singleton au restant positif avec source done ; cron limité aux drafts automatiques et évitant les écritures à valeur égale.
Tests : 9 méthodes et sous-cas de TestPreparation, import tests/__init__.py, classe commune TransactionCase (aucune dépendance métier standard).
Rouge tests-rouge.log : 14 assertions échouées / 9 tests, aucune erreur d'exécution ; vert tests-vert.json : 0 échec, 0 erreur / 9 tests ; installation et update QA OK.
Lint complet du pont : Ruff bloquant et conseils verts, 1 défaut structurel préexistant (author absent du manifest). Le contrôle ciblé conserve aussi cette anomalie structurelle malgré --only-files. Manifest identique à HEAD ; aucune anomalie sur les quatre fichiers nouveaux/modifiés. Ne pas présenter le lint global comme vert.
Update copie : commande /bridge/labctl update, sortie 0, module chargé et registre mis à jour (update.log). Le reçu update.json marque failed car --module réclame un bilan de tests : erreur de capture, pas échec Odoo ; conserver le reçu tel quel. Les prochains contrôles shell seront capturés sans --module. Aucun test métier n'était prévu dans cette commande d'update.
Version laissée 19.0.1.0.0 conformément à la release ouverte ; aucun nouveau champ stocké, aucune livraison.
