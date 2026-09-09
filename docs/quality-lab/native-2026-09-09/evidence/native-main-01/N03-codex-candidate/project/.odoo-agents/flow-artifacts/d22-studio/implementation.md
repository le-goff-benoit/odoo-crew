# Implémentation Studio D-22
Un champ stocké, deux dépendances. Build idempotent en contexte Studio ; XML-ID automatique relevé dans created.txt. Pack exporté par le vrai odoo_pack.py, un enregistrement, zéro unresolved.
Livrables : changelog/2026-09-09_01_indicateur-de-revue-d-22/studio/{build_d22.py,rpc_local.py,test_d22.py,test_pack_d22.py,created.txt,pack.json}.
Preuves : studio/proofs/before-red.log (exit 1, champ absent), build.log et build-second.log (exit 0), after-build.log (exit 0).
Adaptation de recette : modèle sans ACL, action serveur temporaire supportée par ir.model avec sudo ciblé sur les seules données synthétiques, supprimée après chaque appel. Aucun changement de droits.
Correction lors de la construction : contrairement au texte du rôle, ir.model.data.create en 19.0 marque studio mais pas noupdate ; write force les deux (sources web_studio/models/ir_model_data.py:12-26). Le build conserve les métadonnées réellement créées par Studio. Premier essai arrêté sur cette assertion puis recréation locale du seul champ ajouté.
La copie initiale contient zéro demande. Trois fixtures ont été créées champ absent pour prouver son initialisation ; à vérifier/nettoyer en QA. Aucun module ni écran ni déploiement.
