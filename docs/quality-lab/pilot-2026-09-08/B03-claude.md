## Compte-rendu (ce qui compte, en dix lignes)

Aucun outil n'est disponible dans cet exercice : je n'ai lancé ni `odoo_briefing.py`, ni inventaire de base, ni `grep` dans `~/odoo-sources/19.0`. **Je ne peux donc pas rendre le verdict standard**, seulement le préparer et donner les commandes exactes qui le trancheront. Tout ce qui suit est une revue *sous réserve de ces vérifications*, pas un constat.

- **Verdict provisoire** : PARTIEL à confirmer. Odoo porte le motif « double validation au-delà d'un seuil » dans **Achats**, pas (à ma connaissance, non vérifiée) dans Ventes en Community. À vérifier avant toute ligne de code.
- **Voie recommandée** (sous réserve du profil projet) : petit **module custom** surchargeant `action_confirm`, calqué sur le nommage de `purchase`.
- **Bloquants réels** : 3 — définition de « important », qui approuve, et le fait que **la confirmation ne passe pas que par le bouton** (portail, signature, paiement en ligne).
- **Fichier cible** : aucune release ouverte n'est indiquée → `.odoo-agents/revue_en_cours.md`. Contenu ci-dessous, à recopier.

---

# Revue fonctionnelle — Validation responsable des devis importants

**Projet** Atelier Boréal · **série** 19.0 · **modules concernés** `sale` (+ `sale_management`), à compléter après briefing

## 0. Ce qui manque pour que cette revue soit fiable

| Élément | Pourquoi il est nécessaire | Comment l'obtenir |
|---|---|---|
| `odoo_briefing.py <module>` | série exacte (19.0 / 19.1 / 19.4 : `ir.access.csv` change en 19.4), release en cours, modules custom déjà présents, décisions actées | à lancer avant tout |
| Verdict standard | affirmer « ça n'existe pas » sans chemin de fichier est interdit par la méthode | greps §2 |
| Copie de base + `odoo-config-inventory.sh` | savoir si un champ Studio / une automatisation fait **déjà** tout ou partie du travail, et connaître les volumes (nb de devis, distribution des montants → le seuil se choisit sur des données, pas au doigt mouillé) | demander la sauvegarde au client |
| Profil projet (Studio ? modules ?) | tranche la voie par défaut (§3) | briefing + inventaire |

Sans la copie de base, le risque n°1 est de développer un doublon d'une automatisation existante.

## 1. Ce que je comprends

*En tant que responsable commercial, je veux devoir approuver les devis dépassant un certain montant avant qu'ils ne soient confirmés, afin que les opérations aval (livraison, production, facturation) ne se déclenchent pas sur un engagement que je n'ai pas validé.*

