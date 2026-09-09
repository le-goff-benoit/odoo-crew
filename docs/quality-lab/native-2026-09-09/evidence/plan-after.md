# Contre-vérification indépendante

**Verdict : les cinq défauts initiaux sont corrigés dans les scénarios rejoués ; aucun échec des assertions de non-régression ajoutées.**

Exécution réelle : `python3 /tmp/forward-release-plan-auvQFI/after/replay.py`, code retour 0, dernier résultat `ALL REPLAY ASSERTIONS PASSED`. Sorties complètes dans `transcript.txt`. Pour répéter sans écraser les preuves, fournir un nouveau répertoire : `python3 /tmp/forward-release-plan-auvQFI/after/replay.py /tmp/release-plan-replay-nouveau`.

Vérifications :

- Après changement de décision T01 et nouvelle réception T01, T03 reste périmée et T02 reste valide. Une réception explicite T03 rétablit son statut.
- Les réceptions fraîches après préparation des trois versions réussissent dans l'ordre de dépendance sans rouvrir les flows. Assertion d'égalité stricte des listes `attempts` avant/après. Les anciennes réceptions sont présentes dans l'historique.
- Réception T03 avant nouvelle réception de ses parents refusée.
- Voie Studio sur plan module refusée.
- Omission du périmètre T02/T03 lors du sceau refusée.
- Sceau copié vers R02 refusé ; suppression ou modification du plan après sceau refusée ; document métier modifié après sceau refusé.
- Cas cohérent scellé, fermé puis vérifié sans DOCX/PDF. Restauration des fichiers exacts rétablit le check.
- Dépendances initiales et reprise après disparition d'un flow fonctionnent toujours.

Limites inchangées : projet totalement synthétique, états de flow `complete` injectés comme doublures, aucun serveur ou test Odoo réel. Le cas positif de clôture emploie un log explicitement marqué `SYNTHETIC PARSER FIXTURE - NOT ODOO`, afin de tester le contrat du garde. Ces preuves n'attestent donc aucune qualité métier ou recette client. Le garde ne remplace pas la relecture de ce que la commande a réellement testé, notamment par module dans une release à plusieurs modules. Aucun dépôt, profil actif ou client modifié.

Les preuves avant correction restent dans le dossier parent (`findings.md`, `transcript.txt`, `closure-transcript.txt`), sans réécriture.
