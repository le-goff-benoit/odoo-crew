# Passation — Plafond de remise commerciale · Atelier Boréal (Odoo 19.0)

> Exercice sans outils : je n'ai lu ni les sources Odoo, ni le code du projet, ni une copie de la base. **Le verdict standard et la voie technique restent donc non établis** — je liste plus bas ce qu'il faut vérifier avant de trancher. Aucun fichier n'a été écrit ; les entrées PROJECT.md et JOURNAL.md ci-dessous sont prêtes à être enregistrées par qui de droit.

## 1. La règle actuelle (consolidée D-01 + M-02 + M-03)

En tant que commercial, je veux saisir une remise sur un devis dans une limite qui dépend du type de client, afin d'engager l'entreprise sans validation quand je suis dans mon mandat, et de passer par le directeur quand j'en sors.

Règle telle qu'elle se lit aujourd'hui :

1. **Plafond sans approbation** : 15 % si le client est *partenaire*, 10 % sinon.
2. **Partenaire** = case « partenaire commercial » cochée sur le **contact de facturation du devis** (et non sur le client principal, ni sur le contact de livraison).
3. **Au-delà du plafond** : approbation du directeur obligatoire.
4. **Séparation des rôles** : un vendeur ne peut pas approuver sa propre demande.
5. **Revalidation** : un devis déjà approuvé dont la remise **augmente** doit être revalidé ; s'il **diminue**, l'approbation en place reste valable.

## 2. Ce qui remplace l'ancienne décision

| | Avant (D-01) | Après (D-02, à acter) |
|---|---|---|
| Plafond | 10 % pour **tous** les clients | 10 % par défaut, **15 % pour les partenaires** |
| Dépassement | non spécifié | approbation directeur, avec séparation vendeur/approbateur |
| Cycle de vie | non spécifié | revalidation à la hausse, pas à la baisse |
| Notion de partenaire | inexistante | définie par une case sur le contact de facturation |

D-01 est **remplacée, pas amendée** : sa formulation « pour tous les clients » est désormais fausse et ne doit plus être citée. Point favorable : D-01 n'ayant jamais été développée, il n'y a **aucune reprise de données ni de code à défaire** — sous réserve de vérifier qu'aucun paramétrage (limite de remise, champ Studio, automatisation) n'a été posé en base entre-temps.

## 3. Les exemples demandés

| Cas | Résultat attendu | Justification |
|---|---|---|
| Partenaire, 12 % | **Autorisé sans approbation** | 12 ≤ 15 |
| Non-partenaire, 12 % | **Approbation directeur requise** | 12 > 10 |
| Partenaire, 16 % | **Approbation directeur requise** | 16 > 15 |
| Devis approuvé à 16 %, passe à **17 %** | **Revalidation obligatoire** : l'approbation tombe, le devis retourne en attente d'approbation | remise en hausse |
| Devis approuvé à 16 %, passe à **14 %** | **Pas de revalidation** : l'approbation reste valable, le devis reste approuvé | remise en baisse |

Deux sous-cas du dernier exemple, à ne pas laisser au développeur :

- **Partenaire, 16 % → 14 %** : la remise repasse **sous le plafond** (14 ≤ 15). L'approbation devient sans objet. On la conserve telle quelle (règle « la baisse ne revalide pas ») ou on la purge ? Le comportement observable diffère : trace d'approbation visible sur un devis qui n'en a plus besoin. → question ouverte Q4.
- **Non-partenaire, 16 % → 14 %** : la remise reste **au-dessus** du plafond (14 > 10). L'approbation initiale, donnée pour 16 %, couvre 14 % : pas de revalidation. Cohérent avec la règle, à confirmer explicitement car c'est le cas où l'on « approuve par le passé » un montant jamais soumis tel quel.

Un troisième cas non couvert par les exemples mais inévitable en test : **changement du contact de facturation** sur un devis approuvé, faisant passer le client de partenaire à non-partenaire à remise constante (16 % approuvé, devient 16 % non-partenaire). La remise n'augmente pas, mais le plafond baisse. → question ouverte Q2.

## 4. Questions encore ouvertes

**BLOQUANTES** (sans réponse, risque de tout refaire) :

1. **Assiette du plafond** : le seuil s'applique-t-il à la remise de **chaque ligne**, à la remise **moyenne pondérée** du devis, ou à une remise **globale** ? Un devis à 5 % sur 90 % du montant et 40 % sur une ligne symbolique passe ou pas ? Toute la logique de comparaison et de détection de « hausse » en dépend.
2. **Évaluation du statut partenaire** : figé au moment de l'approbation, ou recalculé en continu (donc réversible si le contact de facturation change) ? Et que vaut le statut si le devis n'a pas de contact de facturation distinct, ou si la case est cochée sur la société mère mais pas sur le contact ?
3. **Qui est « le directeur »** : un groupe de sécurité dédié, le responsable hiérarchique du vendeur, ou un utilisateur paramétré par société ? Et si l'unique porteur du droit est lui-même le vendeur du devis, la demande est-elle bloquée ou remonte-t-elle ailleurs ?
4. **Effet de la revalidation** : le devis retourne-t-il en brouillon, ou reste-t-il approuvable dans un état « en attente d'approbation » sans perdre sa numérotation et son historique d'envoi ? Peut-il être envoyé au client pendant l'attente ?
5. **Périmètre du cycle de vie** : la règle s'applique-t-elle uniquement au **devis**, ou aussi au bon de commande confirmé et aux avenants ? Une remise modifiée après confirmation déclenche-t-elle la même revalidation ?