Périmètre : modèle `sale.order`, une société, N vendeurs + 2 responsables. La confirmation est le point de non-retour (elle déclenche l'aval) : c'est bien elle qu'il faut instrumenter, pas l'envoi du devis.

**Problème réel — non établi.** Le dossier donne une solution (« un responsable valide »), pas le problème vécu. Il manque l'évidence : combien de devis « importants » par mois, quel incident a déclenché la demande (remise excessive ? prix hors grille ? engagement de délai intenable ? mauvaise créance ?), quel a été son coût. **Ce point conditionne la spec** : si l'incident portait sur les **remises**, un seuil sur le montant total ne l'attrapera pas, et on aura livré un contrôle qui ne protège de rien. C'est l'observation la plus utile de cette revue. À poser au client avant développement.

## 2. Verdict standard Odoo 19.0 — **à établir, non rendu**

Hypothèses de travail à confirmer, chacune avec sa commande :

```bash
S=~/odoo-sources/19.0
# 1. Existe-t-il une double validation côté ventes ?
grep -rn "double_validation" $S/addons/sale*/ ${S}-enterprise/sale*/
# 2. Le motif de référence côté achats (à transposer si absent en vente)
grep -rn "po_double_validation" $S/addons/purchase/models/ $S/addons/purchase/res_config_settings*
# 3. Points d'extension réels de la confirmation
grep -rn "def action_confirm\|def _action_confirm\|def _can_be_confirmed" $S/addons/sale/models/sale_order.py
# 4. Une app d'approbations générique réutilisable ?
ls ${S}-enterprise | grep -i approval
grep -rn "approval" ${S}-enterprise/*/models/*.py | grep -i "sale" | head -30
# 5. Contrôles de remise déjà présents (si le vrai problème, c'est la remise)
grep -rn "discount" $S/addons/sale/models/sale_order_line.py | head -30
# 6. Série suivante : la fonction arrive-t-elle en standard ?
grep -rn "double_validation\|approval" ~/odoo-sources/19.4/addons/sale/models/ | head
```

Lecture des résultats :
- si (1) ou (4) remonte → **ÇA EXISTE / PARTIEL**, on configure, on ne développe pas ;
- si seul (2) remonte → **À DÉVELOPPER**, mais en **calquant le nommage d'`purchase`** (`so_double_validation`, `so_double_validation_amount`, groupe dédié) : si Odoo standardise plus tard, la migration devient une suppression de module, pas une reprise ;
- (6) est obligatoire : un développement que la série suivante rend standard doit adopter par avance les noms de champs du futur standard.

**Série suivante** : à vérifier (`SERIES_MATRIX.md` fait foi). Pièges 19.x à respecter dès l'écriture : `group_ids` et non `groups_id` sur `res.users`, `models.Constraint` et non `_sql_constraints`, et `ir.access.csv` si la cible est 19.4.

## 3. Voies possibles

| Voie | Effort | Ce que l'utilisateur obtient | Coût migration | Recommandée |
|---|---|---|---|---|
| Configuration seule | — | Rien : aucun paramètre standard connu ne bloque la confirmation d'un devis sur seuil (à confirmer §2) | nul | non |
| Studio / automatisation en base | faible | Automatisation « on write » levant une erreur + champ seuil. **Limites fermes** : pas de surcharge de `action_confirm`, donc contrôle contournable par le portail/l'API ; `safe_eval` ; pas de test Python | faible | non — la demande touche une limite ferme de Studio |
| **Module custom** | faible (1–2 j) | Surcharge de `_action_confirm`/`action_confirm` : blocage fiable quel que soit le canal, bouton « Approuver », traçabilité, tests | à chaque migration, mais surface minimale si le nommage calque le standard | **oui** |

Le dossier indique une installation acceptant les modules custom (donc pas Odoo Online). Si le briefing révèle **zéro module custom et du Studio en base**, la voie par défaut redevient Studio — et alors la limite « contournement par le portail » doit être actée comme risque résiduel assumé par le client.

**Vaut-elle son coût ?** Oui si le volume de devis au-dessus du seuil est significatif. Si c'est un cas trimestriel, un contrôle a posteriori documenté coûte moins cher. À trancher avec les volumes de la copie de base.

## 4. Contradictions et risques

| # | Sév. | Point | Pourquoi c'est un problème | Proposition |
|---|---|---|---|---|
| 1 | Haute | « Important » n'est pas défini | Seuil montant ? remise ? marge ? délai de paiement ? Un seuil sur le total ne protège pas d'une remise de 40 % sur un petit devis | Question bloquante Q1 ; concevoir le critère comme **méthode surchargeable** (`_get_approval_reason()`) pour ajouter des règles sans refonte |
| 2 | Haute | La confirmation n'est pas qu'un bouton | Portail client, signature en ligne, paiement en ligne, abonnements/renouvellements, import, API : tous appellent le même chemin serveur. Un contrôle posé sur le bouton seul est contournable | Poser le contrôle sur la **méthode serveur**, pas sur la vue ; tester explicitement le canal portail |
| 3 | Haute | Devis déjà en base au déploiement | Un blocage rétroactif fige des devis en cours ; un blocage non rétroactif laisse passer les gros devis du jour | Question bloquante Q3 ; défaut proposé : ne s'applique qu'aux devis créés après activation, ou approbation implicite des devis existants marquée en base |
| 4 | Moyenne | Modification après approbation | Un devis approuvé à 50 k€ passé à 90 k€ puis confirmé : l'approbation ne vaut plus rien | Invalider l'approbation si un élément du critère change après approbation (montant, remise, lignes) |
| 5 | Moyenne | Le vendeur peut-il approuver son propre devis ? | Si les responsables sont aussi vendeurs, l'auto-approbation vide le contrôle | Q2 ; défaut proposé : interdit, message explicite |
| 6 | Moyenne | Droits et visibilité | Le groupe « approbateur » doit-il être un nouveau groupe ou `sale.group_sale_manager` ? Le second donne beaucoup plus que l'approbation | Groupe dédié, implicant `sale.group_sale_manager` seulement si le client le confirme |
| 7 | Moyenne | Multi-devise | Un seuil en euros comparé à un devis en USD sans conversion est faux | Comparer sur le montant en devise société (champ société standard, à identifier dans les sources) |
| 8 | Basse | Multi-société | Une seule société aujourd'hui, mais le seuil doit être porté par société pour ne pas coûter cher plus tard | Paramètre par société dès le départ |
| 9 | Basse | Vues héritées / autres modules | La surcharge de la vue formulaire de `sale.order` peut entrer en conflit avec un module tiers | Vérifier après briefing les modules installés touchant `sale.order` |

## 5. Questions bloquantes

1. **Qu'est-ce qu'un devis « important » ?** Montant (HT ou TTC), remise, marge, ou combinaison ? Quel seuil chiffré ? *(Sans réponse, le critère développé peut ne rien protéger.)*
2. **Qui approuve, et le vendeur peut-il s'auto-approuver ?** Les deux responsables indifféremment ? Un seul suffit-il ? Que fait-on en cas d'absence (délégation, escalade) ?
3. **Les devis déjà créés** : soumis au contrôle, ou approuvés d'office ?
4. **Blocage dur ou avertissement ?** La confirmation est-elle impossible, ou possible avec justification tracée ?
5. **Quels canaux de confirmation sont concernés ?** Le client peut-il confirmer lui-même depuis le portail / par signature en ligne ? Si oui, le blocage y est-il souhaité (et quel message voit le client) ?

Les cinq sont posables ; la demande est cadrable. Q1 et Q5 sont les plus coûteuses si mal répondues.

## 6. Hypothèses retenues à défaut de réponse

- Critère = montant total **HT** en devise société, seuil unique paramétrable, `0` = désactivé.
- Approbateurs = groupe dédié `Approbation des devis`, les 2 responsables dedans ; auto-approbation interdite.
- Blocage **dur** : `UserError` explicite à la confirmation.
- Devis existants à l'installation : considérés approuvés (pas de blocage rétroactif), marqué en base.
- Toute modification du montant après approbation réinitialise l'approbation.
- Portail : la confirmation client est bloquée avec un message neutre (« Ce devis est en cours de validation par notre équipe »).

## 7. Spécification (sous réserve du verdict §2)

### Modèle de données — `sale.order`
- `approval_state` : sélection `not_required` / `to_approve` / `approved`, calculé-stocké, réinitialisé sur modification du critère.
- `approved_by_id` (`res.users`), `approved_on` (datetime), en lecture seule.
- Méthode `_get_approval_reason()` retournant le motif de blocage ou `False` — **point d'extension prévu** pour ajouter la règle « remise » sans refonte.
- Paramètre de seuil porté par la société et exposé dans les Paramètres de Ventes ; nommage à aligner sur celui trouvé côté `purchase` (§2).

### Comportement
- Surcharge du point d'extension serveur de la confirmation (le nom exact — `action_confirm` ou `_action_confirm` — est à lire dans `sale/models/sale_order.py` de la série, cf. §2 commande 3).
- Si approbation requise et non obtenue → erreur utilisateur nommant le motif et le seuil.
- Bouton **Approuver** visible pour le seul groupe approbateur, sur les devis `to_approve`, masqué pour le créateur du devis.
- Approbation et refus tracés dans le chatter.

### Interface
Bandeau d'état sur le devis, bouton **Approuver**, filtre « À approuver » dans la liste des devis.

### Sécurité
Nouveau groupe, règles d'accès à la série (`ir.model.access.csv` en 19.0 ; **`ir.access.csv` si la cible est 19.4**). Le bouton n'est pas la sécurité : le contrôle est côté serveur.

### Reprise de données
Script d'installation positionnant `approval_state` sur les devis existants selon la décision Q3.

### Hors périmètre
Workflow à plusieurs niveaux, délégation automatique, approbation par e-mail, contrôle sur les commandes déjà confirmées, contrôle sur les remises (tant que Q1 ne le demande pas explicitement).

## 8. Critères d'acceptation

- [ ] Étant donné un seuil à X et un devis à X−1, quand un vendeur confirme, alors la confirmation aboutit.
- [ ] Étant donné un devis à X+1, quand un vendeur confirme, alors une erreur nomme le motif et le devis reste en devis.
- [ ] Étant donné ce devis approuvé par un responsable, quand le vendeur confirme, alors la confirmation aboutit et le chatter trace l'approbateur et la date.
- [ ] Étant donné un devis approuvé dont le montant passe au-dessus du seuil après modification, quand on confirme, alors une nouvelle approbation est exigée.
- [ ] Étant donné un devis au-dessus du seuil, quand le vendeur qui l'a créé tente d'approuver, alors le bouton est indisponible.
- [ ] Étant donné un devis au-dessus du seuil non approuvé, quand le **client** confirme depuis le portail, alors la confirmation est refusée avec un message client acceptable.
- [ ] Étant donné un seuil à 0, quand on confirme n'importe quel devis, alors aucun contrôle ne s'applique.
- [ ] Étant donné un devis en devise étrangère, quand son équivalent société dépasse le seuil, alors l'approbation est exigée.
- [ ] Étant donné les devis existants avant installation, quand on confirme, alors le comportement est conforme à la décision Q3.

## 9. Estimation et découpage

1. Seuil + `approval_state` + blocage serveur + tests *(le cœur ; livrable seul)*
2. Bouton d'approbation, groupe, filtre, chatter
3. Canal portail + reprise de données

Estimation indicative 1–2 j, **à confirmer après le verdict §2** : si le standard ou l'app d'approbations couvre le besoin, elle tombe à quelques heures de configuration.

**Niveau QA : renforcé** — la demande crée un groupe de droits et touche des données existantes. Copie client obligatoire.

## 10. Ce que l'utilisateur verra

Le vendeur : un message de blocage à la confirmation d'un gros devis, et un état « En attente de validation ». Le responsable : un filtre « À approuver » et un bouton **Approuver**. Le client, si Q5 le confirme : un message d'attente sur le portail au lieu de la confirmation immédiate.

---

**Pour `PROJECT.md`** (à écrire une fois les réponses obtenues) — *Compréhension métier* : la confirmation d'un devis est le point de non-retour opérationnel chez Atelier Boréal ; deux responsables commerciaux pour N vendeurs. *Décisions actées* : à remplir après arbitrage de Q1–Q5 (seuil, approbateurs, sort des devis existants) — rien n'est acté à ce stade.