# Réception documentaire de A

Critère : Décision A : afficher la référence dossier dans la fiche interne.

La demande A borne expressément le contrôle à la cohérence documentaire. Le contrat spec.md reprend exactement cette décision. Le fichier documentary/reference.txt contient le marqueur reference_dossier=visible ; la preuve initiale et le contrôle documentaire rejoué dans plan-proof-v2.json l’attestent. Aucun développement ni test Odoo exécuté, aucun comportement d’interface Odoo reçu.

La réception indépendante renouvelée est dans review.json et sa trace native dans delegation.md. La publication est attestée séparément dans publication.md après exécution du publieur. La présente pièce ne suffit pas seule à attester ces étapes : leurs preuves doivent être présentes et positives avant finish.

Une première commande de contrôle a échoué car elle attendait les caractères littéraux antislash-n au lieu du saut de ligne réel ; cette erreur de transcription est conservée dans plan-proof.json. La commande corrigée vérifie le saut de ligne sans modifier le fichier documentaire.
