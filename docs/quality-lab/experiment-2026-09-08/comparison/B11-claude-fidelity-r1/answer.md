Compte-rendu (10 lignes)

- Les cinq scénarios sont tranchés par les règles E‑02/E‑03 déjà arbitrées : 48 unités = seuil (60 % de 80). Détail en §3.
- E‑01 (« tout livrer en une fois ») est **remplacé** par E‑02 ; comme E‑01 n'a jamais été implémenté, il n'y a a priori rien à retirer, à confirmer sur l'état réel du code/base.
- **Verdict standard Odoo 19.0 : non établi.** Sans accès aux sources ni à une copie de base, je ne peux pas affirmer ce qu'Odoo couvre déjà (politique de livraison, case « expéditions partielles » sur le contact). Piste à vérifier en priorité, non prouvée : `picking_policy` sur `sale.order`.
- **Voie technique : non établie.** Le profil du projet (modules custom ? Studio en base ? Online/on‑premise ?) n'est pas connu ; or l'exigence « revalidation sur diminution » et la séparation demandeur/approbateur touchent probablement les limites de Studio.
- 4 questions bloquantes restent ouvertes (granularité, point de blocage, référence après variations, reprise des commandes ouvertes) : le développement peut démarrer sur le socle (champ contact, groupe, seuil), pas sur le moteur de décision.
- À enregistrer : `.odoo-agents/revue_en_cours.md` (release non ouverte), `.odoo-agents/PROJECT.md`, `.odoo-agents/JOURNAL.md` — contenus ci‑dessous, prêts à coller. Je n'ai écrit aucun fichier.

---

# 1. Contenu à enregistrer dans `.odoo-agents/revue_en_cours.md`

