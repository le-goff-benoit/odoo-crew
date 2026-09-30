# Mémoire, réception et pilotage — 30 septembre 2026

Référence : `063ac5f`. Deux corrections présentes dans le checkout avant ce travail
sont conservées : annulation motivée des flows sans revendication et exclusion des
décisions remplacées dans les sources d’impact (rapport du 17 septembre).

## Contrats et résultats

| Défaut / risque | Contre-épreuve synthétique | Résultat |
|---|---|---|
| Leçons en puces perdues | Gras, puce, label mixte ; champ suivant exclu | Corrigé |
| Exception cachée par le budget | Rubrique obligatoire plus longue que le budget | Exception conservée, insuffisance annoncée |
| Décision limitée à une release | Publication A puis lecture B ; remplacement explicite | Registre projet alimenté, ancien état historique |
| Proposition promue à tort | Proposition puis acceptation sourcée | Aucune confirmation avant acceptation |
| Remplacement concurrent | Deux successeurs pour le même prédécesseur | Second refusé avant écriture |
| Sources courantes périmées | Mutation après préparation | Publication/refus de validation |
| Conflit de journal indépendant | Ajout tiers entre préparation et publication | Conservé ; répétition sans doublon |
| Ajout ou base altérés | Modification du préfixe / bloc publié / preuve | Refus, aucune publication silencieuse |
| Feedback perdu à la clôture | Collecte répétée, append du journal, tri, échec/rattrapage | Historique immuable et tri préservés |
| Façade contournant les portes | Double start, réception d’un flow ouvert, environnement changé | Refus du moteur conservés |

Les tests de mémoire sont rouges sur la référence (`memory-before.log`) puis verts.
Cas inédit ajouté après le premier correctif : label `Exception :` en continuation
et lecture de la release d’origine après remplacement dans une autre release.
Ils détectent deux angles morts supplémentaires, corrigés avant adoption.

## Validation

- Tests : `tests/pilotage/test_harness_{memory,feedback,work}.py`, tests de réception
  enrichis, suite complète ; contrôle du graphe et build isolé avec parité.
- Tricorder : tests du CLI avec caractères shell littéraux, parcours Electron
  sur projets synthétiques, réception de la demande et reprise contextualisée,
  contrôles historiques de persistance et navigation conservés.
- Aucun projet client ni aucune source Odoo modifiés par les essais.
- `measurements.json` mesure la taille du routage initial, pas le temps d’exécution.

## Adoption et limites

Fonctions déterministes adoptées avec tests ; instructions raccourcies adoptées
comme politique explicite. Aucun gain de vitesse, coût ou qualité comportementale
revendiqué : pas de nouvelle campagne native comparative Astra/Sol/Opus.
Sol 6 reste candidat expérimental, les rôles héritent du principal. La parité de
construction Claude/Codex est conservée tant qu’aucune divergence utile n’est prouvée.

Le feedback automatise la capture et le bilan déterministe. Sa qualification
sémantique demeure une opération explicite des agents. Aucun scheduler LLM ni
base vectorielle ajouté. Une mémoire de décisions peut rester partielle : les
règles manuscrites restent obligatoires jusqu’à reprise sourcée. La cible d’usage
« comprendre en moins de 30 secondes » attend un essai avec l’utilisateur.

Guide opérationnel : [HARNESS.md](../../HARNESS.md).
