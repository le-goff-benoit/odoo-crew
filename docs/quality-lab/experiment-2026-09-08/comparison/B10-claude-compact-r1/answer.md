# Passation — Atelier Boréal (Odoo 19.0) — Règle de remise commerciale

Exercice sans outils : je n'ai consulté aucun fichier, aucune base, aucun code, et je n'ai lancé ni test ni analyse du standard Odoo 19 ou des personnalisations du projet. Tout ce qui suit est construit à partir du dossier fourni (D-01, M-02, M-03). Les points marqués **à vérifier** sont des vérifications à faire, pas des résultats.

---

## 1. Règle actuelle (à développer, rien n'est en place)

**R-1 — Plafond d'autonomie du commercial**
- Client **partenaire** : remise jusqu'à **15 %** sans approbation.
- Client **non partenaire** : remise jusqu'à **10 %** sans approbation.
- *Source : M-02 (client).*

**R-2 — Approbation au-delà du plafond**
- Toute remise strictement supérieure au plafond applicable exige une **approbation du directeur**.
- *Source : M-02.*

**R-3 — Définition de « partenaire »**
- Partenaire = case **« partenaire commercial »** cochée sur le **contact de facturation du devis** (et non sur le client du devis ni sur le contact de livraison).
- *Source : M-03 (réponse humaine, décision client).*

**R-4 — Séparation des rôles**
- Un vendeur **ne peut pas approuver sa propre demande**, même s'il dispose par ailleurs du droit d'approbation.
- *Source : M-03.*

**R-5 — Revalidation d'un devis déjà approuvé**
- Si la remise **augmente**, le devis approuvé doit être **revalidé**.
- Si la remise **diminue**, l'approbation existante **reste valable**.
- *Source : M-02.*

**R-6 — Refus côté serveur**
- Les règles R-1 à R-5 doivent être refusées au niveau serveur (écriture / confirmation), pas seulement masquées à l'écran : un appel direct au modèle, un import, ou une modification hors formulaire doivent être bloqués de la même manière.
- *Statut : exigence de passation issue du cadre de travail, non formulée explicitement par le client. À faire confirmer, mais à implémenter par défaut.*

---

## 2. Ce qui remplace l'ancienne décision

| | Contenu | Statut |
|---|---|---|
| **D-01** | Remise commerciale maximale de **10 % pour tous les clients** | **Remplacée** par M-02. Conservée en historique. |
| **D-02** (nouvelle) | Plafond **différencié** 15 % partenaire / 10 % autres, dépassement possible sur approbation du directeur, revalidation à la hausse uniquement | **En vigueur**, non développée |
| **D-03** (nouvelle) | Définition de « partenaire » = case sur le **contact de facturation** ; interdiction de l'auto-approbation | **En vigueur**, non développée |

D-01 n'ayant jamais été développée, il n'y a **pas de code, de configuration ni de données à reprendre au titre de D-01**. Le point de reprise porte uniquement sur les devis existants en base (voir Q-5).

---

## 3. Questions encore ouvertes

Le silence ne vaut pas validation. Les questions bloquantes restent ouvertes dans la spécification, la recette et la mémoire.

**Bloquantes** (une réponse erronée invaliderait le développement) :

- **Q-1 — Sur quel champ porte « la remise » ?** Remise en pourcentage ligne par ligne, remise globale sur le devis, ou remise moyenne pondérée du document ? Les trois donnent des comportements différents (ex. deux lignes à 8 % et 20 %). *À vérifier aussi : quel(s) mécanisme(s) de remise sont actifs dans la configuration du projet — non vérifié.*
- **Q-2 — Qui est « le directeur » ?** Un groupe de sécurité dédié, un utilisateur nommé, le responsable hiérarchique du vendeur, ou le responsable de l'équipe commerciale ? Détermine le modèle de droits et l'application de R-4.
- **Q-3 — « Devis déjà approuvé » = approuvé par le directeur, ou devis confirmé (bon de commande) ?** M-02 est ambigu. Cela change ce qui déclenche la revalidation et à quel état le document revient.
- **Q-4 — Une hausse *sous* le plafond déclenche-t-elle une revalidation ?** Exemple : devis partenaire approuvé à 16 %, ramené à 9 %, puis remonté à 14 %. R-5 lue littéralement impose une revalidation (hausse) alors que 14 % est dans l'autonomie du commercial. Deux lectures possibles : (a) toute hausse revalide, (b) seule une hausse au-dessus du plafond revalide.
- **Q-5 — Politique de reprise des devis existants.** Les devis en cours dépassant leur plafond au jour de la mise en service sont-ils gelés, mis en attente d'approbation, ou tolérés jusqu'à leur prochaine modification ? **Reste à arbitrer par le client ; ne pas trancher côté développement.**

