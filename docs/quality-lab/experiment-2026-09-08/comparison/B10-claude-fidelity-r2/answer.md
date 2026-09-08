# Revue fonctionnelle — Plafond de remise commerciale et approbation directeur

**Projet** Atelier Boréal · **série** 19.0 · **modules concernés** `sale` (à confirmer), `res.partner`
**Statut** : exercice sans accès aux sources ni à la base — **verdict standard et voie technique non établis** (voir §2 et §3). Aucun fichier n'a été écrit ; le contenu ci-dessous est prêt à être déposé dans `.odoo-agents/revue_en_cours.md` (la release n'est pas ouverte).

---

## 1. Ce que je comprends

En tant que **commercial**, je veux pouvoir accorder une remise jusqu'au plafond correspondant au statut du client, **afin de** conclure sans passer par une validation quand je reste dans les limites fixées ; au-delà, l'approbation du directeur protège la marge.

Périmètre : devis (`sale.order`), plafonds différenciés partenaire / non-partenaire, workflow d'approbation, revalidation à la hausse.

**Problème réel** : non documenté. Aucune évidence n'a été fournie (ticket, volume de devis concernés, fréquence des dépassements, coût des remises non maîtrisées). C'est une faiblesse du dossier : sans le volume de devis au-dessus de 10 %, on ne sait pas si le workflow d'approbation sera déclenché deux fois par an ou vingt fois par jour — et cela change la voie technique autant que l'ergonomie.

## 2. Règle actuelle en vigueur (à transmettre au développeur)

**R-1 — Plafond sans approbation**
- Client **partenaire** : remise ≤ **15 %**
- Client **non partenaire** : remise ≤ **10 %**

**R-2 — Définition « partenaire »** (M-03) : case **« partenaire commercial »** cochée sur le **contact de facturation du devis** (`partner_invoice_id`), et non sur le client commanditaire (`partner_id`). Les deux peuvent différer : c'est le contact de facturation qui fait foi.

**R-3 — Au-delà du plafond** : approbation du **directeur** requise avant validation du devis.

**R-4 — Séparation des rôles** (M-03) : un vendeur **ne peut pas approuver sa propre demande**, y compris s'il dispose par ailleurs du droit d'approbation.

**R-5 — Revalidation** : un devis **déjà approuvé** dont la remise **augmente** doit être **revalidé** ; s'il **diminue**, l'approbation reste acquise.

### Ce qui remplace l'ancienne décision

| Ancienne | Nouvelle |
|---|---|
| **D-01** — remise maximale de 10 % pour **tous** les clients | **D-02** — 10 % non-partenaire / 15 % partenaire, dépassement possible sur approbation directeur |

D-01 est **remplacée, pas amendée** : elle passe au statut `superseded` (par M-02, confirmée par M-03). Deux glissements à noter au développeur, car ils dépassent le simple changement de chiffre :
1. D-01 posait un **plafond dur** (interdiction) ; D-02 pose un **seuil d'approbation** (franchissable). Le comportement au-delà du seuil n'est plus « bloquer » mais « demander ».
2. D-01 n'existait qu'à l'état de décision : **aucun code n'est à modifier**, tout est à créer. Il n'y a pas de dette de migration sur ce point.

## 3. Traitement des exemples demandés

| # | Cas | Seuil applicable | Résultat attendu |
|---|---|---|---|
| E1 | Partenaire, **12 %** | 15 % | ✅ **Autorisé sans approbation** — le devis reste validable directement par le commercial |
| E2 | Non-partenaire, **12 %** | 10 % | ⚠️ **Approbation directeur requise** — dépassement de 2 points ; le devis ne peut être confirmé tant que l'approbation n'est pas donnée |
| E3 | Partenaire, **16 %** | 15 % | ⚠️ **Approbation directeur requise** |
| E4 | Devis **approuvé** à 16 % → **17 %** | — | 🔄 **Revalidation requise** (hausse). L'approbation antérieure est caduque, le devis retourne en attente d'approbation. L'approbateur ne peut pas être le vendeur du devis (R-4) |
| E5 | Devis **approuvé** à 16 % → **14 %** | — | ✅ **Aucune revalidation** (baisse). L'approbation à 16 % couvre 14 % |

