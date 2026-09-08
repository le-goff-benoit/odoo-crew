## Préambule — ce que cet exercice permet et ne permet pas

Je n'ai ni sources Odoo, ni base client, ni dépôt : je n'ai lancé ni `odoo_briefing.py`, ni `odoo-config-inventory.sh`, ni aucun `grep` dans `~/odoo-sources/19.0`. **Le verdict standard et la voie technique restent donc non établis** — ils sont posés en hypothèses à vérifier, marquées comme telles, et c'est la première tâche de la passation.

Je ne peux pas non plus écrire de fichier. Ce qui suit est le **contenu à enregistrer**, à trois emplacements : `.odoo-agents/revue_en_cours.md` (aucune release n'est ouverte dans le dossier fourni), `.odoo-agents/PROJECT.md`, `.odoo-agents/JOURNAL.md`.

---

## Règle consolidée et les 5 cas demandés

Seuil : 60 % de 80 = **48 unités**. « Atteint 60 % » est lu comme **≥ 48** (inclusif) — à confirmer, cf. Q4.

| # | Situation | Quantité dispo | Résultat attendu |
|---|---|---|---|
| T-01 | Contact accepte les partiels | 50 | **Livraison partielle sans approbation** (50 ≥ 48) |
| T-02 | Contact accepte les partiels | 40 | **Approbation du responsable logistique requise** (40 < 48) ; le préparateur demandeur ne peut pas être l'approbateur |
| T-03 | Contact refuse les partiels | 50 | **Aucune livraison partielle** ; attente des 80 unités complètes. Le seuil de 60 % ne s'applique pas |
| T-04 | Partielle approuvée à 50, ramenée à 40 | 40 | **Approbation invalidée, revalidation requise** (quantité en baisse) |
| T-05 | Partielle approuvée à 50, portée à 60 | 60 | **Approbation conservée, aucune revalidation** (quantité en hausse) |

**Point important pour le testeur** : T-04 et T-05 sont robustes à l'ambiguïté signalée en Q3 (une livraison à 50 avec contact acceptant n'aurait pas dû requérir d'approbation — l'énoncé postule pourtant une approbation existante). Sous les deux lectures possibles, T-04 finit en « approbation requise » (40 < 48 de toute façon) et T-05 en « livrable sans nouvelle approbation ». Ces deux tests sont donc exécutables **avant** l'arbitrage. Les cas qui, eux, dépendent de l'arbitrage sont hors périmètre de test tant que Q3/Q5 ne sont pas tranchées :
- approuvée à 40, ramenée à 30 (baisse sous le seuil, déjà sous le seuil) ;
- approuvée à 50 → portée à 60 → ramenée à 55 : hausse par rapport à la **dernière quantité approuvée** (50), baisse par rapport à la **dernière quantité proposée** (60). Deux résultats opposés selon la référence retenue.

---

## Fichier 1 — `.odoo-agents/revue_en_cours.md`

