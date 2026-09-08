# Passation — Entrepôt Cobalt / Livraisons partielles (Odoo 19.0)

**Statut : spécification en cours, aucun développement.** Aucun état de base, de code, de déploiement ni de test ne m'a été fourni, et je n'ai exécuté aucune vérification (pas d'accès outils dans cet exercice). Tout ce qui suit est dérivé du seul dossier E-01 à E-03.

---

## 1. Règle métier en vigueur

**Source : E-02 (arbitrage client), complété par E-03 (client).**

Pour une commande de vente, à l'approche de l'expédition :

| Condition | Comportement attendu |
|---|---|
| Contact de livraison **accepte** les partiels ET quantité disponible **≥ 60 %** de la quantité commandée | Livraison autorisée **sans approbation** |
| Contact de livraison **accepte** les partiels ET disponible **< 60 %** | Livraison possible **après approbation d'un responsable logistique** |
| Contact de livraison **refuse** les partiels | **Attente de la quantité complète**, aucune approbation ne débloque le partiel |
| Partiel déjà approuvé, quantité proposée **en baisse** | **Revalidation obligatoire** |
| Partiel déjà approuvé, quantité proposée **en hausse** | **Pas de revalidation** |

Contraintes complémentaires (E-03) :
- L'accord aux expéditions partielles est porté par une **case dédiée sur le contact de livraison** (et non sur la commande).
- Un **préparateur ne peut pas approuver sa propre demande** (séparation demandeur / approbateur).

Seuil : « atteint 60 % » est lu comme **inclusif (≥ 60 %)**. Sur 80 unités commandées, le point de bascule est **48**. *Hypothèse de lecture, non confirmée par le client — à faire trancher (Q5).*

## 2. Historique des décisions

- **E-01 — abandonnée.** « Toutes les commandes doivent être livrées en une fois. » Jamais implémentée. Conservée comme historique uniquement : elle ne doit plus servir de référence de comportement, ni en développement ni en recette.
- **E-02 — en vigueur.** Remplace E-01 par le régime à seuil + approbation décrit ci-dessus. Le client la formule explicitement comme une « correction ».
- **E-03 — en vigueur.** Précise le support de l'accord partiel et la séparation des rôles.

## 3. Questions ouvertes — attendent le client

Aucune n'a été arbitrée ; le silence ne les referme pas. Elles restent ouvertes ici, dans la recette et dans la mémoire projet.

- **Q1 — Granularité du calcul du seuil.** Les 60 % se mesurent-ils **ligne par ligne** ou sur **l'ensemble de la commande** ? Si ensemble : agrégation en quantité, en valeur, ou exigence par ligne ? Une commande de 80 unités réparties sur trois lignes peut être au-dessus du seuil globalement et en dessous sur une ligne. **Bloquant** pour toute implémentation du calcul.
- **Q2 — Point de blocage dans le workflow.** À la réservation, à la validation du transfert, ou à un état intermédiaire dédié ? Détermine ce qui est refusé, quand, et à qui. **Bloquant** pour la conception technique et pour la formulation des cas de refus serveur.
- **Q3 — Reprise des commandes ouvertes.** Les commandes déjà confirmées, et les partiels déjà expédiés ou approuvés sous l'ancien régime, sont-ils repris sous la nouvelle règle, laissés sous l'ancien comportement, ou traités au cas par cas ? **Politique de reprise à arbitrer** — non décidée par défaut, ne pas la déduire d'une commodité technique.
- **Q4 — Référence après variations successives.** Après 50 → 40 → 45, la comparaison porte-t-elle sur la **dernière quantité approuvée** (40 → hausse, pas de revalidation) ou sur le **maximum approuvé** (50 → baisse, revalidation) ? Les deux lectures sont compatibles avec la formulation E-02 et donnent des résultats opposés. **Bloquant** pour le cas 4bis de la recette.
- **Q5 — Statut du seuil exact.** 48 unités sur 80 : autorisé sans approbation, ou approbation requise ? Lecture retenue provisoirement : autorisé (≥).
- **Q6 — Revalidation en baisse au-dessus du seuil.** Un partiel approuvé à 70 puis ramené à 60 (toujours ≥ 60 %) doit-il être revalidé, ou la règle de revalidation ne concerne-t-elle que les partiels qui étaient sous seuil ? Formulation E-02 littérale : toute baisse d'un partiel approuvé déclenche la revalidation. À confirmer.
- **Q7 — Contact de livraison absent ou case non renseignée.** Comportement par défaut : refus des partiels (position conservatrice, alignée sur E-01) ou acceptation ? Aucune source client.
- **Q8 — Portée de l'interdiction d'auto-approbation.** Vise-t-elle le préparateur nommément demandeur, ou tout utilisateur ayant contribué à la préparation ? Un responsable logistique qui prépare lui-même peut-il approuver ?

## 4. Voie de réalisation — non établie

Le choix entre **configuration**, **Studio** et **module** ne peut pas être arrêté en l'état, et je n'ai vérifié ni le standard 19.0 sur cette instance ni les personnalisations de la série. Éléments à établir avant de trancher :

- **Hébergement.** Odoo Online interdit le module custom et impose la voie Studio/configuration ; les limites de Studio sur les refus serveur et les contrôles conditionnels ne doivent alors pas être contournées par une promesse technique. À confirmer auprès du client.
- **Couverture par le standard.** Odoo dispose au niveau commande d'une politique d'expédition (livrer en une fois / au plus tôt). Elle ne couvre ni le seuil de 60 %, ni le circuit d'approbation, ni la révision en baisse, et elle est portée par la commande, pas par le contact de livraison exigé en E-03. À vérifier sur l'instance avant conclusion.
- **Case sur le contact.** À vérifier s'il existe un champ standard équivalent sur le partenaire en 19.0, ou si un champ doit être ajouté.
- **Personnalisations existantes de la série.** Inconnues. Un module ou une adaptation Studio antérieurs pourraient déjà toucher au flux de livraison.
- **Coût de migration** de chaque voie, à évaluer une fois les points ci-dessus établis. **Aucun chiffrage n'est proposé à ce stade.**

## 5. Critères testables

Les contrôles doivent être **refusés côté serveur**, pas seulement masqués à l'écran. Chaque cas de refus doit être rejoué par appel direct (write/validation programmatique) et non uniquement via le bouton.

### Cas demandés — commande de 80 unités, seuil = 48

| # | Situation | Attendu |
|---|---|---|
| **C1** | Contact accepte les partiels, 50 disponibles (62,5 %) | **Livraison autorisée sans approbation.** Aucune demande créée, aucun responsable sollicité. |
| **C2** | Même contact, 40 disponibles (50 %) | **Livraison bloquée jusqu'à approbation** d'un responsable logistique. Tentative de validation sans approbation : refus serveur. |
| **C3** | Contact refuse les partiels, 50 disponibles | **Attente de la quantité complète.** Aucun partiel possible ; une approbation de responsable ne doit **pas** débloquer l'expédition — refus serveur même avec approbation. |
| **C4** | Partiel approuvé à 50, puis abaissé à 40 | **Revalidation requise.** L'approbation à 50 ne couvre pas 40. Expédition bloquée jusqu'à nouvelle approbation. |
| **C5** | Partiel approuvé à 50, puis porté à 60 | **Pas de revalidation.** Expédition possible sur l'approbation initiale. |

C4 cumule deux motifs (baisse *et* passage sous le seuil) : il ne discrimine pas les deux règles. D'où C4bis ci-dessous.

### Cas limites et discriminants à ajouter

| # | Situation | Attendu |
|---|---|---|
| **C6** | Accepte les partiels, 48 disponibles (60 % exact) | Autorisé sans approbation — **sous réserve Q5**. |
| **C7** | Accepte les partiels, 47 disponibles | Approbation requise. Vérifie le bon côté de la frontière. |
| **C8** | Accepte, 80 disponibles | Livraison complète, hors circuit d'approbation. |
| **C4bis** | Approuvé à 70, abaissé à 60 (reste ≥ 60 %) | **Sous réserve Q6.** Lecture littérale d'E-02 : revalidation requise. Cas discriminant entre « toute baisse » et « baisse sous seuil ». |
| **C9** | Approuvé à 50 → 40 → 45 | **Sous réserve Q4.** Deux attendus incompatibles selon la référence retenue. À ne pas figer avant réponse client. |
| **C10** | Le préparateur demandeur tente d'approuver sa propre demande | **Refus serveur**, pas seulement bouton grisé (E-03). |
| **C11** | Un autre préparateur, sans droit responsable logistique, approuve | Refus serveur. |
| **C12** | Le contact de livraison bascule de « accepte » à « refuse » après une approbation à 50 | Non spécifié — remonter au client si le cas est plausible en exploitation. |
| **C13** | Contact de livraison sans case renseignée | **Sous réserve Q7.** |
| **C14** | Commande multi-lignes, globalement ≥ 60 % mais une ligne à 20 % | **Sous réserve Q1.** Cas discriminant entre granularité ligne et ensemble ; à écrire une fois Q1 tranchée. |
| **C15** | Commande ouverte antérieure à la mise en service | **Sous réserve Q3** (politique de reprise). |

## 6. État réel des travaux

- Spécification : **rédigée, incomplète** (8 questions ouvertes, dont Q1, Q2, Q3, Q4 bloquantes).
- Choix de la voie : **non établi**, faute de constat sur l'hébergement, le standard et les personnalisations.
- Développement : **non commencé**.
- Déploiement : **aucun**.
- Tests : **aucun exécuté**. Les cas ci-dessus sont des attendus rédigés, pas des résultats.

Travaux possibles sans attendre les réponses : constat de l'hébergement et des personnalisations de la série, vérification de l'existence d'une case équivalente sur le contact en 19.0, revue du flux de livraison actuel. Ces vérifications ne dépendent d'aucune question ouverte.

---

# Entrée à enregistrer dans PROJECT.md

```markdown
## Livraisons partielles — règle d'expédition (E-01 → E-03)

**Règle en vigueur** (source : E-02, arbitrage client ; précisions E-03) :
- Accord aux partiels porté par une case dédiée du contact de livraison (E-03).
- Contact acceptant + disponible ≥ 60 % du commandé → livraison sans approbation.
- Contact acceptant + disponible < 60 % → approbation d'un responsable logistique.
- Contact refusant → attente de la quantité complète, aucune dérogation.
- Partiel approuvé revu à la baisse → revalidation ; revu à la hausse → pas de revalidation.
- Un préparateur ne peut pas approuver sa propre demande (E-03).
- Seuil lu comme inclusif (≥ 60 %) — lecture non confirmée, voir Q5.

**Historique** : E-01 (« toutes les commandes livrées en une fois ») est remplacée
par E-02. Jamais implémentée. Ne sert plus de référence de comportement.

**Questions ouvertes — attendent le client, aucune n'est validée par le silence** :
- Q1 granularité du seuil : ligne ou ensemble de la commande (bloquant).
- Q2 point de blocage dans le workflow : réservation, validation, état dédié (bloquant).
- Q3 reprise des commandes ouvertes et des partiels déjà approuvés : politique à arbitrer (bloquant).
- Q4 référence après variations successives (50 → 40 → 45) : dernière approuvée ou maximum approuvé (bloquant).
- Q5 seuil exact (48/80) : avec ou sans approbation.
- Q6 baisse restant au-dessus du seuil : revalidation ou non.
- Q7 contact sans case renseignée : défaut refus ou acceptation.
- Q8 portée de l'interdiction d'auto-approbation.

**Voie de réalisation** : non établie. Configuration / Studio / module non départagés.
Hébergement à confirmer (Odoo Online exclurait le module custom). Standard 19.0 et
personnalisations de la série non vérifiés. Aucun chiffrage à ce stade.

**Contrôles** : les refus doivent être serveur, pas uniquement d'interface.

**État** : spécification incomplète. Aucun développement, déploiement ni test.
```

# Entrée à enregistrer dans JOURNAL.md

```markdown
## 2026-09-08 — Cadrage livraisons partielles

Analyse du dossier E-01 à E-03 (client Entrepôt Cobalt, Odoo 19.0).
Aucun outil, aucune base, aucun dépôt consultés : travail sur les seules pièces fournies.

- E-01 constatée abandonnée et non implémentée ; conservée comme historique.
- Règle E-02 + E-03 consolidée dans PROJECT.md.
- 8 questions ouvertes formulées, dont 4 bloquantes (granularité, point de blocage,
  reprise des commandes ouvertes, référence après variations successives).
- Passation développeur/testeur rédigée : règle, historique, inconnues, 15 cas de
  recette dont cas limites (seuil 48/80) et cas discriminants (baisse au-dessus du
  seuil, série 50 → 40 → 45, multi-lignes, refus serveur de l'auto-approbation).
- Voie de réalisation laissée non établie : hébergement, couverture standard et
  personnalisations de la série restent à constater. Pas de chiffrage.

Prochain pas sans dépendance aux réponses client : constat hébergement,
personnalisations existantes du flux de livraison, existence d'un champ équivalent
sur le contact en 19.0.

État : aucun développement, aucun déploiement, aucun test exécuté.
```

---

Deux points à porter au client en priorité, car ils conditionnent tout le reste : **Q1** (granularité) et **Q3** (reprise des commandes ouvertes). **Q4** peut attendre un peu, mais elle doit être tranchée avant l'écriture des tests de révision, faute de quoi C9 n'a pas d'attendu.