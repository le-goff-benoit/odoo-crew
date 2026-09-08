Passation pour **Atelier Boréal — Odoo 19.0**, fondée uniquement sur le dossier fourni. Aucun fichier, paramétrage, développement, test ou déploiement n’a été réalisé dans cet exercice.

**Règle actuelle et sources**

L’objectif métier est d’encadrer les remises accordées par les commerciaux et de soumettre les dépassements à une approbation indépendante.

- **Client partenaire :** le commercial peut accorder jusqu’à **15 % inclus** sans approbation liée au dépassement du plafond — M-02.
- **Autre client :** le plafond reste à **10 % inclus** — M-02.
- Le statut partenaire correspond à la case **« partenaire commercial » du contact de facturation du devis** — M-03. Il ne faut pas le déduire d’un autre contact.
- Au-delà du plafond applicable, **l’approbation du directeur est obligatoire** — M-02.
- **Un vendeur ne peut pas approuver sa propre demande**, y compris s’il dispose également de droits de directeur — M-03.
- Pour un devis déjà approuvé, **toute augmentation de remise impose une revalidation ; une diminution n’en impose pas** — M-02. Cette règle ne comporte aucune exception liée au plafond.

D-01, qui fixait un plafond uniforme de 10 %, est **remplacée par M-02, précisée par M-03**. Elle reste conservée comme historique et n’avait pas été développée. Le plafond de 10 % demeure applicable aux non-partenaires.

**Exemples à transmettre au développeur et au testeur**

Pour les trois premières lignes, on considère un devis sans approbation antérieure à revalider.

| Situation | Résultat attendu |
|---|---|
| Partenaire à 12 % | Pas d’approbation requise au titre du plafond de 15 %. |
| Non-partenaire à 12 % | Approbation du directeur requise. |
| Partenaire à 16 % | Approbation du directeur requise. |
| Devis approuvé à 16 %, puis porté à 17 % | Revalidation obligatoire ; l’approbation précédente ne suffit plus. |
| Devis approuvé à 16 %, puis ramené à 14 % | Aucune revalidation exigée du seul fait de cette diminution. Cela vaut aussi pour un non-partenaire, malgré le dépassement persistant de son plafond de 10 %. |

**Questions ouvertes et portée du blocage**

Les décisions ci-dessus sont acquises. Les points suivants ne doivent pas être résolus implicitement par le développeur :

1. **Mesure de la remise :** s’agit-il d’une remise par ligne, d’une remise globale ou d’un taux effectif calculé sur le devis ? Comment traiter les lignes à taux différents et les arrondis ? Cette réponse bloque la définition du calcul et sa recette chiffrée.
2. **Point de contrôle :** quelle opération doit être empêchée tant que l’approbation ou la revalidation manque : envoi, confirmation ou autre étape ? Peut-on enregistrer un brouillon au-dessus du plafond ? Cela bloque le comportement exact du circuit.
3. **Droits et identité :** quels utilisateurs constituent les directeurs habilités ? Pour l’interdiction d’auto-approbation, « sa propre demande » désigne-t-il le demandeur, le commercial affecté au devis, ou les deux ? Cela bloque la matrice complète des droits, sans remettre en cause l’interdiction.
4. **Évolutions après approbation :** si la remise passe de 16 % approuvés à 14 %, puis remonte à 15 %, cette remontée impose-t-elle une revalidation ? Le traitement d’une diminution est établi ; la référence à utiliser lors d’une remontée successive reste à préciser. De même, quel effet donner à un changement de contact de facturation ou de sa case partenaire ?
5. **Données existantes :** quelle politique appliquer aux devis déjà présents lors de la mise en service ? Aucun statut d’approbation ne doit leur être attribué par supposition.

Ces questions restent ouvertes dans la spécification et la recette. Les cas indépendants de leurs réponses peuvent déjà être préparés.

**Orientation technique à établir**

Le dossier ne prouve ni la couverture du standard Odoo 19.0, ni les personnalisations existantes, ni le mode d’hébergement. **Aucun verdict ni choix entre configuration, Studio et module n’est donc établi.**

Les vérifications devront porter sur le calcul des remises, le contact de facturation, les approbations disponibles, les droits côté serveur et la gestion des modifications après approbation.

