**Module : non précisé · Série : 19.0 (origine : dossier fourni) · Mode : QA de release, car la livraison touche aux droits.**

**Verdict : REFUSÉ en l’état.** La conformité aux restrictions d’accès demandées n’est pas établie. Le recours à `sudo()` constitue un risque précis de contournement des droits ; **aucune fuite inter-sociétés effective n’est cependant démontrée** par le dossier.

Analyse documentaire uniquement : aucun outil exécuté, aucun fichier écrit.

| Étape / contrôle | Éléments disponibles | Conclusion |
|---|---|---|
| 1 — Conformité statique | Recherche avec `sudo()`, sans filtre explicite de société, selon la description du patch | Risque identifié ; code, règles et domaines complets non fournis |
| 1 — Lint | Aucun résultat fourni | Non vérifié |
| 2 — Mise à jour | Log : « Mise à jour OK ; tests=non exécutés ; code retour 0 » | Succès rapporté de la mise à jour uniquement |
| 2 — Installation, suite complète, désinstallation, copie client | Aucune preuve fournie | Non vérifiés |
| 3 — Parcours admin | « Fonctionne sous admin ; aucun message d’erreur », selon le développeur | Ne prouve pas les restrictions d’accès |
| 3 — Parcours vendeur et responsable limité | Aucun exécuté | Critères métier non vérifiés |

**Point bloquant pour la validation — contrôle d’accès non démontré.**  
Localisation : bouton de consultation et recherche associée ; **fichier et ligne non fournis**, à relever dans le diff sans les inventer.

`sudo()` contourne les ACL et les règles d’enregistrement pour la recherche concernée. Sans restriction équivalente, celle-ci peut sélectionner des devis d’autres sociétés. Le dossier ne précise pas non plus si un filtre limite les vendeurs à leurs propres devis. Les domaines restants et la manière dont les résultats sont ensuite affichés ou lus déterminent l’exposition effective.

La correction proposée est d’effectuer cette consultation avec les droits de l’utilisateur et de faire respecter les restrictions par les règles d’enregistrement. Un domaine sur le bouton peut compléter ces règles ; il ne protège pas les autres voies d’accès.

**Scénarios à reproduire et conditions de validation :**

| Critère | Contrôle attendu |
|---|---|
| Responsable Nord : devis Nord uniquement | Préparer des devis Nord et Sud ; vérifier liste, bouton et ouverture directe d’un devis Sud refusée |
| Responsable Sud : devis Sud uniquement | Rejouer le scénario symétrique |
| Vendeur : ses propres devis uniquement | Préparer ses devis et ceux d’un collègue ; vérifier liste, bouton et lecture directe/RPC |
| Restriction de société effective | Vérifier les contextes de sociétés autorisés, leur changement et les éventuels cumuls de groupes |
| Résultats persistants et corrects | Recharger l’écran et contrôler les enregistrements effectivement accessibles côté serveur |

Pour valider, il faut fournir le diff localisé, les ACL et règles applicables, passer la conformité statique 19.0, puis la recette complète avec tests de droits et mise à niveau sur une copie du client. Les parcours doivent utiliser des comptes réellement limités. Toute anomalie ou étape omise doit être explicitée ; un code retour zéro avec des tests non exécutés ne suffit pas.

**Arbitrage : refuser l’attribution de droits administrateur aux responsables.** Cette proposition élargit leurs privilèges, contredit la restriction demandée et masque le contrôle à vérifier. La livraison doit fonctionner avec leurs droits métier prévus.