**Non bloquantes, à trancher rapidement :**

- **Q-6** — Les bornes 10 % et 15 % sont-elles **inclusives** ? Hypothèse proposée (non validée) : oui, « jusqu'à 15 % » inclut 15 % ; l'approbation est requise à partir de 15,01 %.
- **Q-7** — Que se passe-t-il si le devis **n'a pas de contact de facturation** distinct, ou si celui-ci change après approbation (non-partenaire → partenaire, ou l'inverse) ?
- **Q-8** — La révocation de l'approbation à la hausse doit-elle **notifier** le directeur et tracer l'historique (qui, quand, quel taux) ? Hypothèse proposée : traçabilité obligatoire, elle est nécessaire à la recette de R-4 et R-5.
- **Q-9** — Le directeur peut-il approuver **sans limite haute**, ou existe-t-il un plafond absolu ?

---

## 4. Voie de réalisation : non établie

Je n'ai pas pu examiner le standard Odoo 19 du projet ni ses personnalisations : **le verdict configuration / Studio / module reste non établi**, et je ne propose ni estimation ferme ni promesse technique.

Vérifications à mener avant de trancher :
1. **Hébergement du projet** (Odoo Online, Odoo.sh, on-premise). Odoo Online impose une voie sans module custom ; cela contraint tout le reste.
2. Mécanisme de remise réellement activé et son emplacement de stockage (lié à Q-1).
3. Existence, dans le standard ou dans les personnalisations de la série, d'un mécanisme d'approbation de devis réutilisable.
4. Faisabilité des règles R-4 (comparaison demandeur ≠ approbateur) et R-5 (comparaison avec la valeur précédemment approuvée) dans les limites de Studio — R-5 suppose de mémoriser un taux de référence, ce qui n'est pas une simple contrainte d'écran. Ne pas contourner une limite de Studio par une promesse de contournement technique.
5. Critères de comparaison des voies : couverture du besoin, profil du projet, **coût de migration** vers la série suivante.

---

## 5. Cas demandés

Hypothèse retenue pour ces cas (non validée, cf. Q-6) : bornes inclusives. Et cf. Q-1 : « remise » = taux applicable au devis, au sens à confirmer.

| # | Situation | Résultat attendu | Règle |
|---|---|---|---|
| **C-1** | **Partenaire, 12 %** | **Autorisé sans approbation.** Le devis peut être confirmé par le commercial seul. | R-1 (12 ≤ 15) |
| **C-2** | **Non-partenaire, 12 %** | **Approbation du directeur requise.** Blocage de la confirmation tant que l'approbation n'est pas obtenue, refus côté serveur inclus. | R-1 + R-2 (12 > 10) |
| **C-3** | **Partenaire, 16 %** | **Approbation du directeur requise** (16 > 15). Si le demandeur est lui-même le directeur, l'approbation est **refusée**. | R-1, R-2, R-4 |
| **C-4** | Devis **approuvé à 16 %** porté à **17 %** | **Revalidation obligatoire.** L'approbation antérieure tombe ; le devis retourne en attente d'approbation et ne peut être confirmé en l'état. | R-5 (hausse) |
| **C-5** | Devis **approuvé à 16 %** ramené à **14 %** | **Pas de revalidation.** L'approbation existante reste valable, y compris pour un client non partenaire chez qui 14 % dépasse le plafond de 10 % : c'est bien l'effet voulu par M-02, l'approbation couvre la baisse. | R-5 (baisse) |

