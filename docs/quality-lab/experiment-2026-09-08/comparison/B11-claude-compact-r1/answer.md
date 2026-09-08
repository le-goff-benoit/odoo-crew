## 0. Statut de l'exercice

Aucun outil n'a été utilisé : je n'ai ni ouvert la base, ni lu le code de la série, ni exécuté de test. Tout ce qui suit est dérivé du seul dossier fourni (E-01, E-02, E-03). Le verdict « standard / Studio / module » reste **non établi**, et aucun chiffrage n'est donné.

---

## 1. Règle métier consolidée (état courant)

| # | Règle | Source | Statut |
|---|---|---|---|
| R1 | Le contact de livraison porte un accord explicite aux expéditions partielles, matérialisé par une case dédiée sur le contact. | E-03 (client) | Décision client |
| R2 | Contact **refusant** les partiels → aucune livraison avant quantité complète. | E-02 (client) | Décision client |
| R3 | Contact **acceptant** les partiels, disponible ≥ 60 % du commandé → livraison sans approbation. | E-02 | Décision client |
| R4 | Contact acceptant, disponible < 60 % → approbation du responsable logistique requise. | E-02 | Décision client |
| R5 | Une livraison partielle **déjà approuvée** doit être revalidée si la quantité proposée **diminue** ; pas si elle augmente. | E-02 | Décision client |
| R6 | Un préparateur ne peut pas approuver sa propre demande (séparation des rôles). | E-03 | Décision client |

**Historique remplacé** — E-01 : « toutes les commandes doivent être livrées en une fois ». Règle jamais implémentée, explicitement corrigée par E-02. À conserver comme historique : elle explique pourquoi aucun code existant n'est censé porter cette contrainte, et sert de garde-fou si quelqu'un la retrouve ailleurs dans la documentation projet.

---

## 2. Questions bloquantes (ouvertes, non résolues par le silence)

| Q | Question | Impact si non tranchée |
|---|---|---|
| Q1 | **Granularité du seuil 60 %** : calculé ligne par ligne, ou sur l'ensemble de la commande (quantités agrégées / valeur) ? | Change le résultat de la majorité des commandes multi-lignes. Bloquant pour le développement du calcul. |
| Q2 | **Point de blocage dans le workflow** : au moment de la réservation, à la validation du transfert, ou à la confirmation de commande ? | Détermine le modèle porteur du contrôle et l'ergonomie du refus. Bloquant. |
| Q3 | **Référence après variations successives** : après une approbation à 50 puis passage à 60, une redescente à 55 est-elle une diminution (par rapport à 60) ou reste-t-elle couverte (≥ 50 approuvé) ? | Bloquant pour R5. Deux implémentations légitimes et divergentes. |
| Q4 | **Reprise des commandes ouvertes** : les commandes déjà confirmées au moment de la mise en service sont-elles soumises à la règle, gelées, ou traitées manuellement ? | Bloquant pour le déploiement, pas pour le développement du cœur de règle. |
| Q5 | **Case « accepte les partiels »** : sur quel contact exactement (adresse de livraison, client facturé, société parente) et comportement si l'adresse de livraison n'a pas la case mais le parent oui ? | Bloquant pour R1/R2. |
| Q6 | **Hébergement** (Odoo Online / Odoo.sh / on-premise) et existence de personnalisations sur les livraisons dans la série. | Détermine si un module custom est possible. Odoo Online imposerait une voie sans module. Bloquant pour le choix de voie, pas pour la spécification métier. |

Aucune de ces questions n'a été arbitrée par le client. Elles restent ouvertes dans la spécification, dans la recette et dans la mémoire projet tant qu'une réponse sourcée n'est pas enregistrée.

---

## 3. Hypothèses proposées (à confirmer, non appliquées)

- **H1** : le seuil de 60 % s'entend en quantités, seuil inclusif (« atteint 60 % » → 60 % exactement passe sans approbation). Sur 80 unités, le seuil est **48**.
- **H2** : l'approbation porte sur une quantité précise, pas sur la commande en général ; c'est cette quantité qui sert de référence à R5.
- **H3** : R5 s'applique aux livraisons ayant fait l'objet d'une approbation ; le cas d'une livraison partie sans approbation (≥ 60 %) puis abaissée sous le seuil relève de R4 (nouvelle approbation nécessaire) — à confirmer, la formulation d'E-02 ne le dit pas.
- **H4** : « responsable logistique » et « préparateur » correspondent à deux droits distincts à créer ou à mapper sur les groupes existants.