**À ARBITRER** (on peut avancer sous hypothèse écrite) :

- Sort de l'approbation quand la remise repasse sous le plafond (cf. §3).
- Comportement sur les remises négatives / majorations, sur les devis importés ou dupliqués (un duplicata d'un devis approuvé à 16 % doit repartir non approuvé — à confirmer).
- Multi-société : plafonds identiques partout, ou paramétrables par société ?
- Le client est-il notifié / voit-il quoi que ce soit ? À ce stade je pars sur **rien de visible côté portail**.

## 5. Ce qu'il reste à établir avant d'écrire une ligne de code

À faire par qui aura les accès, dans cet ordre :

1. **Briefing du module** et série confirmée (19.0 annoncée) ; vérifier notamment les changements 19.0 qui touchent les droits (`groups_id` → `group_ids`, `ir.model.access.csv`) si la voie retenue est un module.
2. **Standard Odoo 19.0** : chercher dans les sources s'il existe déjà un mécanisme de plafond de remise et un workflow d'approbation sur `sale.order` (côté Community *et* Enterprise) avant de conclure « à développer ». Si un mécanisme d'approbation générique existe et couvre 80 % du besoin, le développement se réduit au calcul du plafond.
3. **Inventaire de la base client** : la case « partenaire commercial » existe-t-elle déjà (champ standard, champ Studio, ou à créer) ? Y a-t-il déjà une automatisation sur la remise ? Combien de devis existants dépassent 10 % et 15 % — c'est le volume de la reprise éventuelle.
4. **Profil du projet** (modules custom ? Studio ? Online ou on-premise ?) : c'est lui qui tranche entre Studio et module. Réserve : une règle qui doit **bloquer** une valeur, tracer un approbateur et interdire l'auto-approbation touche les limites de Studio (pas de surcharge de méthode, pas de test Python) ; si le projet est Online, il faudra écrire le risque résiduel.

## 6. Critères d'acceptation (pour le testeur)

Plafonds :
- [ ] Étant donné un devis dont le contact de facturation a la case partenaire cochée, quand le commercial saisit 12 %, alors le devis est enregistrable et confirmable sans approbation.
- [ ] Étant donné un devis dont le contact de facturation n'a pas la case cochée, quand le commercial saisit 12 %, alors le devis ne peut pas être confirmé sans approbation du directeur et l'utilisateur voit un message le lui indiquant.
- [ ] Étant donné un devis partenaire, quand le commercial saisit 16 %, alors une approbation du directeur est requise.
- [ ] Étant donné un devis partenaire à exactement 15 % (et un devis non-partenaire à exactement 10 %), alors aucune approbation n'est requise — le seuil est inclusif.

Séparation des rôles :
- [ ] Étant donné un devis créé par le vendeur V et nécessitant une approbation, quand V tente d'approuver, alors l'approbation est refusée avec un message explicite, même si V dispose du droit d'approbation.
- [ ] Étant donné le même devis, quand le directeur D (≠ V) approuve, alors le devis passe approuvé et l'identité de D ainsi que la date sont tracées et consultables.

Cycle de vie :
- [ ] Étant donné un devis approuvé à 16 %, quand la remise passe à 17 %, alors l'approbation est invalidée, le devis repasse en attente d'approbation et ne peut pas être confirmé en l'état.
- [ ] Étant donné un devis approuvé à 16 %, quand la remise passe à 14 %, alors le devis reste approuvé, aucune nouvelle demande n'est créée et il reste confirmable.
- [ ] Étant donné un devis approuvé à 16 % chez un non-partenaire, quand la remise passe à 14 % (toujours > 10 %), alors le devis reste approuvé sans nouvelle demande.
- [ ] Étant donné un devis approuvé, quand on le duplique, alors la copie n'est pas approuvée.

Non-régression / droits :
- [ ] Étant donné un utilisateur sans droit d'approbation, alors le bouton d'approbation n'est pas visible et l'appel direct de l'action est refusé (test côté serveur, pas seulement côté vue).
- [ ] Étant donné les devis existants en base, quand la fonctionnalité est installée, alors aucun devis existant ne devient non modifiable ni ne bascule en attente d'approbation de façon rétroactive (comportement à confirmer avec Q5).

**Niveau QA : renforcé** — la demande porte sur des droits, un workflow d'approbation et le montant facturé. Tests à rejouer sur copie de la base client, pas seulement sur base vierge.

## 7. Découpage proposé

1. **Incrément 1** — identification du partenaire (champ/critère sur le contact de facturation) et calcul du plafond applicable, affiché en lecture seule sur le devis. Livrable seul, sans blocage : permet de valider Q1 et Q2 sur données réelles.
2. **Incrément 2** — blocage de la confirmation au-dessus du plafond + demande d'approbation + droits et interdiction d'auto-approbation.
3. **Incrément 3** — invalidation de l'approbation à la hausse, conservation à la baisse, et traçabilité.

Les incréments 2 et 3 sont bloqués par les questions Q1, Q3, Q4 ; l'incrément 1 peut démarrer dès que Q2 est tranchée et que l'inventaire de la base a dit si la case partenaire existe déjà.

---

## Entrée prête à enregistrer — `PROJECT.md`

```markdown
## Décisions actées

### D-02 — Plafond de remise commerciale différencié (remplace D-01)
- **Provenance** : message client M-02 du <date>, précisé par la réponse humaine M-03.
- **Statut** : décidée côté métier — **non développée, non déployée, non testée**.
- **Règle** :
  - plafond de remise sans approbation : **15 %** pour un client partenaire, **10 %** sinon ;
  - **partenaire** = case « partenaire commercial » cochée sur le **contact de facturation
    du devis** (pas le client principal, pas le contact de livraison) ;
  - au-delà du plafond : **approbation du directeur** obligatoire ;
  - **un vendeur ne peut pas approuver sa propre demande** ;
  - un devis déjà approuvé dont la remise **augmente** doit être revalidé ; s'il
    **diminue**, l'approbation en place reste valable.
- **Remplace D-01** (« remise maximale de 10 % pour tous les clients »). D-01 n'ayant
  jamais été développée, aucune reprise de code ni de données n'est requise ; reste à
  vérifier qu'aucun paramétrage n'a été posé en base entre-temps.

## Compréhension métier
- Le réseau de clients d'Atelier Boréal est segmenté : les **partenaires commerciaux**
  bénéficient d'un mandat de négociation plus large (15 % contre 10 %). La segmentation
  se lit au niveau du **contact de facturation**, ce qui implique qu'un même groupe
  client peut avoir des plafonds différents selon l'entité facturée.
- Le dépassement de plafond n'est pas interdit : il est **délégué au directeur**. Le
  besoin porte donc autant sur la traçabilité de l'approbation que sur le blocage.
- L'asymétrie hausse/baisse indique que l'approbation est comprise comme un **plafond
  autorisé** (« je t'autorise jusqu'à 16 % ») et non comme la validation d'une valeur
  exacte.

## Points à établir (non tranchés)
- Assiette du plafond : remise par ligne, moyenne pondérée, ou remise globale.
- Définition opérationnelle du « directeur » (groupe dédié / hiérarchie / paramètre société).
- Périmètre : devis seul, ou aussi bons de commande confirmés et avenants.
- Verdict standard Odoo 19.0 et voie technique (configuration / Studio / module) :
  **non établis**, faute d'accès aux sources, au code du projet et à une copie de la base.
```

## Entrée prête à enregistrer — `JOURNAL.md`

```markdown
## <date> — Revue fonctionnelle : plafond de remise commerciale

**Intervenant** : analyste fonctionnel · **Nature** : analyse, aucun fichier de module modifié.

- Consolidation de D-01, du message client M-02 et de la réponse humaine M-03 en une
  règle unique ; **D-01 est remplacée par D-02** (le plafond n'est plus uniforme à 10 %).
- Passation préparée pour le développeur et le testeur : règle consolidée, 5 cas de
  référence arbitrés (partenaire 12 % OK, non-partenaire 12 % → approbation,
  partenaire 16 % → approbation, 16 %→17 % → revalidation, 16 %→14 % → pas de
  revalidation), 5 questions bloquantes, 11 critères d'acceptation, découpage en
  3 incréments.
- **État réel** : rien n'est développé, déployé ni testé. Aucune revue n'a été écrite
  sur disque au cours de cette session.
- **Non établi faute d'accès** : briefing du module, verdict standard Odoo 19.0
  (existe-t-il déjà un plafond de remise / un workflow d'approbation sur `sale.order` ?),
  inventaire de la base client (la case « partenaire commercial » existe-t-elle déjà ?
  volumétrie des devis > 10 % et > 15 %), profil du projet et donc voie technique.
- **Prochaine étape** : lancer le briefing et l'inventaire de configuration, puis
  trancher Q1 (assiette du plafond) et Q3 (définition du directeur) avec le client
  avant tout démarrage des incréments 2 et 3.
- **Niveau QA retenu** : renforcé (droits, workflow d'approbation, montant facturé) —
  tests sur copie de la base client obligatoires.
```

---

**Réserve à conserver dans la passation** : les questions 1 à 5 restent ouvertes. Le silence du client ne les valide pas ; les hypothèses de la section 4 ne doivent pas être transformées en comportement à implémenter. L'incrément 1 est le seul démarrable en l'état.