```markdown
# Revue fonctionnelle — Approbation des livraisons partielles (E-01/E-02/E-03)

**Projet** Entrepôt Cobalt · **série** 19.0 · **modules concernés** à établir (vente / stock)

## 1. Ce que je comprends
En tant que responsable logistique, je veux que les expéditions partielles ne partent
sans mon approbation que si le client les accepte et si la quantité disponible atteint
60 % du commandé, afin de ne pas dégrader le service client sans arbitrage.
Périmètre : décision « peut-on expédier / faut-il approuver » sur les commandes de vente,
champ d'accord du contact de livraison, séparation demandeur/approbateur, revalidation
en cas de baisse de la quantité proposée.

**Problème réel** : NON ÉTABLI. Aucune évidence fournie (ticket, volume, fréquence, coût
actuel). On ignore combien de commandes par semaine seraient concernées et ce que coûte
aujourd'hui l'absence de règle. À demander avant d'engager un développement.

## 2. Verdict standard Odoo 19.0
**NON ÉTABLI** — aucun accès aux sources ni à une copie de la base client dans cet exercice.
Aucune affirmation d'existence ou d'absence n'est donc opposable ici.

Points à instruire avant tout développement, dans les sources 19.0 puis 19.1/19.4 :
- politique d'expédition existante au niveau de la commande (piste : `picking_policy`
  sur `sale.order`, à confirmer par chemin de fichier) ;
- existence d'un champ standard d'accord aux expéditions partielles sur `res.partner` ;
- mécanisme standard d'approbation/validation à étages sur les transferts ;
- présence en base client de champs Studio, automatisations ou modules tiers couvrant
  déjà tout ou partie de la règle (un développement qui les doublerait serait un défaut).

**Série suivante** : à vérifier dans 19.1/19.4 (`SERIES_MATRIX.md`). Si la fonction y
apparaît, le modèle de données custom doit calquer les noms de champs du futur standard.

## 3. Voies possibles
**NON ÉTABLI** — le profil du projet (nombre de modules custom, présence de Studio,
hébergement Online/SaaS ou non) n'est pas connu, or c'est lui qui tranche la voie par défaut.

Deux exigences pèsent sur ce choix et doivent être vérifiées contre les limites de Studio :
- la revalidation « si la quantité baisse, pas si elle monte » suppose de comparer à un
  état antérieur mémorisé — logique conditionnelle avec historique ;
- « un préparateur ne peut pas approuver sa propre demande » suppose un contrôle sur
  l'utilisateur courant au moment de l'approbation, en plus des droits de groupe.
Si l'une des deux excède `safe_eval`/les automatisations, la voie module s'impose pour
le moteur de décision, Studio restant possible pour le champ du contact et l'écran.

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|----------|-------|----------------------------|-------------|
| 1 | Haute | E-01 vs E-02 | « tout livrer en une fois » et « livrer à 60 % » sont incompatibles | E-02 remplace E-01 ; vérifier qu'aucun code/automatisation n'applique encore E-01, sinon le retirer dans le même lot |
| 2 | Haute | Granularité du seuil | 60 % par ligne et 60 % sur l'ensemble donnent des décisions opposées sur une même commande | Non arbitré — question bloquante Q1 |
| 3 | Haute | Point de blocage | Bloquer à la réservation, à la validation du transfert ou à la confirmation change qui est bloqué et quand | Non arbitré — question bloquante Q2 |
| 4 | Haute | Référence après variations successives | Après 50 approuvé puis 60 sans revalidation, une baisse à 55 est-elle une baisse ? | Non arbitré — question bloquante Q3 |
| 5 | Haute | Reprise des commandes ouvertes | Commandes déjà confirmées, partiellement livrées, ou dont le contact n'a pas la case renseignée | Non arbitré — question bloquante Q4 ; prévoir une valeur par défaut explicite |
| 6 | Moyenne | Séparation demandeur/approbateur | Si le responsable logistique est aussi le préparateur (petite équipe, astreinte), la commande se bloque | Définir le repli : second approbateur, ou blocage assumé et tracé |
| 7 | Moyenne | Contact de livraison ≠ client facturé | La case porte sur le contact de livraison ; sur commande sans adresse de livraison distincte, la référence est ambiguë | Règle explicite : lire le contact de livraison de la commande ; définir le comportement s'il est vide |
| 8 | Moyenne | Changement de contact en cours de vie | Changer l'adresse de livraison après approbation change la règle applicable | Traiter comme un événement de revalidation |
| 9 | Moyenne | Unités et arrondi | 60 % sur des quantités fractionnaires ou des UdM différentes | Comparer le ratio à 0,6 avec la précision décimale des quantités ; « atteint » = ≥ |
| 10 | Moyenne | Volume / performance | Recalcul de disponibilité à chaque mouvement sur un parc inconnu | Mesurer sur copie client avant généralisation |
| 11 | Basse | Non-dits | Multi-société, portail, mobile, commandes importées ou dupliquées, retours/annulations | À couvrir en spec une fois Q1–Q4 tranchées |

## 5. Questions bloquantes
1. Le seuil de 60 % se calcule-t-il ligne à ligne ou sur l'ensemble de la commande (et sur quelle mesure : quantités, valeur) ?
2. À quel moment du flux la règle bloque-t-elle : réservation, validation du transfert, ou plus tôt ?
3. Après une hausse non revalidée (50 → 60), une baisse ultérieure se compare-t-elle à 60 (dernière quantité en vigueur) ou à 50 (dernière quantité explicitement approuvée) ?
4. Que fait-on des commandes déjà ouvertes à la mise en service, et des contacts dont la case n'est pas renseignée ?
5. Qui approuve quand le responsable logistique est lui-même le préparateur de la demande ?

## 6. Hypothèses proposées, non actées
- Seuil « atteint » = quantité disponible **≥** 48 pour 80 commandées (comparaison inclusive).
- Case du contact non renseignée = **refus** des expéditions partielles (repli prudent).
- Référence de baisse = dernière quantité couverte par une approbation en vigueur, mise à jour silencieusement à la hausse (donc 50 → 60 porte la référence à 60).
- Granularité : ensemble de la commande.

Une question bloquante reste ouverte : le silence du client ne valide pas une hypothèse.
Ces propositions ne sont ni des critères définitifs ni des décisions actées. Le socle
(champ du contact, groupe d'approbation, paramètre de seuil) est développable
indépendamment de ces arbitrages ; le moteur de décision ne l'est pas.

## 7. Spécification
Rédaction complète différée : le moteur de décision dépend de Q1–Q4. Socle spécifiable
dès maintenant :
### Modèle de données
- Accord aux expéditions partielles porté par le **contact de livraison** (E-03), booléen ; nom et emplacement à aligner sur le standard 19.x après vérification en sources.
- Seuil 60 % exposé en **paramètre de configuration**, pas en constante dans le code.
- Traçabilité de l'approbation : approbateur, horodatage, quantité approuvée (nécessaire pour la règle de revalidation).
### Sécurité
- Groupe « responsable logistique » habilité à approuver ; contrôle explicite « approbateur ≠ auteur de la demande » (E-03).
### Reprise de données
- À arbitrer (Q4). Un booléen ajouté sur les contacts existants doit avoir une valeur par défaut décidée, pas subie.
### Hors périmètre
- Toute modification de la logique de facturation, des retours et des annulations.

## 8. Critères d'acceptation
Cas de référence : commande de 80 unités, seuil = 48.

- [ ] Contact acceptant les partiels, 50 disponibles → expédition possible **sans approbation** (50 ≥ 48).
- [ ] Contact acceptant les partiels, 40 disponibles → expédition **bloquée jusqu'à approbation** du responsable logistique (40 < 48).
- [ ] Contact refusant les partiels, 50 disponibles → **aucune expédition partielle**, ni directe ni sur approbation ; attente des 80.
- [ ] Livraison approuvée à 50 puis abaissée à 40 → l'approbation **tombe**, nouvelle approbation exigée (baisse ; et 40 < 48).
- [ ] Livraison approuvée à 50 puis portée à 60 → l'approbation **reste valide**, aucune revalidation.
- [ ] Un utilisateur du groupe préparateur ne peut pas approuver une demande dont il est l'auteur (message explicite, pas un échec silencieux).
- [ ] Le seuil est modifiable par configuration sans intervention sur le code.

## 9. Estimation et découpage
Estimation chiffrée : non établie tant que la voie technique et Q1–Q4 le sont pas.
Découpage proposé, livrable dans cet ordre :
1. Socle : case du contact de livraison, groupe d'approbation, paramètre de seuil, traçabilité de l'approbation.
2. Décision « partiel autorisé / approbation requise / attente du complet » (dépend de Q1 et Q2).
3. Revalidation sur baisse (dépend de Q3).
4. Reprise des commandes et contacts existants (dépend de Q4).

**Niveau QA : renforcé** — la fonction touche les droits (approbation, séparation des
rôles) et des données existantes (contacts, commandes ouvertes). Copie de la base client
exigée avant recette.

## 10. Ce que l'utilisateur verra
Non établi tant que Q2 n'est pas tranchée : l'écran où le blocage apparaît dépend du point
du flux retenu. Acquis : une case sur la fiche du contact de livraison, un message de
blocage explicite pour le préparateur, une action d'approbation réservée au responsable
logistique.
```

