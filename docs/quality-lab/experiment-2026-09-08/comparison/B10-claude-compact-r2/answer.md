# Passation — Atelier Boréal (Odoo 19.0) — Règle de remise et approbation

**Statut réel des travaux :** aucune vérification technique n'a été effectuée dans cet exercice (pas de lecture du code, pas d'inspection de base, pas de test, pas de déploiement). Le choix de voie (configuration / Studio / module) n'est **pas établi** : il dépend de vérifications listées plus bas. Aucun chiffrage ferme n'est donné.

---

## 1. Règle actuelle (en vigueur), avec sources

| # | Règle | Source |
|---|---|---|
| R1 | Remise commerciale accordée librement par le commercial jusqu'à **10 %** pour un client **non partenaire**. | M-02 (client) |
| R2 | Remise accordée librement jusqu'à **15 %** pour un client **partenaire**. | M-02 (client) |
| R3 | Au-delà du seuil applicable (10 % ou 15 %), une **approbation du directeur** est requise. | M-02 (client) |
| R4 | Un devis **déjà approuvé** doit être **revalidé** si sa remise **augmente** ; pas de revalidation si elle **diminue**. | M-02 (client) |
| R5 | « Partenaire » = case **« partenaire commercial » cochée sur le contact de facturation du devis**. | M-03 (réponse humaine, décision client sourcée) |
| R6 | Un vendeur **ne peut pas approuver sa propre demande**. | M-03 |

Statut : R1–R6 sont des décisions client sourcées. **Aucune n'est développée à ce jour.**

## 2. Ce qui remplace l'ancienne décision (historique)

