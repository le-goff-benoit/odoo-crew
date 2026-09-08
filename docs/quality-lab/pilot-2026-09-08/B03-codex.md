# Revue fonctionnelle — Validation des devis importants

**Projet** Atelier Boréal · **Série** 19.0 · **Périmètre** devis et confirmation commerciale.

Analyse limitée au dossier : aucun fichier écrit, aucune source ni base consultée, aucun test exécuté. La revue est donc restituée ici.

## 1. Ce que je comprends

« En tant que responsable commercial, je veux approuver les devis engageant fortement l’entreprise afin de contrôler ces engagements avant leur confirmation et le déclenchement des opérations aval. »

**Problème réel présumé** : éviter qu’un vendeur engage seul l’entreprise au-delà de limites acceptables. Le dossier ne décrit ni incident, ni fréquence, ni volume, ni coût actuel. La validation est la solution demandée ; ses règles métier restent à définir.

## 2. Verdict standard Odoo 19.0

**Non établi sur les pièces fournies.** Sans sources ni inventaire de base, aucun verdict « ÇA EXISTE », « PARTIEL » ou « À DÉVELOPPER » ne serait étayé. Aucun chemin de preuve ne peut être cité.

Vérifications à prévoir :

- Dans les sources 19.0 : rechercher une couverture du besoin dans les modules installables concernés et identifier le mécanisme effectif de confirmation.
- Dans la base et les modules du projet : rechercher validations, champs Studio, automatisations, droits et personnalisations existants. « Aucun mécanisme décrit » ne signifie pas « aucun mécanisme présent ».
- Dans la série suivante disponible, 19.1 : rechercher une couverture nouvelle et ses conséquences sur la migration et le modèle de données.

## 3. Voies possibles

| Voie | Effort indicatif | Résultat et limites | Coût à la migration |
|---|---|---|---|
| Configuration standard | Faible si couverture complète | À privilégier si elle garantit le contrôle avant toute confirmation | Faible, avec recette |
| Studio / configuration en base | Faible à moyen | Écran et suivi possibles à vérifier ; un bouton masqué ne garantit pas le blocage de tous les canaux | Revalidation des règles et vues |
| Module custom | Moyen, selon règles et existant | Extension ciblée si le contrôle nécessaire manque réellement | Maintenance du contrôle et des tests |

**Recommandation** : rechercher d’abord une couverture standard complète. Si elle manque, retenir la solution qui garantit le blocage côté serveur. Un module devient pertinent si une surcharge de méthode est nécessaire ; le simple fait que l’installation accepte des modules ne justifie pas son développement.

## 4. Contradictions et risques

| # | Sévérité | Point | Proposition |
|---|---|---|---|
| 1 | P1 | « Important » n’est pas défini : impossible de déterminer quels devis bloquer. | Faire approuver une règle calculable et ses bornes. |
| 2 | P1 | La confirmation déclenche déjà l’aval : une approbation après confirmation arrive trop tard. | Contrôler avant tout effet aval, quel que soit le canal. |
| 3 | P1 | Un devis approuvé puis modifié peut engager davantage que ce qui a été autorisé. | Lier l’approbation au contenu examiné et définir son invalidation. |
| 4 | P1 | Le traitement des devis existants peut soit bloquer l’activité, soit laisser passer des engagements non contrôlés. | Décider explicitement du périmètre de bascule. |
| 5 | P2 | Les canaux de confirmation et personnalisations ne sont pas inventoriés. | Examiner interface, portail/signature/paiement si activés, API et automatisations. |

## 5. Questions réellement bloquantes

1. **Déclenchement** : qu’est-ce qu’un devis important — montant HT ou TTC, seuil et égalité au seuil, remises par ligne ou globales, combinaison des conditions ? Si plusieurs devises sont utilisées, quelle conversion retenir ?
2. **Autorité** : l’accord d’un seul des deux responsables suffit-il ? Un responsable peut-il approuver son propre devis ? Qui peut ensuite confirmer ?
3. **Modifications** : quels changements après approbation imposent une nouvelle validation, notamment prix, quantité, remise, client et conditions de paiement ?
4. **Confirmation** : quels canaux sont réellement utilisés, et quel comportement attendre lorsque le client signe ou paie avant l’approbation interne ?
5. **Bascule** : les devis déjà créés et encore non confirmés sont-ils soumis à la règle dès son activation ?