---

# 2. Passation développeur / testeur

## 2.1 Table de décision (référence unique pour dev et QA)

Commande de 80 unités · seuil = 60 % × 80 = **48**

| # | Contact accepte les partiels | Quantité proposée | Comparaison au seuil | Décision attendue | Source |
|---|---|---|---|---|---|
| 1 | oui | 50 | 50 ≥ 48 | Expédition **sans approbation** | E-02 |
| 2 | oui | 40 | 40 < 48 | **Approbation** du responsable logistique requise | E-02 |
| 3 | non | 50 | sans objet | **Pas d'expédition partielle** ; attendre 80. L'approbation ne débloque pas ce cas | E-02 |
| 4 | oui | 50 approuvé → 40 | baisse | Approbation **invalidée**, revalidation requise (et 40 < 48) | E-02 |
| 5 | oui | 50 approuvé → 60 | hausse | Approbation **maintenue**, pas de revalidation | E-02 |
| — | — | tout cas | — | L'approbateur ne peut pas être l'auteur de la demande | E-03 |

Cas 4 : deux motifs concourent (baisse **et** passage sous le seuil). Un test qui ne
distingue pas les deux ne prouve rien sur la règle de revalidation. Ajouter, une fois Q3
tranchée, un cas de baisse **au‑dessus** du seuil (50 → 49) : c'est lui qui teste la règle
« baisse » isolément.

## 2.2 Pour le développeur

Développable maintenant : le socle (§7 ci‑dessus) — case sur le contact de livraison,
groupe d'approbation, seuil en paramètre, traçabilité approbateur/date/quantité.

Bloqué sur arbitrage client : granularité du calcul (Q1), point de blocage dans le
flux (Q2), référence après variations successives (Q3), reprise de l'existant (Q4).

Avant la première ligne de code, trois vérifications sont dues et n'ont **pas** été faites
ici : ce que le standard 19.0 couvre déjà, ce que la base client contient déjà
(Studio, automatisations, modules tiers), et ce que la série suivante prévoit. Un
développement qui doublerait l'un des trois serait à reprendre.

Points d'attention connus : E-01 n'est pas implémenté mais doit être confirmé comme
absent du code **et** des automatisations ; comparer le ratio avec la précision décimale
des quantités et non en flottant brut ; conserver la quantité approuvée, sans quoi la
règle de revalidation n'est pas calculable.

## 2.3 Pour le testeur

Jeu de données minimal : un article, un contact A (case cochée), un contact B (case
décochée), un contact C (case non renseignée — comportement à confirmer, Q4), un
utilisateur préparateur, un utilisateur responsable logistique, un utilisateur cumulant
les deux rôles.