---

## 4. Vérifications à mener avant de choisir la voie

Sans accès, aucun résultat n'est disponible ; voici ce qu'il faut établir :

1. Ce que couvre déjà le standard Odoo 19 en matière de politique d'expédition sur la commande de vente (livraison dès que possible / quand tout est prêt) et sur la gestion des reliquats de transfert — pour savoir quelle part de R2/R3 est de la configuration.
2. Absence ou présence d'un champ standard « accepte les livraisons partielles » sur le contact ; à défaut, champ à créer.
3. Personnalisations existantes de la série sur `sale.order` / `stock.picking` susceptibles d'entrer en conflit.
4. Hébergement et politique du projet en matière de modules custom.
5. Capacité de Studio à porter le contrôle serveur exigé par R6 : une contrainte purement écran ne satisfait pas la règle. Ne pas promettre de contournement technique des limites de Studio.

Comparaison des voies (configuration / Studio / module) à faire ensuite sur : couverture réelle du besoin, profil du projet, coût de migration. **Verdict actuel : non établi.**

---

## 5. Passation développeur

Points à couvrir, indépendamment de la voie retenue (aucun code ici) :

- **Calcul du taux de disponibilité** : nécessite Q1 avant écriture. Seuil inclusif à 60 % sous H1.
- **Drapeau contact** : lecture du consentement selon Q5 ; comportement par défaut si la case n'a jamais été cochée = refus (position conservatrice, à valider).
- **Contrôle d'accès** : le refus d'approbation par le demandeur (R6) doit être **rejeté côté serveur**, pas seulement masqué dans l'interface. Un test doit tenter l'approbation directement via l'appel serveur avec l'utilisateur préparateur et vérifier le refus.
- **Traçabilité** : conserver, sur l'objet approuvé, l'identité de l'approbateur, la date et la **quantité approuvée** — c'est la donnée de référence de R5 et de Q3.
- **Invalidation** : mécanisme de retour à l'état « à approuver » lors d'une diminution ; ne pas déclencher lors d'une augmentation.
- **Reprise de données** : rien à coder tant que Q4 n'est pas arbitrée ; ne pas choisir une politique de reprise par défaut au motif qu'elle est pratique.

---

## 6. Passation testeur — cas demandés (80 unités commandées, seuil 48 sous H1)

| Cas | Contexte | Attendu | Règle | Remarque |
|---|---|---|---|---|
| T1 | Contact accepte, 50 disponibles | Livraison possible **sans approbation** (50 ≥ 48) | R3 | — |
| T2 | Même contact, 40 disponibles | Livraison **bloquée** en attente d'approbation du responsable logistique (40 < 48) | R4 | — |
| T3 | Contact refuse, 50 disponibles | **Aucune livraison** ; attente des 80 unités. Le seuil de 60 % ne s'applique pas. | R2 | Vérifie que R2 prime sur R3 |
| T4 | Approuvée à 50, abaissée à 40 | Approbation **invalidée**, revalidation requise | R5 | — |
| T5 | Approuvée à 50, portée à 60 | Approbation **conservée**, pas de revalidation | R5 | — |

### Cas limites et discriminants complémentaires

| Cas | Contexte | Attendu | Objet du test |
|---|---|---|---|
| T6 | Contact accepte, exactement 48 disponibles | Sans approbation | Inclusivité du seuil (H1) — discriminant |
| T7 | Contact accepte, 47 disponibles | Approbation requise | Borne basse du seuil |
| T8 | Approuvée à 50, abaissée à 49 | Revalidation requise **bien que 49 ≥ 48** | Discrimine R5 (toute baisse) de R4 (seuil seul) |
| T9 | 55 livrables sans approbation, puis chute à 40 | À définir — dépend de H3 | Zone non spécifiée par E-02 ; ne pas figer en recette avant réponse client |
| T10 | Approuvée à 50 → 60 → 55 | À définir — dépend de Q3 | Cas discriminant central sur la référence |
| T11 | Préparateur tente d'approuver sa propre demande via l'écran | Bouton indisponible | R6, couche écran |
| T12 | Même tentative par appel serveur direct | **Refus serveur** | R6, couche réelle des droits — discriminant |
| T13 | Responsable logistique approuve une demande d'un autre utilisateur | Accepté | Non-régression de R6 |
| T14 | Commande multi-lignes, une ligne à 100 %, une à 20 % | À définir | Dépend de Q1 ; cas discriminant ligne vs ensemble |
| T15 | Contact de livraison sans case cochée (jamais renseignée) | À définir | Dépend de Q5 et du défaut retenu |