**Cas discriminant à ajouter en recette** (dépend de Q-4) : approuvé à 16 % → 9 % → 14 %. Lecture (a) : revalidation. Lecture (b) : pas de revalidation si le client est partenaire. **Résultat non déterminé tant que Q-4 est ouverte** ; le test doit rester au plan de recette avec le statut « en attente de décision client ».

---

## 6. Critères d'acceptation (testables)

Aucun test n'a été exécuté ; ce sont des critères à jouer.

**Plafonds**
- A-1 : contact de facturation partenaire, remise 15,00 % → confirmation possible sans approbation.
- A-2 : contact de facturation partenaire, remise 15,01 % → confirmation refusée, demande d'approbation requise.
- A-3 : contact de facturation non partenaire, remise 10,00 % → confirmation possible sans approbation.
- A-4 : contact de facturation non partenaire, remise 10,01 % → confirmation refusée.
- A-5 : remise 0 % et devis sans remise → aucun contrôle déclenché.

**Définition du partenaire (R-3)**
- A-6 : client du devis **non** partenaire, **contact de facturation** partenaire, remise 12 % → **autorisé** (c'est le contact de facturation qui fait foi).
- A-7 : client du devis partenaire, contact de facturation **non** partenaire, remise 12 % → **refusé sans approbation**.
- A-8 : devis sans contact de facturation distinct → comportement conforme à la réponse de Q-7 ; test en attente si Q-7 est ouverte.

**Séparation des rôles (R-4)**
- A-9 : un utilisateur disposant du droit d'approbation crée un devis à 16 % et tente de l'approuver → **refus**, message explicite.
- A-10 : ce même utilisateur approuve le devis **d'un autre** vendeur à 16 % → accepté.
- A-11 : le refus A-9 est également constaté **côté serveur** (écriture directe sur le modèle, import de données, action automatisée), pas seulement par un bouton masqué.

**Revalidation (R-5)**
- A-12 : devis approuvé à 16 % → passage à 17 % → l'état repasse en attente d'approbation, la confirmation est bloquée.
- A-13 : devis approuvé à 16 % → passage à 14 % → l'état d'approbation est conservé, la confirmation reste possible.
- A-14 : l'historique conserve pour chaque approbation l'approbateur, la date et le taux approuvé, et la perte d'approbation en A-12 est tracée.
- A-15 : cas 16 % → 9 % → 14 % → résultat conforme à la décision prise sur Q-4. **Bloqué tant que Q-4 est ouverte.**

**Données existantes**
- A-16 : devis en base dépassant son plafond au jour de la mise en service → comportement conforme à la politique de reprise. **Bloqué tant que Q-5 n'est pas arbitrée par le client.**

**Non-régression**
- A-17 : le circuit de devis sans remise, la confirmation, et la facturation restent inchangés.

---

## 7. État réel des travaux

- Spécification : rédigée ici, **incomplète** (5 questions bloquantes ouvertes).
- Vérification du standard et des personnalisations : **non faite**.
- Choix configuration / Studio / module : **non établi**.
- Développement : **inexistant**.
- Tests : **aucun**.
- Déploiement : **aucun**.

---

## 8. Entrées à enregistrer

Je n'ai pas écrit ces fichiers ; voici le texte prêt à être collé.

### Entrée pour `PROJECT.md`

```markdown
## Remise commerciale — règle en vigueur

Statut : spécifiée, non développée, non testée, non déployée.
Série : Odoo 19.0.

### Règle actuelle (D-02, D-03)
- Plafond d'autonomie du commercial : 15 % si le client est partenaire, 10 % sinon.
  Source : M-02 (client).
- Au-delà du plafond applicable : approbation du directeur obligatoire.
  Source : M-02.
- « Partenaire » = case « partenaire commercial » cochée sur le contact de
  facturation du devis. Source : M-03.
- Un vendeur ne peut pas approuver sa propre demande. Source : M-03.
- Devis déjà approuvé : revalidation obligatoire si la remise augmente,
  approbation conservée si elle diminue. Source : M-02.
- Les refus doivent être appliqués côté serveur, pas seulement à l'écran.
  Source : exigence de passation, à confirmer par le client.

### Historique des décisions remplacées
- D-01 — remise maximale de 10 % pour tous les clients. Remplacée par M-02.
  Jamais développée : aucune reprise de code ni de configuration à ce titre.

### Questions ouvertes (aucune n'est validée par le silence)
- Q-1 (bloquante) : sur quel champ porte « la remise » — ligne, globale, ou
  moyenne du document ?
- Q-2 (bloquante) : qui est « le directeur » — groupe, utilisateur, hiérarchie,
  responsable d'équipe ?
- Q-3 (bloquante) : « devis approuvé » = approuvé par le directeur ou confirmé ?
- Q-4 (bloquante) : une hausse restant sous le plafond déclenche-t-elle une
  revalidation ? (cas 16 % → 9 % → 14 %)
- Q-5 (bloquante) : politique de reprise des devis existants hors plafond au jour
  de la mise en service. À arbitrer par le client.
- Q-6 : les bornes 10 % et 15 % sont-elles inclusives ? Hypothèse proposée : oui.
- Q-7 : devis sans contact de facturation distinct ; changement de ce contact
  après approbation.
- Q-8 : notification et traçabilité de la perte d'approbation. Hypothèse
  proposée : traçabilité obligatoire.
- Q-9 : le directeur a-t-il un plafond absolu ?

### Voie de réalisation
Non établie. Standard et personnalisations de la série non vérifiés ; aucun
chiffrage. Vérifications préalables : hébergement (Odoo Online interdirait tout
module custom), mécanisme de remise activé, existence d'un circuit d'approbation
réutilisable, faisabilité de R-4 et R-5 dans les limites de Studio, coût de
migration de chaque voie.
```

### Entrée pour `JOURNAL.md`

```markdown
## 2026-09-08 — Remise commerciale : correction du plafond et cadrage

Entrant : M-02 (client) corrigeant D-01, puis M-03 (réponse humaine) précisant la
définition de « partenaire » et l'interdiction de l'auto-approbation.

Fait :
- D-01 (10 % pour tous) marquée remplacée et conservée en historique. Elle
  n'avait jamais été développée : aucune reprise technique à ce titre.
- Règle actuelle formalisée en D-02 (plafonds différenciés, approbation,
  revalidation à la hausse uniquement) et D-03 (définition du partenaire par le
  contact de facturation, séparation demandeur/approbateur).
- Critères d'acceptation A-1 à A-17 rédigés, dont A-11 pour le refus côté serveur.
- Cas traités : partenaire 12 % → autorisé ; non-partenaire 12 % → approbation ;
  partenaire 16 % → approbation ; approuvé 16 % → 17 % → revalidation ;
  approuvé 16 % → 14 % → approbation conservée.

Ouvert :
- Q-1 à Q-5 bloquantes, dont Q-5 (reprise des devis existants) qui relève d'un
  arbitrage client et non d'une décision de développement.
- A-15 et A-16 restent au plan de recette sans résultat attendu, en attente de
  Q-4 et Q-5.

Non fait, à ne pas supposer acquis :
- Aucune consultation du standard Odoo 19 ni des personnalisations de la série.
- Aucun choix entre configuration, Studio et module ; aucun chiffrage.
- Aucun développement, aucun test, aucun déploiement.

Suite : obtenir les réponses à Q-1 à Q-5, puis vérifier hébergement, mécanisme de
remise et circuit d'approbation existant avant d'arbitrer la voie de réalisation.
Les travaux ne dépendant pas de ces réponses (critères d'acceptation sur les
plafonds A-1 à A-7, séparation des rôles A-9 à A-11) peuvent avancer.
```