Exécuter les 5 cas de la table §2.1, plus : approbation refusée par un préparateur sur sa
propre demande ; modification du seuil en configuration et re‑exécution du cas 1 avec un
seuil à 70 % (attendu : 50 < 56 → approbation requise) ; contact de livraison changé
après approbation.

QA renforcée, sur copie de la base client : vérifier l'effet du champ ajouté sur les
contacts existants et l'état des commandes déjà ouvertes avant/après déploiement.

Ne pas tester : la logique de facturation, les retours, les annulations (hors périmètre).

---

# 3. Entrée à ajouter dans `.odoo-agents/PROJECT.md`

```markdown
## Compréhension métier
- Entrepôt Cobalt expédie des commandes dont la disponibilité est parfois partielle.
  L'accord du client aux expéditions partielles est une propriété du **contact de
  livraison**, pas de la commande ni du client facturé (source : E-03, client).
- Le responsable logistique arbitre les expéditions partielles insuffisantes ; le
  préparateur les demande. Les deux rôles sont distincts par principe (source : E-03).
- Volumétrie, fréquence et coût actuel du problème : inconnus, non fournis.

## Décisions actées
- **E-01 abandonné.** La règle « toutes les commandes livrées en une fois » est
  remplacée par la règle de seuil E-02 (source : arbitrage client E-02, « correction »).
  E-01 n'avait pas été implémenté ; absence à confirmer sur le code et la base.
- **Seuil d'expédition sans approbation : 60 % de la quantité commandée**, si le contact
  de livraison accepte les expéditions partielles (source : arbitrage client E-02).
- **Sous le seuil : approbation du responsable logistique obligatoire** (source : E-02).
- **Contact refusant les partiels : attente de la quantité complète**, sans voie
  d'approbation (source : E-02).
- **Revalidation asymétrique** : une livraison partielle approuvée doit être revalidée
  si la quantité proposée diminue, pas si elle augmente (source : E-02).
- **Accord aux partiels = case dédiée sur le contact de livraison** (source : E-03).
- **Séparation demandeur/approbateur** : un préparateur ne peut pas approuver sa propre
  demande (source : E-03).

## En attente d'arbitrage client (non décidé)
- Granularité du calcul du seuil : ligne ou ensemble de la commande.
- Point du workflow où le blocage s'applique.
- Référence de comparaison après variations successives (50 → 60 → 55).
- Reprise des commandes ouvertes et des contacts sans valeur pour la nouvelle case.
- Approbateur de repli quand le responsable logistique est l'auteur de la demande.

## Pièges et points ouverts
- Le seuil doit être configurable, non codé en dur.
- Un booléen ajouté sur `res.partner` a un effet immédiat sur tous les contacts
  existants : la valeur par défaut est une décision, pas un détail technique.
- Verdict standard 19.0 et voie technique (Studio / module / configuration) **non
  établis** : ni les sources ni une copie de la base n'ont été consultées à ce jour.

## État réel de réalisation
- Aucun développement, aucun déploiement, aucun test à ce jour. Aucun état de base connu.
```

---

# 4. Entrée à ajouter dans `.odoo-agents/JOURNAL.md`

```markdown
## 2026-09-08 — Revue fonctionnelle : approbation des livraisons partielles (E-01/E-02/E-03)

**Intervenant** benoit@le-projet.ch · **Rôle** analyste fonctionnel · **Série** 19.0

**Fait** — Revue fonctionnelle rédigée à partir des seuls éléments E-01/E-02/E-03.
Décisions client consolidées et sourcées dans PROJECT.md. Table de décision et passation
dev/testeur produites, couvrant les 5 cas de référence sur 80 unités (seuil = 48) :
50 accepté → sans approbation ; 40 accepté → approbation ; 50 refusé → attente du complet ;
50 puis 40 → revalidation ; 50 puis 60 → approbation maintenue.

**Non fait, volontairement** — Verdict standard Odoo 19.0, comparaison avec la série
suivante, inventaire de la base client, choix de la voie technique, estimation chiffrée.
Aucun accès aux sources, à une copie de base ni à l'instance : ces points restent
**non établis** et ne doivent pas être présentés comme instruits.

**Bloquants ouverts** — 5 questions transmises au client (granularité du seuil, point de
blocage, référence après variations successives, reprise de l'existant, approbateur de
repli). Le socle est développable sans elles ; le moteur de décision ne l'est pas.

**Prochaine étape** — Obtenir une sauvegarde de la base client, instruire le verdict
standard 19.0 puis 19.1/19.4, trancher la voie technique, ouvrir la release.
```