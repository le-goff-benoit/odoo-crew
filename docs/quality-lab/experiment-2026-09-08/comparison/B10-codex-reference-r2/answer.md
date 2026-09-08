**Passation — Atelier Boréal, Odoo 19.0**

Analyse fondée uniquement sur D-01, M-02 et M-03. Aucun fichier, source Odoo ou contenu de base n’a été consulté ; aucun développement, déploiement ou test n’a été réalisé. La couverture standard et la voie technique restent à vérifier.

**Règle actuelle et remplacement de D-01**

En tant que commercial, je veux soumettre à un directeur les remises dépassant mon seuil autorisé, afin de faire valider les exceptions commerciales.

D-01 (« remise maximale de 10 % pour tous les clients »), jamais développée, est **remplacée par M-02, précisé par M-03** :

- Le statut partenaire vient de la case **« partenaire commercial » du contact de facturation du devis**.
- Sans approbation, la remise peut atteindre **15 % inclus pour un partenaire**, **10 % inclus pour les autres**.
- Au-delà, l’approbation d’un directeur est obligatoire : ces seuils ne sont donc pas des plafonds absolus.
- Un vendeur ne peut pas approuver sa propre demande, même s’il dispose aussi de droits de directeur.
- Toute augmentation de remise d’un devis déjà approuvé exige une nouvelle validation. Une diminution n’en exige pas.

La fréquence du besoin, les volumes et le coût actuel ne sont pas documentés.

**Cas à transmettre au développeur et au testeur**

| Situation | Résultat attendu |
|---|---|
| Partenaire à 12 % | Autorisé sans approbation |
| Non-partenaire à 12 % | Approbation d’un directeur requise |
| Partenaire à 16 % | Approbation d’un directeur requise |
| Devis approuvé à 16 %, puis porté à 17 % | Nouvelle validation obligatoire ; l’approbation précédente ne couvre pas 17 % |
| Devis approuvé à 16 %, puis abaissé à 14 % | Aucune nouvelle validation, y compris pour un non-partenaire |

**Questions encore ouvertes — bloquantes pour finaliser la spécification**

1. **Mesure de la remise :** contrôle par ligne, remise globale ou remise effective pondérée ? Comment traiter les devis mêlant plusieurs taux et les réductions intégrées aux prix ?
2. **Étape bloquée :** sans approbation valide, faut-il empêcher l’envoi, la confirmation du devis ou une autre action ? La sauvegarde d’un brouillon reste-t-elle permise ?
3. **Habilitations :** quels utilisateurs sont directeurs approbateurs, sur quelles sociétés, et qui approuve lorsque le vendeur est lui-même directeur ?
4. **Référence d’augmentation :** après approbation à 16 %, diminution à 14 %, puis remontée à 15 %, faut-il revalider ? Il faut choisir entre comparaison avec la dernière remise enregistrée et comparaison avec la remise approuvée.
5. **Changement de statut :** que devient une approbation ou une autorisation lorsque le contact de facturation change, ou lorsque sa case partenaire est modifiée ?

Ces réponses ne doivent pas être remplacées par des hypothèses silencieuses.

**Critères d’acceptation**

Les scénarios de taux ci-dessous supposent une mesure de remise convenue.

- [ ] Avec une remise de 10 %, un non-partenaire ne nécessite aucune approbation ; au-dessus de 10 %, il en nécessite une.
- [ ] Avec une remise de 15 %, un partenaire ne nécessite aucune approbation ; au-dessus de 15 %, il en nécessite une.
- [ ] Si les contacts de commande et de facturation ont des statuts différents, seul celui du contact de facturation détermine le seuil.
- [ ] Les cinq exemples du tableau donnent exactement les résultats indiqués.
- [ ] Un vendeur tentant d’approuver sa propre demande est refusé, même s’il est directeur.
- [ ] Un utilisateur sans habilitation de directeur ne peut pas approuver ; un directeur habilité distinct du demandeur peut approuver.
- [ ] Après passage de 16 % approuvé à 17 %, l’action métier à définir reste bloquée jusqu’à une nouvelle approbation valide.
- [ ] Après passage de 16 % approuvé à 14 %, aucune nouvelle approbation n’est demandée.
- [ ] Les contrôles s’appliquent aussi aux modifications hors formulaire, notamment par import ou API.
- [ ] Après arbitrage, les scénarios « 16 → 14 → 15 » et changement de contact/statut sont ajoutés à la recette.

**Préconisations à confirmer :** conserver une trace de l’approbateur, de la date et de la remise approuvée ; identifier le champ existant avant d’en créer un ; définir le traitement des devis existants sans leur attribuer d’approbation fictive. QA **renforcée**, portant sur les droits et les données existantes, avec copie client. Aucun résultat de recette n’est acquis.

Entrées proposées, **prêtes à enregistrer mais non écrites** :

```markdown
## Compréhension métier
- Les seuils de remise sans approbation dépendent du contact de
  facturation du devis : 15 % si « partenaire commercial » est coché,
  10 % sinon. Les dépassements restent possibles après approbation.

## Décisions actées
- D-01 — REMPLACÉE : maximum de 10 % pour tous les clients.
  Cette décision n’avait pas été développée.
- D-02 — Règle métier actuelle, issue de M-02 et M-03 :
  seuils inclusifs de 15 % pour les partenaires et 10 % sinon ;
  dépassement soumis à un directeur ; aucune auto-approbation
  par le vendeur ; nouvelle validation si la remise d’un devis
  approuvé augmente, aucune si elle diminue.
  Partenaire = case du contact de facturation du devis.

## Points ouverts
- Mesure de la remise ; action bloquée ; habilitations des directeurs ;
  référence après diminution puis augmentation ; effet des changements
  de contact de facturation ou de statut partenaire.
- Couverture standard, existant en base et reprise des devis à vérifier.
```

```markdown
## 2026-09-08 — Passation fonctionnelle des remises
- Dossier analysé : D-01, correction client M-02, précision humaine M-03.
- D-01 identifiée comme remplacée par la règle métier D-02 proposée
  pour consignation dans PROJECT.md.
- Cas attendus : partenaire 12 % sans approbation ; non-partenaire
  12 % et partenaire 16 % avec approbation ; 16 % approuvé → 17 %
  avec revalidation ; 16 % approuvé → 14 % sans revalidation.
- Cinq questions bloquantes recensées ; critères de recette préparés.
- Statut : analyse sur dossier uniquement. Aucun fichier écrit,
  aucune vérification des sources ou de la base, aucun développement,
  déploiement ou test exécuté. Validation technique et QA à réaliser.
```