```markdown
# Revue fonctionnelle — Livraisons partielles conditionnées (E-01 → E-03)

**Projet** Entrepôt Cobalt · **série** 19.0 · **modules concernés** à établir
(candidats : sale, stock, sale_stock — non vérifiés)

## 1. Ce que je comprends
En tant que préparateur, je veux savoir si je peux expédier une commande
incomplète, afin de ne pas immobiliser du stock disponible ni expédier chez un
client qui refuse les partiels.
Périmètre : règle de décision « peut-on livrer partiellement ? », approbation
par le responsable logistique, case d'accord sur le contact de livraison.

**Problème réel** : non établi. Aucun ticket, volume, fréquence ni coût actuel
n'est fourni dans le dossier. Nombre de commandes concernées par mois, part des
contacts refusant les partiels, coût du blocage actuel : à demander avant
d'engager le développement. C'est ce qui décide si la fonction vaut son prix.

## 2. Verdict standard Odoo 19.0
**NON ÉTABLI** — aucune source n'a été consultée dans cet exercice.

Trois vérifications à faire avant toute ligne de code, par ordre de rendement :
1. **E-01 est probablement de la configuration, pas du développement.** Odoo
   porte historiquement une politique de livraison « tout en une fois / dès que
   possible » au niveau de la commande de vente et du partenaire. À vérifier :
   `grep -rn "picking_policy" ~/odoo-sources/19.0/addons/sale*/models/*.py
   ~/odoo-sources/19.0/addons/stock/models/*.py`. Si le champ existe, E-01 se
   règle par paramétrage + valeur par défaut sur le partenaire, et le
   développement se réduit au seuil de 60 % et à l'approbation.
2. **E-03, « case dédiée du contact »** : vérifier si un champ équivalent existe
   déjà sur `res.partner` avant d'en créer un. Un champ custom qui double un
   champ standard est un défaut de priorité 1.
3. **Base client** : aucun état de base fourni. Un champ Studio ou une
   automatisation peuvent déjà porter tout ou partie de la règle. Demander une
   sauvegarde et passer `odoo-config-inventory.sh` avant de conclure
   « à développer ».

**Série suivante** : non vérifié. À contrôler dans `~/odoo-sources/19.1` et
`19.4` — si le standard couvre la fonction plus tard, le modèle de données doit
en calquer les noms de champs dès maintenant.

## 3. Voies possibles
Non tranché — le profil du projet (nombre de modules custom, présence de
Studio, hébergement SaaS ou non) n'est pas connu. La grille reste à remplir
après le briefing.

| Voie | Effort | Ce que l'utilisateur obtient | Coût migration | Recommandée |
|---|---|---|---|---|
| Configuration | à établir | couvre probablement E-01 seul | quasi nul | à évaluer en 1er |
| Studio / base | à établir | case partenaire + champs ; approbation par automatisation | moyen | selon profil |
| Code custom | à établir | règle complète + revalidation | payé à chaque migration | selon profil |

Signal ferme quelle que soit la voie : la revalidation sur baisse de quantité
suppose de mémoriser un état entre deux modifications. En Studio, c'est à la
limite de ce que `safe_eval` et les automatisations portent proprement ; si
l'arbitrage Q1/Q5 mène à un suivi par ligne, la voie module devient probable.

## 4. Contradictions et risques
| # | Sévérité | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| R1 | Majeure | E-01 « tout en une fois » vs E-02 qui autorise les partiels | Règles contradictoires si E-01 reste en vigueur | E-02 est explicitement une « correction » du client : E-01 est abrogé. Acté, cf. PROJECT.md |
| R2 | Majeure | Approbation postulée à 50 (T-04/T-05) alors que 50 ≥ 48 ne requiert aucune approbation | La règle de revalidation vise un état d'approbation que la règle d'entrée ne produit pas dans ce cas | Q3 |
| R3 | Majeure | Référence après variations successives (50 → 60 → 55) | Dernière quantité **approuvée** ou dernière quantité **proposée** : résultats opposés | Q5 |
| R4 | Majeure | Granularité ligne ou commande | 60 % atteint sur l'ensemble peut masquer une ligne à 0 % | Q1 |
| R5 | Majeure | Point de blocage dans le workflow | Bloquer la réservation, la validation du picking ou la confirmation de commande n'a ni le même effet ni le même coût | Q2 |
| R6 | Majeure | Reprise des commandes ouvertes | Commandes en cours, partiellement réservées, déjà livrées en partie : état d'approbation initial indéfini | Q4 |
| R7 | Moyenne | E-03 « un préparateur ne peut pas approuver sa propre demande » | Séparation demandeur/approbateur : à porter par les groupes **et** par une contrainte serveur, pas seulement par l'écran | Contrainte au niveau modèle + test dédié |
| R8 | Moyenne | Multi-société, multi-entrepôt, contact de livraison ≠ client facturé | La case est sur le **contact de livraison** : à quel partenaire exactement (`partner_shipping_id`) ? | À figer dans la spec |
| R9 | Moyenne | Valeur par défaut de la case sur les contacts existants | Un défaut « accepte » ouvre des expéditions non voulues ; « refuse » bloque le parc | Défaut proposé : refus. Non acté, cf. hypothèses |
| R10 | Moyenne | Seuil 60 % en dur | Sera renégocié ; codé en dur, chaque changement est une intervention | Paramètre de configuration, pas une constante |
| R11 | Moyenne | Arrondis et unités de mesure | 60 % de 7 unités = 4,2 ; comportement sur UoM non décimales indéfini | Règle d'arrondi à figer |
| R12 | À vérifier | Pièges de série 19.0 (`res.users.groups_id` → `group_ids`, `_sql_constraints` → `models.Constraint`, `ir.model.access.csv`) | Un développement écrit avec les idiomes < 19.0 ne passera pas | Contrôler SERIES_MATRIX.md — **non vérifié dans cet exercice** |

## 5. Questions bloquantes
1. **Q1 — Granularité** : le seuil de 60 % s'apprécie-t-il ligne par ligne, ou
   sur la quantité totale de la commande ? Une commande de 80 unités sur deux
   lignes de 40, dont l'une à 100 % et l'autre à 20 %, est-elle livrable ?
2. **Q2 — Point de blocage** : où la règle s'applique-t-elle — confirmation de
   commande, réservation, ou validation du bon de livraison ? C'est ce point qui
   détermine l'écran où le préparateur voit le blocage.
3. **Q3 — Approbation au-dessus du seuil** : une livraison à 50 sur 80 avec
   contact acceptant est autorisée sans approbation. Peut-elle malgré tout
   porter une approbation (dérogation, validation volontaire) ? Sinon, les cas
   « approuvée à 50 » de E-02 sont sans objet et la règle de revalidation ne
   concerne que les quantités sous le seuil.
4. **Q4 — Commandes ouvertes** : à la mise en service, les commandes en cours
   sont-elles considérées comme approuvées, à réapprouver, ou hors périmètre ?
   Et « atteint 60 % » est-il inclusif (48 exactement passe) ?
5. **Q5 — Référence après variations** : après 50 approuvé puis 60 puis 55, on
   compare à la dernière quantité **approuvée** (50 → hausse → pas de
   revalidation) ou à la dernière quantité **proposée** (60 → baisse →
   revalidation) ?

Cinq questions bloquantes sur une demande de cette taille : la demande est à la
limite de la maturité. Rien ne doit être développé sur Q1, Q2 et Q5 avant
réponse — ce sont des choix de modèle, pas des détails d'écran.

## 6. Hypothèses proposées, non actées
- H1 : seuil apprécié sur la quantité totale de la commande (Q1).
- H2 : blocage à la validation du bon de livraison (Q2).
- H3 : « atteint 60 % » inclusif, 48 exactement passe (Q4).
- H4 : référence = dernière quantité approuvée (Q5).
- H5 : case du contact à « refuse les partiels » par défaut sur les contacts
  existants (R9).
- H6 : seuil de 60 % exposé en paramètre de configuration (R10).

Une question bloquante reste ouverte : le silence du client ne valide pas une
hypothèse. Ces propositions ne sont ni des critères définitifs ni des décisions
actées. Ce qui peut avancer sans elles : la vérification du standard (section
2), l'inventaire de la base client, la case sur le contact de livraison et la
séparation demandeur/approbateur.

## 7. Spécification
### Modèle de données
- Sur le contact de livraison : indicateur booléen « accepte les expéditions
  partielles ». **Nom du champ à figer après vérification qu'aucun équivalent
  standard ou Studio n'existe** (section 2).
- Sur l'objet porteur de la livraison (commande ou bon de livraison — dépend de
  Q2) : état d'approbation, quantité approuvée de référence, approbateur, date.
- Paramètre de configuration : seuil, valeur initiale 60 %.
- Le reste du modèle est suspendu à Q1, Q2 et Q5.

### Comportement
1. Contact refusant les partiels → aucune expédition avant la quantité complète,
   quel que soit le taux disponible. Le seuil ne s'applique pas.
2. Contact acceptant, quantité disponible ≥ seuil → expédition autorisée, sans
   approbation.
3. Contact acceptant, quantité disponible < seuil → approbation du responsable
   logistique requise.
4. Approbation acquise puis quantité en baisse → approbation invalidée,
   nouvelle approbation requise.
5. Approbation acquise puis quantité en hausse → approbation conservée.

### Interface
Non figée : dépend de Q2. Ce qui est certain : le motif du blocage doit être
lisible par le préparateur (quel contact, quel taux atteint, quel seuil), sans
quoi il ouvrira un ticket à chaque cas.

### Sécurité
- Approbation réservée au responsable logistique.
- L'approbateur ne peut pas être le demandeur (E-03). À porter par une
  contrainte serveur, testable, pas seulement par un masquage de bouton.
- Vérifier les idiomes de groupes de la série 19.0 avant écriture (R12).

### Reprise de données
- Valeur de la case sur les contacts existants : suspendu à R9/H5.
- Traitement des commandes ouvertes : suspendu à Q4.
- Volume réel inconnu : à mesurer sur copie de la base avant migration.

### Hors périmètre
- Notification ou relance de l'approbateur.
- Historique ou reporting des approbations.
- Reliquats, regroupement d'expéditions, transporteurs.

## 8. Critères d'acceptation
- [ ] Étant donné 80 commandées, un contact acceptant les partiels et 50
      disponibles, quand le préparateur lance la livraison, alors elle part sans
      approbation.
- [ ] Étant donné 80 commandées, un contact acceptant les partiels et 40
      disponibles, quand le préparateur lance la livraison, alors elle est
      bloquée et une approbation du responsable logistique est demandée.
- [ ] Étant donné 80 commandées, un contact refusant les partiels et 50
      disponibles, quand le préparateur lance la livraison, alors elle est
      refusée et aucun seuil n'est proposé ; l'attente porte sur 80.
- [ ] Étant donné une livraison partielle approuvée à 50, quand la quantité
      proposée passe à 40, alors l'approbation est invalidée et une nouvelle
      approbation est requise.
- [ ] Étant donné une livraison partielle approuvée à 50, quand la quantité
      proposée passe à 60, alors l'approbation reste valide et la livraison part
      sans nouvelle approbation.
- [ ] Étant donné une demande d'approbation créée par le préparateur P, quand P
      tente de l'approuver, alors le serveur refuse l'opération.
- [ ] Étant donné le seuil porté de 60 % à 70 % dans la configuration, quand une
      commande de 80 avec 50 disponibles est traitée, alors une approbation est
      requise — sans intervention sur le code.

## 9. Estimation et découpage
Estimation non chiffrable : voie technique non arrêtée et périmètre suspendu à
cinq questions bloquantes. Ordre proposé :
- **I0** — Vérification standard 19.0 + inventaire de la base client. Peut
  supprimer une partie du développement. À faire avant tout chiffrage.
- **I1** — Case « accepte les partiels » sur le contact de livraison + règle de
  refus strict (cas T-03). Livrable seul, indépendant de Q1/Q5.
- **I2** — Seuil paramétrable et blocage sous seuil (T-01, T-02). Dépend de Q1
  et Q2.
- **I3** — Approbation, séparation demandeur/approbateur (T-02, contrainte E-03).
- **I4** — Revalidation sur baisse (T-04, T-05). Dépend de Q3 et Q5.
- **I5** — Reprise des commandes ouvertes et des contacts. Dépend de Q4.

**Niveau QA : renforcé**, avec copie client — la fonction touche des droits
(approbation, séparation des rôles) et des données existantes (contacts,
commandes ouvertes).

## 10. Ce que l'utilisateur verra
Le préparateur verra un blocage motivé au lancement de la livraison, avec le
taux atteint et le seuil. Le responsable logistique verra une demande à
approuver, et la reverra si la quantité baisse. L'administrateur verra une case
sur le contact de livraison et un seuil dans les paramètres. L'écran exact
dépend de Q2.
```

---

## Fichier 2 — entrées à ajouter dans `.odoo-agents/PROJECT.md`

```markdown
## Compréhension métier
- Entrepôt Cobalt expédie des commandes dont la quantité disponible est souvent
  inférieure à la quantité commandée. L'arbitrage entre « expédier tout de
  suite » et « attendre le complet » dépend du **contact de livraison**, pas du
  client facturé.
- Deux rôles distincts interviennent : le **préparateur**, qui demande, et le
  **responsable logistique**, qui approuve.
- La quantité livrable varie dans le temps entre la demande et l'expédition :
  la règle doit donc gérer un état d'approbation, pas seulement un contrôle
  instantané.
- Volumes, fréquence et coût actuel du problème : **inconnus**, non fournis.

## Décisions actées
- **E-02 abroge E-01.** La règle « toutes les commandes doivent être livrées en
  une fois » est remplacée par la règle conditionnelle. *Source : arbitrage
  explicite du client, E-02, formulé comme « correction ».* E-01 n'avait jamais
  été implémentée : aucune reprise de code n'est due à ce titre.
- **Seuil de livraison sans approbation : 60 % de la quantité commandée**,
  applicable uniquement si le contact de livraison accepte les partiels.
  *Source : client, E-02.*
- **Sous le seuil : approbation du responsable logistique obligatoire.**
  *Source : client, E-02.*
- **Contact refusant les partiels : attente de la quantité complète**, le seuil
  ne s'applique pas. *Source : client, E-02.*
- **Revalidation asymétrique** : une livraison partielle approuvée doit être
  revalidée si la quantité proposée diminue, pas si elle augmente.
  *Source : client, E-02.*
- **L'accord aux expéditions partielles est porté par une case dédiée du contact
  de livraison.** *Source : client, E-03.*
- **Séparation demandeur/approbateur** : un préparateur ne peut pas approuver sa
  propre demande. *Source : client, E-03.*

## En attente d'arbitrage client (ne pas développer)
- Granularité du calcul : ligne ou ensemble de la commande.
- Point du workflow où le blocage s'applique.
- Reprise des commandes ouvertes à la mise en service ; caractère inclusif du
  seuil (48 exactement).
- Possibilité d'une approbation au-dessus du seuil (cohérence des cas
  « approuvée à 50 » de E-02).
- Quantité de référence après variations successives : dernière approuvée ou
  dernière proposée.

## État réel de réalisation
- Rien n'est développé, déployé ni testé. E-01 n'a jamais été implémentée.
- Verdict standard Odoo 19.0 : **non établi**, aucune source consultée.
- État de la base client : **inconnu**, aucune sauvegarde fournie ; présence
  éventuelle de champs Studio ou d'automatisations non inventoriée.
- Voie technique (configuration / Studio / module) : **non arrêtée**, profil du
  projet inconnu.

## Pièges connus
- Vérifier `picking_policy` (ou équivalent) dans le standard avant tout
  développement sur E-01 : forte présomption de configuration suffisante.
- Ne pas coder le seuil de 60 % en dur.
- La case porte sur le **contact de livraison**, à ne pas confondre avec le
  client facturé.
- Série 19.0 : contrôler les idiomes de groupes, de contraintes SQL et de
  droits d'accès avant écriture (non vérifié à ce jour).
```

---

## Fichier 3 — entrée à ajouter dans `.odoo-agents/JOURNAL.md`

```markdown
## 2026-09-08 — Revue fonctionnelle E-01/E-02/E-03, livraisons partielles

**Intervenant** analyste fonctionnel · **Projet** Entrepôt Cobalt · **Série** 19.0
**Livrable** `.odoo-agents/revue_en_cours.md` (aucune release ouverte)

**Fait**
- Consolidation des consignes E-01, E-02 et E-03 en une règle unique ; E-02
  identifié comme abrogeant E-01.
- Cinq cas de référence chiffrés sur 80 unités commandées (seuil = 48), remis
  au testeur : 50/accepte → sans approbation ; 40/accepte → approbation ;
  50/refuse → attente du complet ; 50 puis 40 → revalidation ; 50 puis 60 →
  approbation conservée.
- Douze risques et cinq questions bloquantes formulés ; découpage en six
  incréments proposé ; niveau QA renforcé retenu (droits + données existantes).

**Non fait — et pourquoi**
- Aucune source Odoo consultée, aucun briefing lancé, aucune base inventoriée :
  outils indisponibles. Le **verdict standard reste non établi** et la **voie
  technique non arrêtée**. Aucune affirmation sur le standard n'est sourcée.
- Aucun chiffrage : le périmètre dépend de cinq arbitrages ouverts.

**Prochaine action**
1. Lancer `odoo_briefing.py` sur le module, puis vérifier dans
   `~/odoo-sources/19.0` si le standard couvre E-01 (piste : politique de
   livraison sur la commande / le partenaire) et si un champ standard porte déjà
   l'accord aux partiels.
2. Demander une sauvegarde de la base client et passer
   `odoo-config-inventory.sh` : champs Studio, automatisations, volumes réels.
3. Envoyer les cinq questions bloquantes au client. Ne rien développer sur la
   granularité, le point de blocage et la référence de revalidation avant
   réponse.
4. Demander l'évidence du problème réel : nombre de commandes concernées,
   fréquence, coût actuel. Elle manque totalement.
```

---

## Compte-rendu

- **Verdict standard : non établi.** Aucune source consultée — je ne peux pas dire si Odoo 19.0 fait déjà tout ou partie de la demande, et c'est la première chose à trancher. Forte présomption que E-01 relevait d'un simple paramétrage.
- **Voie technique : non arrêtée**, profil du projet et contenu de la base inconnus.
- **Décision structurante actée** : E-02 abroge E-01 (source : correction explicite du client).
- **Les 5 cas demandés sont chiffrés** (seuil = 48) et exécutables ; T-04 et T-05 sont testables malgré l'ambiguïté sur l'approbation au-dessus du seuil, ce qui n'est pas le cas des variations successives.
- **5 questions bloquantes** : granularité, point de blocage, approbation au-dessus du seuil, commandes ouvertes + inclusivité, référence après variations. C'est le maximum : la demande est à la limite de la maturité.
- **Évidence manquante** : ni volume, ni fréquence, ni coût actuel. On ne sait pas encore si la fonction vaut son prix.
- **Emplacements** : `.odoo-agents/revue_en_cours.md`, `.odoo-agents/PROJECT.md`, `.odoo-agents/JOURNAL.md` — contenus ci-dessus, à enregistrer manuellement, je n'ai pas pu écrire.