Ces réponses conditionnent la spécification définitive. Aucun seuil ni accord implicite ne peut les remplacer.

## 6. Hypothèses proposées, à arbitrer

- L’approbation autorise une confirmation ultérieure ; elle ne confirme pas automatiquement.
- Aucun délai écoulé ne vaut approbation.
- Un refus laisse le devis modifiable et permet une nouvelle soumission.
- Aucun devis déjà confirmé n’est annulé ou rejoué par cette évolution.
- Le périmètre initial reste celui d’une seule société.

## 7. Spécification déjà cadrable

**Modèle de données.** Réutiliser les objets existants avant d’ajouter des champs. Le dispositif doit pouvoir représenter : validation non requise, requise, en attente, approuvée et refusée. Il doit conserver l’auteur, la date et le résultat de la décision, ainsi que le contenu ou la révision auxquels elle s’applique. Les noms techniques dépendront des vérifications du standard.

**Comportement.**

- Déterminer si une validation est nécessaire à partir du contenu courant du devis.
- Soumettre le devis à un responsable autorisé.
- Avant chaque confirmation, recalculer son éligibilité et vérifier l’existence d’une approbation encore valable.
- Bloquer toute confirmation soumise à validation sans approbation valable, avant tout effet aval.
- Invalider l’approbation lors des modifications définies par l’arbitrage métier.
- Empêcher qu’une modification concurrente permette de confirmer un contenu différent de celui approuvé.

**Interface.** Afficher le statut, le motif de validation et la dernière décision. Présenter les actions de soumission, d’approbation et de refus selon les droits. Le message de blocage doit expliquer l’action attendue.

**Sécurité.** Contrôler les droits côté serveur. Une écriture directe, un import ou un appel API ne doit pas permettre à un vendeur de fabriquer une approbation. La visibilité des informations internes sur le portail doit être vérifiée.

**Reprise de données.** Recenser les devis ouverts, leurs états et les volumes concernés ; simuler leur classement selon la règle retenue. Ne créer aucune approbation rétroactive sans décision explicite.

**Hors périmètre proposé.** Validation des commandes déjà confirmées, circuits à plusieurs niveaux et changements des opérations aval.

## 8. Critères d’acceptation

À décliner avec les seuils et droits arbitrés :

- [ ] Un devis non soumis à validation conserve son parcours de confirmation.
- [ ] Les cas juste sous le seuil, au seuil et juste au-dessus produisent le résultat convenu ; les règles de remise sont également couvertes.
- [ ] Un devis soumis à validation, sans accord valable, ne peut être confirmé par aucun canal actif ; aucune opération aval n’est créée.
- [ ] Un responsable habilité peut approuver ; un vendeur ne peut pas contourner ce droit par écriture directe.
- [ ] L’approbation seule ne déclenche pas l’aval ; la confirmation autorisée conserve les effets actuels.
- [ ] Une modification nécessitant une nouvelle validation rend l’accord précédent inutilisable.
- [ ] Un refus bloque la confirmation et permet une nouvelle soumission selon le parcours retenu.
- [ ] Une modification concurrente à l’approbation ou à la confirmation ne contourne pas le contrôle.
- [ ] Les devis antérieurs à la bascule suivent exactement la politique décidée.

## 9. Estimation et découpage

1. Vérifier le standard, l’existant et les canaux actifs ; obtenir les cinq arbitrages.
2. Livrer le contrôle minimal complet : éligibilité, décision, droits, blocage et invalidation.
3. Préparer la bascule des devis ouverts et réaliser la recette sur copie client.

**Chiffrage fiable impossible à ce stade. Niveau QA renforcé**, compte tenu des droits, des données existantes et des effets de la confirmation. Une copie client sera nécessaire pour cette recette ; elle n’est pas disponible dans l’exercice.

## 10. Ce que l’utilisateur verra

Le vendeur verra quels devis nécessitent un accord, leur statut et la raison d’un blocage. Les responsables disposeront d’une liste des demandes et des actions de décision. La confirmation restera une action distincte, sous réserve de validation de cette hypothèse.

**À consigner ultérieurement dans `PROJECT.md`** : le contrôle doit précéder les opérations aval. Les seuils, droits, règles d’invalidation et modalités de bascule restent des décisions attendues, pas des décisions actées.