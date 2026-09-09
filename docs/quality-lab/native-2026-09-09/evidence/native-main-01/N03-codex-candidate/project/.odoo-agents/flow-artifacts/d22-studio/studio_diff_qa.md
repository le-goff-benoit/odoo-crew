# QA diff Studio — PASS
Odoo 19.0, copie lab_client. `odoo_pack.py diff <release>/studio/pack.json --db lab_client --url http://127.0.0.1:49635` exécuté : zéro création, zéro mise à jour, un objet identique ; preuve studio/proofs/qa-diff.log.
Relecture du pack : un seul ir.model.fields, x_studio_needs_review boolean/store=True, depends sur les deux champs existants, calcul D-22 exact, assignation sur tous les records. XML-ID auto Studio et référence modèle lab_seed_model ; aucun unresolved, vue, ACL, action ou automatisation dans le pack.
Pas de lint ni de test de module : voie Studio. Références de la revue concordantes avec ir_model.make_compute 19.0. C1/C5 partie statique couverts ; idempotence et scénarios restent à exécuter dans la voie runtime.
