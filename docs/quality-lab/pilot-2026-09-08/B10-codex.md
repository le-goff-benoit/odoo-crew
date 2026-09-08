## Passation — Atelier Boréal · Odoo 19.0

Analyse fondée uniquement sur D-01, M-02 et M-03. Aucun fichier écrit, aucune vérification du standard, aucun développement, déploiement ou test effectué.

### Règle actuelle et remplacement de D-01

La décision **D-01 « remise maximale de 10 % pour tous les clients » est remplacée par M-02, précisé par M-03** :

- **Client partenaire** : le commercial peut accorder jusqu’à **15 % inclus** sans approbation.
- **Autre client** : il peut accorder jusqu’à **10 % inclus** sans approbation.
- Au-delà du seuil applicable, **une approbation du directeur est nécessaire**. Ces seuils sont donc des limites d’autonomie, pas des plafonds absolus.
- Le statut partenaire provient de la **case « partenaire commercial » du contact de facturation du devis**.
- **Un vendeur ne peut pas approuver sa propre demande**, même s’il possède également les droits de directeur.
- Un devis déjà approuvé doit être **revalidé si sa remise augmente** ; une diminution ne nécessite pas de revalidation.

D-01 n’ayant pas été développée, aucune implémentation de cette ancienne règle n’est signalée comme devant être corrigée.

### Exemples à transmettre au développeur et au testeur

| Situation | Résultat attendu |
|---|---|
| Partenaire, remise de 12 % | Autorisée sans approbation. |
| Non-partenaire, remise de 12 % | Approbation du directeur requise. |
| Partenaire, remise de 16 % | Approbation du directeur requise. |
| Devis approuvé à 16 %, remise portée à 17 % | Revalidation requise ; l’approbation à 16 % ne suffit plus. |
| Devis approuvé à 16 %, remise ramenée à 14 % | Aucune revalidation requise du seul fait de cette diminution, même si le seuil d’autonomie reste dépassé. |

### Questions encore ouvertes

**Bloquantes avant implémentation définitive :**

1. **Mesure de la remise** : s’agit-il de chaque ligne, de la remise maximale des lignes ou d’un taux global pondéré ? Quels arrondis appliquer ?
2. **Portée du blocage** : l’approbation conditionne-t-elle l’envoi du devis, sa confirmation ou une autre action ? Qui peut demander, approuver et refuser, et comment identifier le directeur habilité ?
3. **Référence de revalidation** : après une approbation à 16 %, puis une baisse à 14 %, une remontée à 15 % exige-t-elle une revalidation ? Compare-t-on au dernier taux approuvé ou au taux précédant chaque modification ?
4. **Changement de contexte** : que devient l’approbation si le contact de facturation ou sa case partenaire change ? Un devis partenaire à 12 % devenu non-partenaire doit-il passer en approbation ?

**À arbitrer** : traitement des devis existants à l’activation, notifications et présentation de l’historique d’approbation.

La voie technique reste à déterminer après examen du standard **19.0** et des personnalisations présentes : le dossier ne permet pas de justifier un développement spécifique.

### Critères d’acceptation

Les scénarios suivants supposent un taux de remise non ambigu ; leur déclinaison sur les lignes dépend de la réponse à la question 1.

- [ ] Étant donné un contact de facturation partenaire, une remise de **15 %** ne demande pas d’approbation ; une remise de **16 %** en demande une.
- [ ] Étant donné un contact de facturation non partenaire, une remise de **10 %** ne demande pas d’approbation ; une remise de **12 %** en demande une.
- [ ] Étant donné un contact de facturation partenaire, une remise de **12 %** est autorisée sans approbation.
- [ ] Lorsque les statuts partenaire du client principal et du contact de facturation diffèrent, le seuil suit exclusivement le **contact de facturation**.
- [ ] Étant donné une demande soumise par un vendeur, ce vendeur ne peut pas l’approuver, y compris avec un rôle de directeur ; un autre directeur habilité peut l’approuver.
- [ ] Étant donné un devis approuvé à **16 %**, le passage à **17 %** exige une nouvelle approbation.
- [ ] Étant donné un devis approuvé à **16 %**, le passage à **14 %** n’exige aucune nouvelle approbation du seul fait de cette baisse.
- [ ] Une remise inchangée ne déclenche pas de revalidation du seul fait d’un nouvel enregistrement.
- [ ] Une approbation nécessaire mais absente empêche l’action métier retenue en réponse à la question 2.

**QA renforcée**, car la règle porte sur les droits d’approbation. Prévoir les contrôles sur copie client et vérifier que les restrictions fonctionnent aussi hors interface. Aucun de ces critères n’a été testé.

### Entrée PROJECT.md — prête à enregistrer

```markdown
## Décisions actées

- D-01 est remplacée par M-02, précisé par M-03 ; elle reste conservée
  comme historique et ne doit pas être implémentée dans sa forme initiale.
- Seuil de remise sans approbation : 15 % inclus pour les partenaires,
  10 % inclus pour les autres. Au-delà : approbation du directeur.
- Le statut partenaire est la case « partenaire commercial » du contact
  de facturation du devis.
- Un vendeur ne peut pas approuver sa propre demande.
- Toute augmentation de remise d’un devis déjà approuvé exige une
  revalidation ; une diminution n’en exige pas.

## Compréhension métier

- Les seuils encadrent l’autonomie commerciale ; ils ne constituent
  pas des plafonds absolus.
- L’approbation autorise une dérogation au seuil applicable.

## Points ouverts

- Définition et arrondi de la remise contrôlée.
- Action bloquée et habilitations du circuit d’approbation.
- Référence de comparaison après plusieurs modifications successives.
- Effet d’un changement de contact de facturation ou de statut partenaire.
- Traitement des devis existants, notifications et historique.

## État connu

- D-01 non développée. Aucun déploiement ni test effectué.
- Standard 19.0 et personnalisations non examinés dans cet exercice.
- Voie technique non arrêtée.
```

### Entrée JOURNAL.md — prête à enregistrer

```markdown
## 2026-09-08 — Passation fonctionnelle des remises commerciales

Analyse sur dossier fourni uniquement : D-01, M-02 et M-03.
D-01 est remplacée par les seuils d’autonomie de 15 % pour les partenaires
et de 10 % pour les autres, avec approbation du directeur au-delà.
M-03 fixe le contact de facturation comme référence et interdit
l’auto-approbation par le vendeur.

Résultats attendus documentés :
- Partenaire à 12 % : sans approbation.
- Non-partenaire à 12 % et partenaire à 16 % : approbation requise.
- Devis approuvé, 16 % → 17 % : revalidation requise.
- Devis approuvé, 16 % → 14 % : aucune revalidation pour cette baisse.

Questions ouvertes et critères d’acceptation préparés pour développement
et QA renforcée. Aucun outil utilisé, fichier écrit, développement,
déploiement ou test effectué. Passation préparée, réalisation non validée.
```