| Voie à examiner | Condition de pertinence | Migration |
|---|---|---|
| Configuration standard | Couverture démontrée de toutes les règles | Généralement moins de maintenance spécifique, avec recette à chaque migration |
| Studio | Capacités démontrées pour le circuit et les refus côté serveur | Dépendance aux personnalisations et à leur compatibilité |
| Module spécifique | Besoin non couvert et hébergement compatible | Maintenance et adaptation du code à prévoir |

**Odoo Online exclut le module custom.** Studio ne peut pas être retenu sur une simple promesse de contournement de ses limites. Aucun chiffrage ferme n’est possible sur ce dossier.

**Critères d’acceptation**

Les critères suivants sont définis mais **non exécutés** :

- Le plafond découle exclusivement de la case du contact de facturation. Tester des contacts commercial et de facturation dont les statuts partenaire sont opposés.
- À 15 % pour un partenaire et à 10 % pour un non-partenaire, aucune approbation n’est exigée au titre du dépassement. Au premier taux représentable au-dessus de ces limites, elle l’est ; la précision reste à définir.
- Les cinq exemples du tableau produisent les résultats indiqués.
- Sur un devis déjà approuvé, une augmentation exige une revalidation, même si le nouveau taux reste sous le plafond. Une diminution seule n’en exige pas.
- Un directeur habilité, distinct du vendeur concerné par l’interdiction, peut approuver. Un utilisateur non habilité et un vendeur approuvant sa propre demande sont refusés.
- Les refus d’approbation sont effectifs **côté serveur**, même par appel direct ou par un autre canal disponible ; masquer un bouton ne suffit pas.
- Après une augmentation, l’ancienne approbation ne permet pas de franchir l’étape soumise à validation. **Recette bloquée sur le choix de cette étape.**
- Les essais sur remises multiples, arrondis, identités ambiguës, variations successives, changement de partenaire et reprise des données restent **à compléter après arbitrage**, et non réputés acceptés.

**Entrée PROJECT.md — prête à enregistrer**

Projet : Atelier Boréal — Odoo 19.0  
Sujet : plafonds de remise et approbation des devis.

Règle actuelle : M-02 remplace D-01. Plafond commercial de 15 % inclus pour les partenaires, de 10 % inclus pour les autres ; au-delà, approbation du directeur. Selon M-03, le statut partenaire provient de la case « partenaire commercial » du contact de facturation du devis. Un vendeur ne peut pas approuver sa propre demande. Selon M-02, toute augmentation de remise d’un devis approuvé exige une revalidation ; une diminution n’en exige pas.

Historique : D-01 prévoyait 10 % pour tous les clients ; décision remplacée, jamais développée.

Questions ouvertes : définition et précision de la remise ; étape contrôlée ; habilitations et identité visée par l’auto-approbation ; référence lors de variations successives ; effets des changements de contact ou de statut partenaire ; politique de reprise des données existantes.

Recette définie, non exécutée : seuils inclusifs, dépassements, contact de facturation discriminant, refus serveur et interdiction d’auto-approbation. Cas attendus : partenaire 12 % sans approbation de dépassement ; non-partenaire 12 % et partenaire 16 % avec approbation ; devis approuvé 16 → 17 % à revalider ; 16 → 14 % sans revalidation pour cette diminution. Les cas dépendant des questions ouvertes restent à compléter.

État réel : passation textuelle uniquement. Standard, personnalisations et hébergement non vérifiés ; voie technique non établie. Aucun développement, test ou déploiement effectué.

**Entrée JOURNAL.md — prête à enregistrer**

2026-09-08 — Analyse synthétique sur dossier, sans outils.

Intégration de la correction M-02 et de la précision M-03 dans la règle de référence. D-01 conservée comme décision remplacée et non développée. Préparation de la passation développeur/testeur et des résultats attendus pour les cinq exemples demandés.

Questions maintenues ouvertes dans la spécification, la recette et la mémoire : mesure de remise, étape contrôlée, droits et identité, variations successives, changement de partenaire et reprise des données. Aucun arbitrage implicite. Vérification du standard Odoo 19.0, des personnalisations et de l’hébergement à réaliser avant le choix technique.

Aucun fichier écrit, aucune vérification technique, aucun test ni déploiement réalisé.