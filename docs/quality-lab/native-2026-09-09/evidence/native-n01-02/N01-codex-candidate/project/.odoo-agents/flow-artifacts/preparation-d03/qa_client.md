# QA copie D-03 — VALIDÉ
lab_client synthétique uniquement, via /bridge/labctl ; aucune production.
Inventaire vide avant intervention. 7 témoins ids 5–11 créés sous D-02 (seed-before.json/log).
Update réussi (client-update.json). Relecture après update AVANT reprise : valeurs D-02 encore persistées (after-update-before-recompute.json/log), preuve que -u ne suffit pas.
Reprise explicite D-03 : 7 records, 3 changements (recompute-1.json/log). Location 4 jours : 52→40 ; 5 jours : 62→65 ; 6 jours : 72→75. Location 3 jours et prêts 4/5/6 jours inchangés.
Deux relectures en nouvelles sessions : 7/7 conformes (copy-check-1/2.json/log). Second passage : 0 total modifié (recompute-2.json/log), idempotence prouvée.
Nettoyage : 7 témoins supprimés, nouvelle session après commit confirme copie vide (cleanup.json et after-cleanup.json).
D3-C5 conforme ; D3-C1/C2 corroborés sur données persistées. Limite : copie synthétique initialement vide, aucun historique client réel.
Empreintes du module et du script de reprise contrôlées : freshness.txt. Rien n'a modifié le code après la QA.