**Point d'attention sur E5, à ne pas résoudre en silence** : si ce devis est celui d'un **non-partenaire**, 14 % reste au-dessus de son seuil de 10 %. La règle « pas de revalidation à la baisse » l'emporte — l'approbation initiale à 16 % couvre a fortiori 14 % — mais le développeur doit implémenter la comparaison **par rapport au taux approuvé**, pas par rapport au seuil. Sinon E5 déclenchera une revalidation parasite. Le symétrique (baisse jusqu'à **9 %**, donc sous le seuil) n'est pas tranché : voir Q4.

## 4. Verdict standard Odoo 19.0

**NON ÉTABLI.** Je n'ai pas accès aux sources `~/odoo-sources/19.0` dans cet exercice, et je ne citerai pas de chemin ni de nom de champ de mémoire. À faire avant tout développement :

1. Vérifier ce que `sale` couvre nativement en 19.0 en matière de limite de remise et de workflow d'approbation sur devis, ainsi que côté Enterprise (`sale_*`, modules de validation/approbation, `approval` le cas échéant).
2. Vérifier l'existence d'un mécanisme générique d'approbation réutilisable plutôt que d'un workflow ad hoc — un développement qui réimplémente un moteur d'approbation standard serait un défaut de priorité 1.
3. Vérifier la présence d'une case « partenaire commercial » **déjà existante** sur `res.partner` (champ standard, champ Studio, ou module tiers) avant d'en créer une : la mémoire projet ne dit pas si elle existe. Sans copie de base ni inventaire, « à créer » est une supposition, pas un constat.
4. Regarder la **série suivante** : si Odoo introduit un plafond de remise en 19.1+, calquer les noms de champs sur le futur standard pour que la migration soit une suppression.

**Série suivante** : non vérifié.

## 5. Voies possibles

**Non tranchée.** Le profil du projet (nombre de modules custom, présence de Studio en base) n'est pas connu ici, or c'est lui qui donne la voie par défaut. Deux éléments de cadrage, à confirmer :

- La règle R-4 (« un vendeur ne peut pas approuver sa propre demande ») est une **comparaison entre l'utilisateur courant et le vendeur de l'enregistrement**. Elle sort du domaine des règles d'accès déclaratives simples ; en Studio elle relèverait de `safe_eval` dans une automatisation, ce qui est faisable mais peu testable (pas de test Python).
- La règle R-5 exige de **mémoriser le taux au moment de l'approbation** pour comparer hausse/baisse. Un champ technique persistant est nécessaire — ce n'est pas un calcul à la volée.

Ces deux points penchent vers un module, mais **la décision revient à l'humain** une fois le profil connu.

## 6. Contradictions et risques

| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| R1 | **Haute** | Assiette de la remise non définie | Odoo porte la remise **par ligne**. « Le devis a 12 % » n'a pas de sens si les lignes ont 0 %, 10 % et 20 %. Max ? moyenne pondérée ? remise globale ? Sans réponse, tous les critères d'acceptation sont ininterprétables | Q1 (bloquante) |
| R2 | **Haute** | Contact de facturation modifiable après approbation | Un devis approuvé à 16 % pour un partenaire (seuil 15) dont on change le contact de facturation pour un non-partenaire : le seuil tombe à 10 %, la remise n'a pas bougé. R-5 ne prévoit pas ce cas — la hausse est du côté du *seuil*, pas de la remise | Traiter le changement de `partner_invoice_id` comme un événement de revalidation ; à arbitrer (Q3) |
| R3 | **Haute** | « Approbation du directeur » non qualifié | Groupe de sécurité ? champ sur l'équipe commerciale ? responsable hiérarchique ? Un seul directeur ou un par équipe ? Détermine le modèle de sécurité entier | Q2 (bloquante) |
| R4 | Moyenne | R-4 et cas du directeur-vendeur | Si le directeur établit lui-même un devis à 20 %, R-4 lui interdit de l'approuver. Blocage total si c'est le seul approbateur | Prévoir un approbateur de secours ou une exception explicite ; à arbitrer |
| R5 | Moyenne | Duplication de devis | Un devis approuvé dupliqué ne doit pas hériter de son approbation. Piège classique de `copy()` | Réinitialiser l'état d'approbation et le taux approuvé à la copie — à inscrire dans la spec |
| R6 | Moyenne | Reprise de données | Des devis existants dépassent probablement déjà les seuils. Les bloquer rétroactivement gèlerait des affaires en cours | Q5 (bloquante) |
| R7 | Moyenne | Portée : devis seulement ? | M-02 parle de « devis ». Et une **commande confirmée** modifiée ? Un avenant ? Une remise appliquée à la facture sans passer par le devis contournerait tout le dispositif | À arbitrer, hypothèse H3 |
| R8 | Faible | Non-dits | Multi-société (la case partenaire est-elle globale ou par société ?), multi-devise (sans objet si la remise est en %, structurant si un jour en montant), portail (le client voit-il « en attente d'approbation » ?), mobile, import de devis, modèles de devis | À couvrir en recette |
| R9 | Faible | Remise en **montant** | Si un utilisateur peut saisir une remise en valeur plutôt qu'en pourcentage, le contrôle est contournable | Vérifier la configuration de `sale` sur l'instance |

## 7. Questions bloquantes

1. **Assiette de la remise** — sur quoi porte le « 12 % » : la remise maximale d'une ligne, la moyenne pondérée sur le total, ou un champ de remise globale au niveau du devis ? Quel champ fait foi pour le contrôle ? *(sans réponse, rien n'est spécifiable)*
2. **Le directeur** — qui approuve, techniquement ? Groupe de sécurité dédié, responsable de l'équipe commerciale, utilisateur nommé ? Et que fait-on si le seul approbateur est aussi le vendeur (R4) ?
3. **Effet de la revalidation** — le devis revalidé retourne dans quel état ? Brouillon (perte de la signature/de l'envoi client) ou un état « en attente d'approbation » distinct qui préserve l'historique ? Et le client est-il notifié ?
4. **Retour sous le seuil** — un devis approuvé à 16 % dont la remise descend à 9 % (sous le seuil de 10 %) reste-t-il marqué « approuvé », ou l'approbation devient-elle sans objet ? *(E5 est tranché, ce cas ne l'est pas)*
5. **Reprise** — que fait-on des devis en cours dépassant les seuils au jour de la mise en service : tolérés en l'état, bloqués à la prochaine modification, ou marqués pour revue ? Combien y en a-t-il ? *(le volume conditionne la réponse ; il faut la copie de base)*

## 8. Hypothèses proposées, **non actées**

- **H1** — La remise s'exprime en pourcentage, ligne par ligne, et le contrôle porte sur le **taux le plus élevé** parmi les lignes.
- **H2** — Le taux approuvé est **mémorisé** à l'approbation ; la comparaison de R-5 se fait contre ce taux mémorisé, pas contre le seuil.
- **H3** — Le dispositif s'applique aux devis **non confirmés**. Les commandes confirmées et les factures sont hors périmètre du premier incrément.
- **H4** — Si `partner_invoice_id` est vide, le contact de facturation retenu est celui déduit du client (comportement Odoo par défaut) ; à défaut de case cochée, le client est **non partenaire**.
- **H5** — La duplication réinitialise l'approbation.

Ces cinq points sont des propositions de travail. Une question bloquante reste ouverte : **le silence du client ne vaut pas validation**. Ne pas les transformer en comportement à implémenter ni en critères définitifs. Le développeur peut avancer sur ce qui n'en dépend pas : la case « partenaire commercial » sur le contact et la lecture du seuil applicable (§9, incrément 1) ne dépendent d'aucune des cinq questions.

## 9. Spécification

### Modèle de données
- `res.partner` : case « partenaire commercial » (booléen) — **vérifier d'abord si elle existe déjà** (standard, Studio ou module tiers) avant d'en créer une.
- `sale.order` : seuil applicable (calculé, non stocké, dérivé du contact de facturation), remise de référence (calculée selon H1, à confirmer par Q1), indicateur « approbation requise », état d'approbation, **taux approuvé** (stocké, H2), approbateur et date d'approbation.

### Comportement
- Le seuil est déterminé par la case « partenaire commercial » du **contact de facturation** du devis (R-2).
- Remise ≤ seuil → aucune approbation. Remise > seuil → approbation requise avant confirmation.
- L'approbateur doit disposer du droit d'approbation **et** être différent du vendeur du devis (R-4).
- Devis approuvé, remise **augmentée** → l'approbation tombe, revalidation requise (R-5). Remise **diminuée** → approbation conservée.
- Duplication → approbation et taux approuvé réinitialisés (H5).

### Interface
- Indication visible de l'état d'approbation sur le devis, bouton d'approbation réservé aux approbateurs habilités, message explicite au blocage (« remise de 12 % supérieure au plafond de 10 % applicable à ce client — approbation directeur requise »).

### Sécurité
- Le droit d'approbation est distinct du droit de vente. La règle R-4 s'applique **au niveau serveur** et pas seulement par masquage du bouton : un bouton caché n'est pas un contrôle.

### Reprise de données
- Dépend de Q5. Aucune contrainte obligatoire ne doit être ajoutée sur un modèle peuplé sans réponse à cette question.

### Hors périmètre (premier incrément)
- Commandes confirmées, avenants, factures (H3) · remises en montant · historique d'approbation exportable · notification client.

## 10. Critères d'acceptation

Rédigés sous H1/H2 ; à figer après réponse à Q1.

- [ ] Étant donné un devis dont le contact de facturation a la case « partenaire commercial » **cochée**, quand la remise est de **12 %**, alors le devis est validable **sans approbation** *(E1)*.
- [ ] Étant donné un devis dont le contact de facturation a la case **décochée**, quand la remise est de **12 %**, alors le devis **requiert l'approbation du directeur** et ne peut être confirmé avant *(E2)*.
- [ ] Étant donné un devis dont le contact de facturation est **partenaire**, quand la remise est de **16 %**, alors le devis **requiert l'approbation du directeur** *(E3)*.
- [ ] Étant donné un devis **approuvé** à **16 %**, quand la remise passe à **17 %**, alors l'approbation est révoquée et une **nouvelle approbation** est requise *(E4)*.
- [ ] Étant donné un devis **approuvé** à **16 %**, quand la remise passe à **14 %**, alors le devis **reste approuvé** et aucune action n'est demandée *(E5)*.
- [ ] Étant donné le même devis à **14 %** pour un client **non partenaire** (seuil 10 %), alors il reste **approuvé** : la comparaison porte sur le taux approuvé, pas sur le seuil.
- [ ] Étant donné un devis nécessitant approbation, quand **le vendeur du devis** tente de l'approuver, alors l'action est **refusée côté serveur**, même s'il appartient au groupe des approbateurs *(R-4)*.
- [ ] Étant donné un devis dont la remise est exactement **au seuil** (10 % non-partenaire, 15 % partenaire), alors **aucune approbation** n'est requise — le seuil est inclusif.
- [ ] Étant donné un devis **approuvé**, quand il est **dupliqué**, alors la copie est **non approuvée** *(H5)*.
- [ ] Étant donné un devis sans contact de facturation partenaire identifié, alors le seuil appliqué est **10 %** *(H4)*.

## 11. Découpage et QA

| # | Incrément | Dépend de |
|---|---|---|
| 1 | Case « partenaire commercial » sur le contact + calcul et affichage du seuil applicable sur le devis (aucun blocage) | rien — **livrable immédiatement** |
| 2 | Détection du dépassement + blocage de la confirmation | Q1 |
| 3 | Workflow d'approbation + règle de non-auto-approbation | Q2, Q3 |
| 4 | Revalidation à la hausse (mémorisation du taux approuvé) | Q3, Q4 |
| 5 | Reprise des devis existants | Q5 |

**Niveau QA : renforcé, obligatoire.** Le sujet touche les **droits** (R-4, séparation vendeur/approbateur) et les **données existantes** (reprise). Recette sur **copie de la base client**, avec au minimum : un utilisateur vendeur, un approbateur, un utilisateur cumulant les deux rôles (test de R-4), et des devis existants au-dessus des seuils.

**Note au testeur** : les cas E1→E5 ci-dessus sont le jeu d'essai minimal. Y ajouter les cas limites (remise exactement au seuil, changement de contact de facturation après approbation, duplication) et vérifier R-4 **par appel serveur direct**, pas seulement via l'interface.

---

## Entrée prête à enregistrer — `.odoo-agents/PROJECT.md`

> Contenu proposé, **non écrit**.

```markdown
### Compréhension métier

- **Statut « partenaire »** : Atelier Boréal distingue des clients partenaires,
  qui bénéficient d'une latitude commerciale supérieure. Le statut se lit sur le
  **contact de facturation** du devis (case « partenaire commercial »), et non sur
  le client commanditaire — les deux peuvent différer.
- La politique de remise fonctionne par **seuil d'approbation**, pas par plafond dur :
  au-delà du seuil, la vente reste possible avec l'aval du directeur.

### Décisions actées

- **D-01** — Remise commerciale maximale de 10 % pour tous les clients.
  **Statut : REMPLACÉE par D-02** (message client M-02 du 2026-09-08).
  Jamais développée : aucune dette technique associée.
- **D-02** (source : M-02, client) — Seuil de remise sans approbation :
  **15 %** pour les clients partenaires, **10 %** pour les autres.
  Au-delà, **approbation du directeur** requise.
- **D-03** (source : M-02, client) — Un devis déjà approuvé doit être **revalidé**
  si sa remise **augmente** ; il conserve son approbation si elle **diminue**.
- **D-04** (source : M-03, arbitrage humain) — « Partenaire » = case
  « partenaire commercial » cochée sur le **contact de facturation du devis**.
- **D-05** (source : M-03, arbitrage humain) — **Un vendeur ne peut pas approuver
  sa propre demande de remise.** Contrôle attendu côté serveur.

### Propositions non actées

- H1 assiette de la remise (taux le plus élevé parmi les lignes) · H2 mémorisation
  du taux approuvé · H3 périmètre limité aux devis non confirmés · H4 défaut
  non-partenaire si contact de facturation absent · H5 réinitialisation à la
  duplication. **Aucune n'est validée par le client.**

### Questions ouvertes (bloquantes)

Q1 assiette de la remise · Q2 identité technique du « directeur » · Q3 état du
devis après revalidation · Q4 retour sous le seuil · Q5 reprise des devis existants.

### État réel de réalisation

- **Non développé. Non déployé. Non testé.** Aucun code écrit à ce jour.
- **Verdict standard Odoo 19.0 : non établi** — les sources n'ont pas été
  consultées. À faire avant tout développement, ainsi que l'inventaire de la
  configuration en base (la case « partenaire commercial » existe peut-être déjà).
- **Voie technique (Studio / module / configuration) : non tranchée** — profil du
  projet inconnu.
```

## Entrée prête à enregistrer — `JOURNAL.md`

> Contenu proposé, **non écrit**.

```markdown
## 2026-09-08 — Revue fonctionnelle : plafonds de remise et approbation directeur

**Contexte** — Le client corrige la règle de remise (M-02) et précise deux points
d'application (M-03). Aucun développement n'avait démarré sur D-01.

**Fait**
- Analyse de la demande, consolidation de la règle en vigueur (D-02 à D-05).
- D-01 (plafond unique à 10 %) marquée REMPLACÉE : changement de nature, on passe
  d'un plafond bloquant à un seuil d'approbation.
- Rédaction de la spécification, des 10 critères d'acceptation et du découpage en
  5 incréments, dont le premier est livrable sans attendre les arbitrages.
- Traitement explicite des 5 cas soumis par le client (12 % partenaire / 12 % non
  partenaire / 16 % partenaire / 16→17 % / 16→14 %).

**Non fait**
- Sources Odoo 19.0 non consultées : **verdict standard non établi**.
- Base client non inventoriée : l'existence de la case « partenaire commercial » et
  le volume de devis concernés restent inconnus.
- Voie technique non arbitrée (profil du projet non relevé).

**Points d'attention transmis**
- L'assiette de la remise (Q1) n'est pas définie : la remise Odoo est portée par
  les lignes, « le devis a 12 % » est ambigu. Bloque les incréments 2 à 5.
- Le changement de contact de facturation après approbation peut faire baisser le
  seuil sans que la remise bouge — cas non couvert par D-03.
- QA renforcée obligatoire (droits + données existantes), sur copie client.

**Prochaine étape** — Obtenir les réponses à Q1–Q5, relever le profil du projet,
inventorier la base ; puis ouvrir la release et basculer la revue vers
`changelog/<release>/revue_fonctionnelle.md`.
```

---

**Synthèse en dix lignes** — Règle en vigueur : seuil 15 % partenaire / 10 % sinon, dépassement sur approbation du directeur, revalidation à la hausse uniquement, pas d'auto-approbation, statut partenaire lu sur le contact de facturation. D-01 est remplacée par D-02, pas amendée : on change de nature (plafond dur → seuil franchissable) ; rien n'ayant été développé, il n'y a pas de dette. Les cinq exemples sont tranchés au §3 ; attention à E5, où la comparaison doit se faire contre le **taux approuvé** et non contre le seuil. Verdict standard et voie technique **non établis** faute d'accès aux sources et à la base — à faire avant la première ligne de code. Cinq questions bloquantes (§7), dont Q1 sur l'assiette de la remise qui conditionne tous les critères d'acceptation. L'incrément 1 (case partenaire + affichage du seuil) est livrable sans attendre ces réponses. QA renforcée obligatoire. Aucun fichier n'a été écrit ; la revue irait dans `.odoo-agents/revue_en_cours.md`, les deux entrées ci-dessus dans `.odoo-agents/PROJECT.md` et `JOURNAL.md`.