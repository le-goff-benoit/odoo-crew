# Implémentation Studio D-22

Livrables : `changelog/2026-09-09_01_indicateur-de-revue-d-22/studio/`.
Un champ calculé stocké créé en contexte Studio ; XML-ID natif relevé dans `created.txt`.
Pack exporté par le vrai `odoo_pack.py` : un seul enregistrement `ir.model.fields`, modèle initial référencé par XML-ID, aucun unresolved.
Scénario avant ajout : rouge attendu (`proofs/red-before.log`). Après ajout : 33 contrôles RPC verts (`proofs/green-build.json`).
Préparation du banc : accès administrateur temporaire, nettoyé ; invalidation complète du cache via le pont car la suppression/insertion d'ACL invalide seulement `stable` dans les sources disponibles.
L'XML-ID natif est créé avec studio=True mais noupdate=False ; le script le protège via write en contexte Studio, sans création ni renommage d'identifiant.
La QA doit encore exécuter `verify_pack.py --from-absent`, vérifier deux applications, absence de doublon et invariants.
