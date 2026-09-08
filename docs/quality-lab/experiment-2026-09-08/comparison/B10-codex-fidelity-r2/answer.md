La règle actuelle est celle de **M-02, précisée par M-03**. Elle remplace D-01 ; elle n’est encore ni développée, ni testée, ni déployée. Le verdict standard Odoo 19.0 et la voie technique restent **non établis**, faute de preuves accessibles dans cet exercice.

**Passation au développeur et au testeur**

En tant que commercial, je veux connaître la limite de remise applicable au devis et obtenir l’approbation nécessaire pour la dépasser.

Les seuils sont des **limites d’autonomie commerciale**, pas des plafonds absolus :

- **Partenaire : jusqu’à 15 % inclus** sans approbation.
- **Non-partenaire : jusqu’à 10 % inclus** sans approbation.
- Au-delà du seuil applicable : approbation du directeur.
- « Partenaire » signifie que la case « partenaire commercial » est cochée sur **le contact de facturation du devis**.
- Un vendeur ne peut pas approuver sa propre demande, même s’il possède également les droits de directeur.
- Sur un devis déjà approuvé, une augmentation de remise impose une revalidation ; une diminution n’en impose pas. Aucun retour sous le seuil n’est donné comme exception à la règle d’augmentation.

**D-01 est remplacée**, et non simplement complétée : le plafond uniforme de 10 % devient un dispositif à deux seuils avec possibilité de dépassement approuvé. Il ne faut pas présenter cette correction comme la modification d’une fonctionnalité existante : D-01 n’avait pas été développée.

Pour les exemples suivants, le pourcentage est supposé représenter la remise métier à contrôler ; sa définition technique reste à arbitrer.

| Cas | Résultat attendu |
|---|---|
| Partenaire à 12 %, sans approbation préalable | Aucune approbation requise. |
| Non-partenaire à 12 %, sans approbation préalable | Approbation du directeur requise. |
| Partenaire à 16 %, sans approbation préalable | Approbation du directeur requise. |
| Devis approuvé à 16 %, augmenté à 17 % | Revalidation requise : l’approbation précédente ne couvre pas l’augmentation. |
| Devis approuvé à 16 %, diminué à 14 % | Aucune revalidation requise, même pour un non-partenaire. |

**Questions bloquantes**

1. Quelle remise contrôle-t-on : chaque ligne, une remise globale, un taux pondéré ? Comment traiter les cumuls et les arrondis ?
2. Quelle opération exige une approbation valide : envoi au client, signature, confirmation du devis ou autre étape ?
3. Après plusieurs modifications, compare-t-on au dernier taux approuvé ou au taux immédiatement précédent ? Exemple : **16 % approuvé → 14 % → 15 %**.
4. Quels utilisateurs sont habilités comme directeurs et qui approuve lorsqu’un vendeur est lui-même directeur ?
5. Quel effet ont un changement de contact de facturation ou de sa case partenaire sur un devis existant, notamment déjà approuvé ?

Ces questions restent ouvertes. Le silence ne valide aucune hypothèse. Le champ technique correspondant à la case, les personnalisations existantes et les mécanismes standard doivent également être identifiés avant de choisir configuration, Studio ou module.

**Périmètre de spécification établi**

La solution devra déterminer la catégorie à partir du contact de facturation, appliquer le seuil correspondant et contrôler l’identité de l’approbateur. L’interdiction d’auto-approbation devra être effective sur les opérations concernées, et pas seulement masquer un bouton.

Le workflow, les champs techniques, les messages et la reprise des devis existants ne sont pas encore spécifiés. En particulier, **aucune approbation historique ne peut être déduite de D-01**, puisqu’elle n’a jamais été développée. Le traitement des devis ouverts à la mise en service devra être cadré après inventaire.

**Critères d’acceptation métier**

Ces critères sont établis ; leur traduction en scénarios techniques dépend des réponses ci-dessus.

- [ ] Un partenaire à 15 % et un non-partenaire à 10 % ne nécessitent pas d’approbation.
- [ ] Un dépassement du seuil applicable nécessite l’approbation du directeur.
- [ ] Les cinq exemples du tableau produisent exactement les résultats indiqués.
- [ ] Lorsque le contact commercial principal et le contact de facturation ont des cases partenaire différentes, la catégorie retenue est celle du contact de facturation.
- [ ] Un utilisateur sans habilitation de directeur ne peut pas donner l’approbation requise.
- [ ] Un vendeur, même habilité comme directeur, ne peut pas approuver sa propre demande.
- [ ] L’augmentation directe d’une remise approuvée exige une revalidation, y compris lorsqu’elle reste sous le seuil d’autonomie.
- [ ] La diminution directe d’une remise approuvée n’exige pas de revalidation.

**QA renforcée**, car les droits et les devis existants sont concernés. Prévoir une copie client pour la validation de l’intégration et de la reprise. Aucun test n’a été exécuté. Le chiffrage attend les arbitrages et l’inventaire ; les règles et scénarios ci-dessus peuvent déjà être revus indépendamment.

Entrée **PROJECT.md** proposée, prête à enregistrer :

```markdown
## Compréhension métier
- Atelier Boréal — Odoo 19.0.
- Le statut partenaire dépend de la case « partenaire commercial » du
  contact de facturation du devis (M-03).
- Les seuils limitent l’autonomie du commercial ; leur dépassement
  reste possible avec approbation du directeur (M-02).

## Décisions actées
- D-01, maximum uniforme de 10 %, est remplacée par M-02, précisée
  par M-03. D-01 n’avait pas été développée.
- Seuil sans approbation : partenaire 15 % inclus ; autres 10 % inclus.
  Au-delà : approbation du directeur (M-02).
- Devis approuvé : augmentation de remise = revalidation ;
  diminution = aucune revalidation (M-02).
- Un vendeur ne peut pas approuver sa propre demande (M-03).

## Questions ouvertes
- Définition et précision de la remise contrôlée.
- Étape du devis conditionnée par l’approbation.
- Référence de comparaison après modifications successives.
- Habilitations des directeurs et approbateur alternatif.
- Effet des changements de contact de facturation ou de statut partenaire.

## Propositions non actées
- Cadrer la reprise des devis ouverts après inventaire.
- Aucun choix technique arrêté ; couverture standard non établie.

## État réel de réalisation
- Passation préparée sur dossier synthétique uniquement.
- Aucun développement, test ou déploiement réalisé.
- Aucune inspection des sources ou de la base effectuée.
```

Entrée **JOURNAL.md** proposée, prête à enregistrer :

```markdown
## 2026-09-08 — Passation fonctionnelle des remises
- Sources : D-01, correction client M-02, précision humaine M-03.
- Correction intégrée : remplacement du seuil uniforme par 15 % pour
  les partenaires et 10 % pour les autres, avec approbation au-delà.
- Revalidation à l’augmentation et interdiction d’auto-approbation
  intégrées à la passation.
- Exemples 12 %, 16 %, 16 → 17 % et 16 → 14 % explicités.
- Cinq questions bloquantes recensées ; critères métier préparés.
- Verdict standard et voie technique non établis.
- Réalisation : analyse uniquement, sans outils ; aucun fichier écrit,
  aucun développement, test ou déploiement effectué.
```