T9, T10, T14, T15 restent **non recettables** tant que les questions correspondantes sont ouvertes : ils sont listés pour ne pas être oubliés, pas pour être exécutés avec un attendu inventé.

**État réel des travaux : aucun développement, déploiement ni test réalisé ou constaté.**

---

## 7. Entrée à enregistrer dans PROJECT.md

```markdown
## Livraisons partielles — règle d'approbation (Entrepôt Cobalt, Odoo 19.0)

### Règle courante
- Le contact de livraison porte une case dédiée « accepte les expéditions
  partielles ». [source : E-03, client]
- Contact refusant : aucune livraison avant la quantité complète. [E-02]
- Contact acceptant, disponible >= 60 % du commandé : livraison sans
  approbation. [E-02]
- Contact acceptant, disponible < 60 % : approbation du responsable
  logistique requise. [E-02]
- Une livraison partielle approuvée est revalidée si la quantité proposée
  diminue ; pas si elle augmente. [E-02]
- Un préparateur ne peut pas approuver sa propre demande ; le refus doit
  être appliqué côté serveur, pas seulement à l'écran. [E-03]

### Historique remplacé
- E-01 : « toutes les commandes doivent être livrées en une fois ».
  Jamais implémentée, corrigée par E-02. Conservée pour mémoire.

### Questions ouvertes (bloquantes, non arbitrées)
- Q1 granularité du seuil 60 % : ligne ou ensemble de la commande.
- Q2 point du workflow où le blocage s'applique.
- Q3 référence de comparaison après variations successives (50 -> 60 -> 55).
- Q4 politique de reprise des commandes déjà ouvertes.
- Q5 contact exact porteur de la case et comportement en cas d'absence.
- Q6 hébergement et personnalisations existantes de la série ; Odoo Online
  interdirait un module custom.

### Hypothèses non validées
- Seuil en quantités, inclusif : 60 % de 80 = 48 unités.
- L'approbation porte sur une quantité précise, qui sert de référence.
- Défaut conservateur si la case contact n'est pas renseignée : refus.

### Voie de réalisation
Non établie. Configuration / Studio / module non départagés : le standard
Odoo 19 et les personnalisations de la série n'ont pas été inspectés.
Aucun chiffrage.

### État des travaux
Aucun développement, déploiement ni test réalisé.
```

---

## 8. Entrée à enregistrer dans JOURNAL.md

```markdown
## 2026-09-08 — Cadrage règle de livraison partielle

Analyse documentaire du dossier Entrepôt Cobalt (E-01 à E-03). Aucun outil
utilisé : pas de lecture de base, de code ni d'exécution de test.

- E-01 (livraison en une fois) constatée non implémentée et remplacée par
  l'arbitrage client E-02. Conservée comme historique.
- Règle courante consolidée à partir d'E-02 et E-03, six points, sources
  tracées dans PROJECT.md.
- Six questions bloquantes formalisées (granularité, point de blocage,
  référence après variations, reprise des commandes ouvertes, contact
  porteur de la case, hébergement/personnalisations). Aucune n'est levée ;
  le silence du client ne les valide pas.
- Passation développeur rédigée : exigence d'un refus serveur pour la
  séparation préparateur/approbateur, traçabilité de la quantité approuvée
  comme référence de revalidation.
- Jeu de recette rédigé : 5 cas demandés (80 unités, seuil 48 sous
  hypothèse) + 10 cas limites/discriminants. Quatre d'entre eux
  (T9, T10, T14, T15) sont marqués non recettables car dépendants de
  questions ouvertes ; aucun attendu n'a été inventé pour ces cas.
- Voie de réalisation non tranchée, aucun chiffrage produit.

Prochaine étape : obtenir les réponses client sur Q1 à Q5 et les éléments
techniques de Q6 avant toute décision de voie.
```