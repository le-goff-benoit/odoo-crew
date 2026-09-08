La règle actuelle résulte de **M-02, précisé par M-03**. Elle remplace D-01 comme règle métier ; D-01 n’ayant jamais été développée, aucune correction d’implémentation n’est attestée.

**Règle à transmettre**

- Est partenaire un client dont la case « partenaire commercial » est cochée sur le **contact de facturation du devis**.
- Sans approbation, le commercial peut accorder jusqu’à **15 % inclus** à un partenaire et **10 % inclus** aux autres clients.
- Au-delà du seuil applicable, une approbation du directeur est nécessaire.
- Un vendeur ne peut pas approuver sa propre demande, même s’il possède également des droits de direction.
- Un devis déjà approuvé doit être revalidé lorsque sa remise augmente ; une diminution ne nécessite pas de revalidation. Cette règle de revalidation ne comporte pas d’exception liée au seuil.

**Verdict standard et voie technique : non établis**, faute de preuves accessibles sur Odoo 19.0 et sur la configuration du projet. Il faut vérifier l’existant avant de choisir configuration, Studio ou module. Aucun fichier, contrôle, test ou déploiement n’a été réalisé dans cet exercice.

**Exemples attendus**

Pour les trois premiers exemples, on considère un devis sans approbation antérieure.

| Situation | Résultat attendu |
|---|---|
| Partenaire à 12 % | Pas d’approbation nécessaire au titre du seuil. |
| Non-partenaire à 12 % | Approbation du directeur nécessaire. |
| Partenaire à 16 % | Approbation du directeur nécessaire. |
| Devis approuvé à 16 %, passage direct à 17 % | Revalidation nécessaire. |
| Devis approuvé à 16 %, passage direct à 14 % | Pas de revalidation nécessaire, même si 14 % reste au-dessus du seuil applicable. |

**Questions bloquantes pour finaliser l’implémentation**

1. Que désigne la « remise du devis » : chaque remise de ligne, une remise globale ou un taux calculé sur l’ensemble ? Quelle précision et quel arrondi déterminent le dépassement ?
2. Quelle opération l’absence d’approbation doit-elle empêcher : envoi du devis, signature, confirmation ou autre étape ? Quels états du devis sont concernés ?
3. Qui peut agir comme directeur et qui approuve lorsque le vendeur demandeur est lui-même directeur ?
4. Après une baisse puis une hausse, quelle valeur sert de référence ? Par exemple, pour **16 % approuvé → 14 % → 15 %**, faut-il revalider ? Que devient également une approbation si le contact de facturation ou sa case partenaire change ?

Ces réponses restent ouvertes. Aucune hypothèse ne doit devenir une décision par défaut. Elles conditionnent le calcul, le point de blocage et certains scénarios de revalidation ; les règles explicites ci-dessus peuvent déjà servir de référence fonctionnelle.

**Critères d’acceptation**

Les taux ci-dessous désignent la remise métier ; leur traduction en données Odoo dépend de la réponse à la question 1.

- [ ] Un partenaire à 15 % et un non-partenaire à 10 % ne nécessitent pas d’approbation au titre du seuil.
- [ ] Le premier taux représentable supérieur au seuil applicable nécessite une approbation du directeur.
- [ ] Les cinq exemples du tableau donnent les résultats indiqués.
- [ ] Lorsque les contacts du devis ont des cases partenaire différentes, c’est exclusivement celle du contact de facturation qui détermine le seuil.
- [ ] Un vendeur ne peut pas approuver sa propre demande, y compris s’il dispose du rôle directeur et tente l’action par un autre accès que le bouton de l’interface.
- [ ] L’approbation d’une autre personne habilitée comme directeur satisfait l’exigence d’approbation pour la remise soumise.
- [ ] Une augmentation directe de la remise d’un devis approuvé exige une nouvelle validation, y compris si le nouveau taux reste sous le seuil.
- [ ] Une diminution directe de cette remise ne déclenche pas de revalidation.

Les critères sur l’opération effectivement bloquée, les changements de contact et les baisses suivies de hausses seront complétés après arbitrage. **QA renforcée pour les droits**, avec copie client avant validation de livraison ; aucun résultat de test n’est disponible.

Entrée **PROJECT.md** prête à enregistrer :

```markdown
## Compréhension métier

Atelier Boréal — Odoo 19.0.
Le plafond de remise sans approbation dépend du statut partenaire du
contact de facturation du devis. Une approbation doit être renouvelée
lorsque la remise d’un devis approuvé augmente, mais pas lorsqu’elle diminue.

## Décisions actées et provenance

- D-01 — REMPLACÉE par D-02 et D-03.
  Ancienne règle : remise commerciale maximale de 10 % pour tous les clients.
  État connu : jamais développée.

- D-02 — Source : message client M-02.
  Plafond sans approbation : 15 % inclus pour les partenaires,
  10 % inclus pour les autres clients.
  Au-delà : approbation du directeur.
  Devis déjà approuvé : revalidation en cas d’augmentation de remise,
  aucune revalidation en cas de diminution.

- D-03 — Source : réponse humaine M-03.
  Partenaire = case « partenaire commercial » cochée sur le contact
  de facturation du devis.
  Un vendeur ne peut pas approuver sa propre demande.

## Questions ouvertes

- Définition, calcul et précision de la remise contrôlée.
- Opération bloquée sans approbation et états concernés.
- Habilitation du directeur et suppléance en cas d’auto-approbation.
- Référence après baisse puis hausse ; effet d’un changement du contact
  de facturation ou de son statut partenaire sur l’approbation.

## Propositions non actées

Vérifier le standard Odoo 19.0 et la configuration existante avant de
choisir la voie technique. Prévoir une QA renforcée sur les droits.
Aucune réponse aux questions ouvertes n’est présumée.

## État réel de réalisation

Passation préparée sur dossier synthétique uniquement.
Aucune implémentation des nouvelles règles n’est attestée.
Aucun accès aux sources ou à la base, aucun test ni déploiement.
Verdict standard et voie technique non établis.
```

Entrée **JOURNAL.md** prête à enregistrer :

```markdown
## 2026-09-08 — Passation fonctionnelle des règles de remise

Sources : mémoire initiale D-01, message client M-02, réponse humaine M-03.

D-01 est remplacée fonctionnellement par D-02 et D-03 :
seuils sans approbation de 15 % pour les partenaires et 10 % pour les
autres ; approbation du directeur au-delà ; revalidation après hausse
d’une remise approuvée, sans revalidation après baisse.
Le statut partenaire provient du contact de facturation.
L’auto-approbation du vendeur est interdite.

Passation préparée avec exemples et critères d’acceptation.
Restent ouverts : mesure de la remise, opération bloquée, habilitations
et suppléance, référence après baisse puis hausse et changements de statut.

Aucune décision technique prise, aucun fichier écrit, aucune opération
sur les sources ou la base, aucun test ni déploiement réalisé.
Prochaine étape proposée : arbitrer ces questions et vérifier l’existant
avant de finaliser la spécification technique et la recette.
```