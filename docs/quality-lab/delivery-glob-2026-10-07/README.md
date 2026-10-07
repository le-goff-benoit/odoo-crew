# Motifs récursifs d'assets — correctif local du contrôle de livraison

Référence d'outillage : d4c5d6dabc1e29769b84f7f334466881de76d71b ; copie exacte du contrôleur avant changement dans reference_delivery_guard.py. Aucun rôle, modèle ni critère de livraison modifié. Les modifications préexistantes d'autres outils sont préservées.

Défaut : fnmatch sur un chemin complet impose au moins un sous-répertoire pour **/* et laisse * traverser les séparateurs. Odoo19 utilise glob(pattern, recursive=True) dans ir_asset._glob_static_file : ** admet zéro répertoire, * reste dans un segment. Les fichiers réels au premier niveau sont donc faussement déclarés absents.

Référence synthétique figée : trois tests et une matrice de48 sous-cas comparée au glob standard indépendant, dont cas réservés avec profondeurs multiples, ?, classes de caractères, fichiers/répertoires cachés et motif absent. Rouge conservé :9 échecs, dont le cas **/* à profondeur zéro et des faux positifs du séparateur/caché.

Correction : asset_glob_matches dans scripts/odoo_delivery_guard.py compare les segments Git avec ** récursif, sans lire le checkout. Le contrôle reste fondé sur le commit exact et ne reçoit aucune exception par module. Les absences véritables sont toujours refusées ; aucun ajout de fichier factice ni modification d'asset déclaré dans le produit.

Vert ciblé :24 tests réussis (globs, livraison et contrôleur), matrice réservée comprise. Build isolé :425 tests, aucun échec,1 skip du parseur TOML standard (Python3.10, nécessite3.11) ; parité35 fichiers et2 blocs conforme. Résultats consignés dans build.log/parite.log. Adoption locale de l'outil après ces contrôles ; aucune publication du dispositif partagé autorisée ou effectuée. Les profils ne changent pas ; le CLI actif lit directement la source corrigée. Aucune campagne LLM ni capacité Odoo générale évaluée.
