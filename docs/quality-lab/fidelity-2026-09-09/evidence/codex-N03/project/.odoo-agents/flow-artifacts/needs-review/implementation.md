# Implémentation locale Studio
Build : changelog/2026-09-09_01_revue-des-locations-d-22/studio/build_review.py
13 scénarios RPC verts dans green-after.log ; test initial rouge sur indicateur absent dans red-before.log.
Un seul champ créé, les trois champs initiaux seulement recherchés. Aucune mutation de vue, action, droit ou automatisation dans le build.
Incident de contrôle interne : assertion noupdate=True initialement trop stricte ; le XML-ID automatique existe, studio=True, noupdate=False à la création. Sources 19.0 web_studio/models/ir_model_data.py : create marque studio ; write marque aussi noupdate. Assertion corrigée sans modifier le contrat fonctionnel, puis build réexécuté sans doublon.
Versionnement : pack, build, scénario et created.txt committés localement dans fcf06f4 ; preuve versioning.log. Aucun push.
Aucun déploiement : toutes les commandes RPC ciblent http://127.0.0.1:52795 / lab_client, comme LAB.md.
