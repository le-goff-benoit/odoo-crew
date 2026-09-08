**La règle actuelle remplace D-01 : le plafond sans approbation devient 15 % pour les partenaires et reste 10 % pour les autres clients.** Cette passation repose uniquement sur le dossier fourni ; aucun fichier, test ou déploiement n’a été réalisé.

### Règle à transmettre au développeur

- Le statut partenaire est déterminé par la case « partenaire commercial » du **contact de facturation du devis**, conformément à M-03.
- Une remise **inférieure ou égale** au plafond applicable ne nécessite pas d’approbation.
- Au-delà du plafond, l’approbation du directeur est obligatoire.
- Un vendeur ne peut pas approuver sa propre demande, y compris s’il dispose également du rôle directeur.
- Pour un devis déjà approuvé, une augmentation de remise impose une revalidation ; une diminution n’en impose pas. Une remise inchangée ne déclenche pas de revalidation au titre de cette règle.

**Décision remplacée :** D-01, « remise maximale de 10 % pour tous les clients », est supplantée par M-02, précisé par M-03. Il s’agit désormais de **plafonds sans approbation**, et non de maxima absolus. D-01 n’ayant pas été développée, aucune migration d’une implémentation de cette décision n’est identifiée dans le dossier.

### Résultat des exemples

Pour les trois premiers cas, on suppose qu’aucune approbation préalable ne couvre la remise.

| Cas | Résultat attendu |
|---|---|
| Partenaire à 12 % | Pas d’approbation nécessaire : 12 % ≤ 15 %. |
| Non-partenaire à 12 % | Approbation du directeur nécessaire : 12 % > 10 %. |
| Partenaire à 16 % | Approbation du directeur nécessaire : 16 % > 15 %. |
| Devis approuvé à 16 %, puis porté à 17 % | Revalidation obligatoire ; l’approbation précédente ne suffit plus. |
| Devis approuvé à 16 %, puis réduit à 14 % | Pas de revalidation. Cela vaut aussi pour un non-partenaire : la diminution bénéficie de l’approbation déjà obtenue à 16 %. |

### Questions encore ouvertes

Ces questions bloquent la finalisation technique ; elles ne remettent pas en cause les résultats ci-dessus.

1. **Mesure de la remise :** contrôle par ligne, remise globale ou taux effectif du devis ? Comment traiter plusieurs remises, les arrondis et leur précision ?
2. **Action à bloquer :** sans approbation valide, faut-il empêcher l’envoi, la confirmation du devis, ou les deux ? La sauvegarde d’un brouillon doit-elle rester possible ?
3. **Donnée partenaire :** quel est le champ technique correspondant à la case et existe-t-il déjà en base ? Que faire si le contact de facturation ou sa case change après une demande ou une approbation ?
4. **Référence de revalidation :** après une approbation à 16 %, une baisse à 14 %, puis une hausse à 15 %, faut-il revalider parce que la dernière remise augmente, ou conserver l’approbation tant que les 16 % approuvés ne sont pas dépassés ?
5. **Habilitations :** qui possède le pouvoir d’approbation du directeur et qui approuve lorsque ce directeur est lui-même demandeur ? Aucun contournement de l’interdiction d’auto-approbation ne doit être implicite.

**Voie technique à déterminer :** le dossier ne contient aucune preuve sur les capacités standard d’Odoo 19.0, de la série suivante, ni sur les personnalisations installées. Il ne permet donc pas de conclure « à développer ». Vérifier leur couverture avant de choisir configuration, Studio ou module.

### Critères d’acceptation pour le testeur

Les contrôles de blocage ci-dessous s’appliqueront à l’action retenue en réponse à la question 2.

- [ ] Un partenaire à **15 % exactement** et un non-partenaire à **10 % exactement** passent sans approbation.
- [ ] Un dépassement de chacun de ces seuils, à la précision retenue, exige une approbation.
- [ ] Les cinq exemples du tableau produisent les résultats annoncés.
- [ ] Si le contact principal et le contact de facturation ont des cases différentes, seule celle du **contact de facturation** détermine le plafond.
- [ ] Pour une demande dépassant le plafond, l’action contrôlée reste bloquée tant qu’un directeur autorisé, distinct du demandeur, n’a pas approuvé.
- [ ] Un vendeur ne peut pas approuver sa propre demande, même avec le rôle directeur ; un utilisateur non habilité ne peut pas approuver.
- [ ] Après approbation à 16 %, une modification à 17 % rend une nouvelle approbation nécessaire ; une sauvegarde à 16 % ne la réclame pas.
- [ ] Après approbation à 16 %, une baisse à 14 % conserve le bénéfice de l’approbation, même si le plafond courant est 10 %.
- [ ] Le blocage et les droits restent effectifs par les autres voies d’écriture disponibles, notamment import et API.

**QA renforcée**, car la règle porte sur les droits et les remises commerciales. Les scénarios liés aux changements de contact, aux variations successives et aux devis existants devront être complétés après arbitrage. Aucun résultat de test n’est acquis.

### Entrée PROJECT.md prête à enregistrer

```markdown
## Compréhension métier
- Atelier Boréal — Odoo 19.0.
- Les plafonds de remise sans approbation sont différenciés selon le
  statut partenaire du contact de facturation du devis.
- Une approbation obtenue reste suffisante en cas de diminution de remise.

## Décisions actées
- D-01 (« remise maximale de 10 % pour tous les clients ») est remplacée
  par M-02, précisé par M-03 : plafond sans approbation de 15 % pour
  les partenaires et de 10 % pour les autres ; au-delà, accord du directeur.
- Partenaire = case « partenaire commercial » cochée sur le contact
  de facturation du devis.
- Un vendeur ne peut pas approuver sa propre demande.
- Un devis approuvé doit être revalidé si sa remise augmente,
  mais pas si elle diminue.

## Points ouverts
- Définition et précision de la remise contrôlée.
- Action bloquée en attente d’approbation.
- Champ partenaire existant et effet d’un changement de contact/statut.
- Référence de comparaison après plusieurs variations de remise.
- Habilitations du directeur et circuit sans auto-approbation.
- Couverture standard et personnalisations existantes à vérifier.

## État connu
- D-01 n’a pas été développée.
- Aucun déploiement ni test n’a eu lieu.
- Voie technique non arrêtée.
```

### Entrée JOURNAL.md prête à enregistrer

```markdown
## Passation fonctionnelle — Remises commerciales
- Sources : décision initiale D-01, correction client M-02,
  précision humaine M-03.
- D-01 supplantée : 15 % sans approbation pour les partenaires,
  10 % pour les autres ; dépassement soumis au directeur.
- Statut partenaire porté par le contact de facturation.
- Auto-approbation interdite ; hausse après approbation à revalider,
  baisse sans revalidation.
- Exemples et critères d’acceptation préparés pour développement et QA.
- Questions ouvertes consignées dans l’entrée PROJECT.md proposée.
- Analyse synthétique sur dossier, sans outils : aucune consultation
  de sources ou de base, aucune écriture, aucun test ni déploiement.
- Prochaine étape : arbitrer les points ouverts, vérifier l’existant,
  puis choisir et spécifier la solution technique.
```