- **D-01 (remplacée)** : « remise commerciale maximale de 10 % pour tous les clients ». Jamais développée, donc aucune reprise de code ni de donnée à prévoir de ce fait.
- **Remplacée par** : R1 + R2 + R3 (seuil différencié partenaire / non-partenaire, avec circuit d'approbation) — source M-02, précisée par M-03.
- Ce qui **subsiste** de D-01 : le plafond de 10 % reste exact pour les clients non partenaires. Ce n'est plus un plafond absolu mais un **seuil d'approbation**.
- Conserver D-01 en mémoire comme historique daté, non comme règle active.

## 3. Hypothèses proposées (non validées — le silence ne vaut pas accord)

| # | Hypothèse | Effet si fausse |
|---|---|---|
| H1 | Les seuils sont **inclusifs** : 10,00 % et 15,00 % passent sans approbation ; l'approbation démarre strictement au-dessus. | Décale tous les cas limites. |
| H2 | Le contrôle porte sur la **remise en pourcentage de chaque ligne** du devis ; un devis est « au-dessus du seuil » dès qu'une ligne l'est. | Un contrôle au niveau du devis (moyenne ou remise globale) donnerait d'autres résultats. |
| H3 | Le contrôle est appliqué **côté serveur** (refus à l'écriture), pas seulement par masquage d'écran. | Contournement possible par import, API, duplication. |
| H4 | Un devis « approuvé » désigne un devis ayant obtenu l'**approbation de remise**, indépendamment de l'état standard de la commande. | Change le déclencheur de R4. |
| H5 | Une remise qui **diminue** conserve son approbation, même si elle repasse sous le seuil (l'approbation reste simplement sans objet). | Change le cas 16 % → 14 %. |

## 4. Questions ouvertes

### Bloquantes (restent ouvertes en spécification, recette et mémoire)

- **Q1 — Hébergement.** Odoo **Online** interdit tout module custom et impose la voie configuration/Studio ; Odoo.sh ou on-premise ouvrent la voie module. Tant que l'hébergement n'est pas connu, la voie n'est pas arbitrable et Studio ne doit pas être promis comme couvrant un besoin qu'il ne couvre pas.
- **Q2 — Qui est « le directeur » ?** Un groupe de sécurité dédié, un utilisateur nommé, ou le responsable hiérarchique du vendeur ? Et **plafond absolu** au-dessus duquel même le directeur ne peut pas approuver (ex. 30 %, 100 %) ?
- **Q3 — Champ « partenaire commercial ».** Odoo utilise déjà en standard la notion de *commercial partner* (entité de facturation racine), qui n'a rien à voir. Le champ demandé existe-t-il déjà chez le client (champ personnalisé, catégorie de contact, tarif) ou est-il à créer ? Le libellé doit être levé pour éviter la collision de vocabulaire.
- **Q4 — Politique de reprise des données existantes.** Que faire des devis et commandes **déjà en base** dont la remise dépasse le seuil applicable ? (à laisser tels quels / à marquer « approbation à régulariser » / à bloquer à la prochaine modification). **À arbitrer par le client** ; ne rien décider par défaut.

### Non bloquantes (à trancher, le travail peut avancer)

- **Q5** — Si le directeur est aussi l'auteur du devis, qui approuve ? (R6 crée une impasse dans ce cas.)
- **Q6** — Le contrôle porte-t-il aussi sur une remise obtenue en **baissant le prix unitaire** ou via une remise globale, ou seulement sur le champ remise % ?
- **Q7** — Si le contact de facturation **change après approbation** (partenaire → non partenaire) sans que la remise bouge, faut-il revalider ?
- **Q8** — Case cochée sur une **société parente** mais pas sur le contact de facturation : héritage ou lecture stricte du contact ?
- **Q9** — Sur revalidation, l'approbation précédente est-elle annulée immédiatement (devis rebasculé en « à approuver ») ou reste-t-elle valide jusqu'à la nouvelle décision ?
- **Q10** — Traçabilité attendue : qui a demandé, qui a approuvé, quand, quel taux approuvé ? Notification au directeur ?

## 5. Vérifications à mener avant de choisir la voie

Aucune n'a été faite ; aucun résultat n'est présumé.

1. Hébergement et liste des modules installés / personnalisations existantes sur la série 19.0.
2. Existence et couverture du **standard** : Odoo propose nativement une limite de remise par groupe et un circuit d'approbation sur devis (validation au-delà d'un montant). À confronter au besoin — ces mécanismes ne sont pas conditionnés à un attribut du client.
3. Capacité réelle de **Studio** à porter : seuil dynamique dépendant d'un champ du contact de facturation, refus serveur, interdiction d'auto-approbation.
4. Présence d'un champ « partenaire » exploitable côté contact.
5. Volume et état des devis/commandes existants hors seuil (alimente Q4).
6. Coût de migration de chaque voie (Studio et champs personnalisés se migrent différemment d'un module).

## 6. Traitement des exemples demandés

Sous H1, H2, H4, H5 et sous réserve de Q2/Q3.

| Cas | Résultat attendu |
|---|---|
| **Partenaire, 12 %** | Seuil applicable 15 %. 12 ≤ 15 → **accepté sans approbation**. Le devis reste modifiable par le commercial. |
| **Non-partenaire, 12 %** | Seuil applicable 10 %. 12 > 10 → **approbation directeur requise**. Le devis ne peut pas être confirmé tant que l'approbation n'est pas obtenue ; refus **côté serveur**, pas seulement bouton grisé. |
| **Partenaire, 16 %** | 16 > 15 → **approbation directeur requise**. L'auteur du devis ne peut pas être l'approbateur (R6). |
| **Devis approuvé à 16 %, passage à 17 %** | La remise **augmente** → **revalidation obligatoire** (R4). L'approbation à 16 % ne couvre pas 17 %. Comportement exact pendant l'attente : voir Q9. |
| **Devis approuvé à 16 %, passage à 14 %** | La remise **diminue** → **pas de revalidation** (R4), même si le client est non-partenaire et que 14 % reste au-dessus de son seuil de 10 % : R4 est explicite et prime. Sous H5, l'approbation initiale reste attachée au devis. **À confirmer par le client** (Q : une baisse qui reste au-dessus du seuil conserve-t-elle bien l'approbation ?). |

## 7. Critères d'acceptation (recette)

Chaque critère est observable ; « refusé » signifie refus à l'enregistrement côté serveur, vérifié aussi hors interface (import, API, duplication de devis).

**Seuils**
- CA-01 : non-partenaire, remise 10,00 % → enregistrement et confirmation possibles sans approbation.
- CA-02 : non-partenaire, remise 10,01 % → confirmation refusée sans approbation.
- CA-03 : partenaire, remise 15,00 % → accepté sans approbation.
- CA-04 : partenaire, remise 15,01 % → confirmation refusée sans approbation.
- CA-05 : partenaire, 12 % → accepté (cas d'exemple).
- CA-06 : non-partenaire, 12 % → refusé sans approbation (cas discriminant : même taux, résultat opposé à CA-05).
- CA-07 : partenaire, 16 % → approbation requise.

**Qualification partenaire**
- CA-08 : la case est cochée sur le **contact de facturation** du devis → seuil 15 %.
- CA-09 : case cochée sur le **client** du devis mais pas sur le contact de facturation distinct → seuil 10 % (lecture stricte de R5 ; dépend de Q8).
- CA-10 : décocher la case sur le contact de facturation d'un devis non encore approuvé le fait repasser au seuil 10 %.

**Approbation**
- CA-11 : le vendeur auteur du devis ne peut pas approuver sa propre demande, y compris s'il dispose par ailleurs des droits de directeur — refus **serveur**.
- CA-12 : un utilisateur sans droit d'approbation ne peut pas approuver, ni via l'interface ni via écriture directe sur le champ d'état.
- CA-13 : l'approbation est tracée (approbateur, date, taux approuvé) et consultable.

**Revalidation**
- CA-14 : devis approuvé à 16 %, passage à 17 % → l'approbation ne couvre plus le devis ; confirmation refusée jusqu'à nouvelle approbation.
- CA-15 : devis approuvé à 16 %, passage à 14 % → aucune revalidation demandée ; le devis reste confirmable.
- CA-16 : devis approuvé à 16 %, retour à 16 % après passage à 14 % → aucune revalidation (pas d'augmentation par rapport au taux approuvé) — **à confirmer** : la référence est-elle le taux approuvé ou le taux précédent ?
- CA-17 : devis multi-lignes approuvé, ajout d'une **nouvelle ligne** à 17 % → revalidation requise (dépend de H2).

**Cas limites**
- CA-18 : remise 0 % et remise vide → aucun contrôle déclenché.
- CA-19 : remise négative (majoration) → non bloquée par cette règle.
- CA-20 : remise obtenue par baisse du prix unitaire sans toucher au champ remise → comportement conforme à la réponse de Q6.

**Non testable en l'état :** tout critère dépendant de Q1 (voie technique), Q2 (identité de l'approbateur, plafond absolu) et Q4 (données existantes). Ces trois points restent ouverts en recette.

---

## 8. Entrée PROJECT.md prête à enregistrer

> *Proposition de texte — non écrite dans le dépôt.*

```markdown
## Remises commerciales et approbation (Odoo 19.0)

### Règle en vigueur
- Client **non partenaire** : remise jusqu'à 10 % sans approbation. [M-02]
- Client **partenaire** : remise jusqu'à 15 % sans approbation. [M-02]
- Au-delà du seuil applicable : **approbation du directeur** obligatoire. [M-02]
- **Partenaire** = case « partenaire commercial » cochée sur le **contact de
  facturation du devis**. [M-03]
- Un vendeur **ne peut pas approuver sa propre demande**. [M-03]
- Devis déjà approuvé : **revalidation si la remise augmente**, pas de
  revalidation si elle diminue. [M-02]

### Historique des décisions
- **D-01 (remplacée par M-02)** : remise maximale 10 % pour tous les clients.
  Jamais développée. Le plafond de 10 % reste valable pour les seuls clients
  non partenaires, et devient un seuil d'approbation et non un maximum.

### Hypothèses non validées
- Seuils inclusifs (10,00 % et 15,00 % passent sans approbation).
- Contrôle au niveau de la ligne de commande.
- Contrôle appliqué côté serveur, pas seulement à l'écran.
- « Approuvé » = approbation de remise obtenue.
- Une remise qui diminue conserve son approbation même sous le seuil.

### Questions ouvertes bloquantes
- Q1 Hébergement (Odoo Online interdit le module custom → voie non arbitrable).
- Q2 Définition du « directeur » (groupe ? personne ? hiérarchie ?) et plafond
  absolu d'approbation.
- Q3 Existence et libellé du champ « partenaire commercial » (collision avec la
  notion standard *commercial partner* d'Odoo à lever).
- Q4 Politique de reprise des devis/commandes existants hors seuil — à arbitrer
  par le client, aucune décision par défaut.

### Questions ouvertes non bloquantes
Q5 directeur auteur du devis · Q6 remise par prix unitaire ou remise globale ·
Q7 changement de contact de facturation après approbation · Q8 héritage
société/contact · Q9 état du devis pendant la revalidation · Q10 traçabilité et
notification.

### Voie technique
**Non établie.** Configuration / Studio / module non tranché : dépend de Q1 et
des vérifications du standard 19.0 (limite de remise par groupe, validation de
devis) et des personnalisations existantes. Aucun chiffrage.

### État des travaux
Spécification en cours. **Aucun développement, aucun test, aucun déploiement.**
```

## 9. Entrée JOURNAL.md prête à enregistrer

> *Proposition de texte — non écrite dans le dépôt.*

```markdown
## 2026-09-08 — Remises : D-01 remplacée, cadrage de la règle différenciée

**Entrées.** M-02 (client) : seuils différenciés 10 % / 15 %, approbation
directeur au-delà, revalidation à la hausse uniquement. M-03 (réponse humaine) :
définition de « partenaire » par la case sur le contact de facturation ;
interdiction de l'auto-approbation.

**Décidé.** D-01 (10 % pour tous) est remplacée et conservée en historique.
La règle active devient R1–R6, consignée dans PROJECT.md avec ses sources.

**Produit.** Passation développeur/testeur : règle sourcée, historique,
hypothèses explicites, questions ouvertes séparées en bloquantes et non
bloquantes, 20 critères d'acceptation incluant les cas discriminants
(12 % partenaire accepté vs 12 % non-partenaire refusé) et les cas de
revalidation (16 → 17 revalidé, 16 → 14 non revalidé).

**Non fait / non vérifié.** Aucune lecture du code ou de la base, aucune
inspection des modules installés, aucun test, aucun déploiement. Le verdict
« standard vs Studio vs module » n'est pas établi et aucun chiffrage n'est
donné.

**Ouvert.** Q1 hébergement · Q2 identité du directeur et plafond absolu ·
Q3 champ « partenaire commercial » et collision de vocabulaire avec le
*commercial partner* standard · Q4 reprise des données existantes.
Le silence du client ne vaut validation d'aucune hypothèse.

**Prochain pas.** Poser Q1–Q4 au client ; en parallèle, mener les vérifications
qui n'en dépendent pas (couverture du standard 19.0, personnalisations, présence
d'un champ partenaire, volume des devis hors seuil).
```

---

**Rappel de portée :** ce document est un livrable textuel. Aucun fichier n'a été écrit, aucune base consultée, aucun test exécuté. La voie technique et l'estimation restent à établir après les vérifications de la section 5.