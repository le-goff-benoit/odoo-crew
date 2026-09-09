# Qualification autonome du dispositif Odoo

Autorisation utilisateur : exécuter le plan de qualification de manière autonome
le 9 septembre 2026. Référence initiale : `152aa737c7efc14cdba5c36b2e614ecb2715adb4`.
Les améliorations précédentes restent des preuves locales ; cette campagne
qualifie des parcours et précise les limites d'usage, sans note globale artificielle.

## Résultat attendu

Une version installée et publiée, accompagnée d'une matrice d'usage : scénarios
qualifiés, défauts restants, supervision nécessaire, durées/coûts observés et
dimensions non mesurées. Un contrôle obligatoire absent ne vaut jamais réussite.

| Jalon | Critère de sortie | État final |
|---|---|---|
| Q0 — Contrat de qualification | Cas, oracles, budgets, critères et référence fixés avant essais | Terminé |
| Q1 — Verdict et provenance | Rapport cohérent avec la réception ; aucune identité de build inventée dans la synthèse contrôlée ; positif et négatif inédits | Terminé : rendu qualifié, récits libres imparfaits |
| Q2 — Droits réels | Utilisateur ordinaire, deux sociétés, refus ORM/RPC et postconditions ; témoin valide et mutant détecté | Terminé : témoin et mutant conformes |
| Q3 — Restauration réelle | ZIP + filestore récupérés, neutralisation vérifiée, erreurs bloquantes, voisin synthétique intact | Terminé : trois scénarios conformes |
| Q4 — Versions et navigateur | Au moins 18.0 et 19.0 réellement exécutées si équipées ; action navigateur synthétique vérifiée | Terminé : ORM 18/19, Chrome19 et mutant, incident conservé |
| Q5 — Chaînes complètes | Développement/QA/journal avec critères et RPC ; délégation réelle, reprise vérifiée ; décisions et code préservés | Exécuté : résultats techniques acquis, qualification globale partielle |
| Q6 — Autonomie et coût | Réceptions exactes, interventions comptées, durées/coûts décrits ; comparaison séquentiel/parallèle avec répétitions si budget disponible | Terminé :10appels, coûts descriptifs, aucun gain causal |
| Q7 — Livraison | Tests/lint/build/parité, preuves et journal, publication/CI, mémoire ; limites explicites | Contrôles locaux verts ; livraison et CI suivies dans le bilan |

## Règles de mesure

- Mesurer séparément compréhension/contrat, code et données, verdict/provenance,
  mémoire/reprise, interventions humaines, temps et coût.
- Zéro faux succès sur les critères obligatoires des cas qualifiés. Un mutant
  critique accepté invalide la qualification de la dimension concernée.
- Un essai arrêté par le fournisseur ou le banc reste un incident ; conserver
  la réponse originale et autoriser seulement une reprise explicite bornée.
- Cas entièrement synthétiques, sources Odoo en lecture seule, bases/réseaux
  distincts, nettoyage vérifié. Aucun accès ou changement d'une base cliente.
- Tout changement est adopté, expérimental ou rejeté après contre-épreuve.
  Deux corrections sans progrès arrêtent la variante, pas les autres jalons.
- Une preuve documentaire ne remplace pas un test ORM/RPC/navigateur. Une
  affirmation de contexte n'est reprise que si sa source la porte effectivement.

## Bornes de cette campagne

Maximum 10 appels CLI LLM, tous explicites, Claude opus/medium constants :
jusqu'à 4 essais de consolidation à 360 s, jusqu'à 6 parcours complets à 900 s.
Une limite monétaire par appel sera passée au CLI si disponible et relevée
dans le protocole d'exécution. Pas de relance cachée, ni d'appel LLM en CI.
Les audits et oracles locaux indépendants ne lancent aucun CLI fournisseur.

Les qualifications droits et restauration disposent chacune de trois scénarios
et quinze minutes d'exécution active initiale. Les incidents techniques donnent
lieu à un amendement documenté. Les versions non équipées restent non qualifiées.
Les répétitions de coût ne priment pas sur les cas critiques : si le budget ne
permet pas une comparaison causale, le bilan dit « descriptif, gain non établi ».

## Répartition et livraison

L'orchestrateur tient ce plan, les rôles, les outils de réception, les essais
natifs et la synthèse. Les travailleurs possèdent leurs lanceurs/fixtures/preuves
droits et restauration ; ils ne modifient pas les fichiers partagés. Un audit
indépendant vérifie environnement, versions et chemins navigateur.

Les profils ne sont installés qu'après adoption justifiée. Le résultat final
précise ce qui peut être confié au dispositif, les contrôles à garder et les
prochains investissements utiles. La campagne est close par ce bilan, même si
certaines dimensions restent explicitement non qualifiées faute de preuves.

## Amendements consignés

- Q4 : les trois essais initiaux ont révélé un crash Chrome et des tests sautés
  malgré un code Odoo zéro. Oracle rouge conservé. Deux essais supplémentaires
  maximum (positif et mutant), quinze minutes de diagnostic/exécution, sans LLM,
  sont autorisés pour corriger uniquement le banc et vérifier le navigateur.
- Q5 Studio : le seed N03 ne fournit aucune ACL au modèle manuel initial ; les
  scénarios métier RPC demandés sont donc impossibles pour admin. Essai initial
  conservé. Correction du seed et préflight RPC réel isolé, puis sixième et dernier
  appel complet réservé au rejeu N03 à paramètres identiques (900 s / 12 USD).
  Les droits sont préexistants à la demande, pas ajoutés par le candidat.
- Q3 traçabilité : la relecture a constaté que le premier essai archive le vrai
  restaurateur mais pas le lanceur ni les deux scripts ORM. Le lanceur les fige
  désormais avant exécution et utilise ces copies. Rejeu déterministe des trois
  scénarios autorisé pour vérifier cette correction de provenance ; aucun LLM.
- Q5 Studio, QA externe : si le CLI n’a pas appliqué deux fois le pack livré,
  un parcours sans LLM de cinq minutes maximum applique ce même pack inchangé sur
  un Lab neuf et vérifie le calcul par RPC. Cette QA de l’orchestrateur reste
  séparée de la note du parcours natif ; aucun crédit rétroactif au CLI.
