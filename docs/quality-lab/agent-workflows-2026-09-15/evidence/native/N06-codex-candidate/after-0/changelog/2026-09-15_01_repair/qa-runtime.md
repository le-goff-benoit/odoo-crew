# QA exécution — Odoo 19.0 — B-42
Réutilisation des preuves fraîches du développeur ; code et tests inchangés depuis le vert.
proofs/red.json/red.log : ancien code, 6 failed, 0 error(s) of 6 tests (17 s). Échecs attendus sur séquences/totaux, sélection vide/mixte, multi-société et AccessError non levées ; pas de simple erreur de chargement.
proofs/green.json/green.log : même classe TestRepair, 0 failed, 0 error(s) of 6 tests, 0 skip (6 s), installation reconnue et update + tests OK. Les stats « 8 tests » incluent des hooks ; le bilan fonctionnel est bien 6 tests.
Couvre tri avec égalité de dates/id, self incomplet et vide, autre société active, lignes annulées/seules/vides, écart 0.005→0.004, issued et autres sociétés préservés, succès utilisateur interne et refus ORM exacts, second appel sans write.
Trois warnings author manquant préexistants. Pas de warning de vue ni erreur runtime. Aucune suite de release, désinstallation ou tour navigateur prétendu.
Verdict de voie : contrôles ciblés verts, limites et dette visibles. Relecture non indépendante.
