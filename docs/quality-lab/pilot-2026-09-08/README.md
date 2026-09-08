# Pilote court — résultats du 8 septembre 2026

Le laboratoire a exécuté les six réponses autorisées. La revue exploratoire
relève **4 conformités à la grille initiale, 1 cas à arbitrer et 1 rejet critique**.
Le résultat utile est un défaut observable de fidélité de la mémoire métier,
ainsi qu’une faiblesse de notre grille. **Aucune amélioration des agents n’est
encore démontrée** et aucun rôle actif n’a été modifié.

## Résultats observés

| Cas | Codex : durée / jugement | Claude Code : durée / jugement |
|---|---|---|
| B03 — cadrage d’une validation | 78,7 s / conforme à la grille | 111,2 s / conforme, avec réserves hors grille |
| B06 — QA des droits | 36,6 s / conforme | 50,3 s / à arbitrer |
| B10 — décision remplacée et passation | 64,6 s / conforme | 169,6 s / rejet critique |

Durée cumulée des six exécutions : **511 secondes, soit 8 min 31 s**. Ce n’est
pas la durée totale de conception, de préparation ou de revue du chantier.
Un démarrage bloqué par le réseau du sandbox, puis un problème DNS dans le
montage isolé, sont conservés localement comme incidents d’infrastructure.
Aucune réponse ni usage n’a été enregistré lors de ces incidents.

Les paquets fournis étaient identiques entre outils pour chaque cas : 2 036,
2 478 et 2 116 mots. Les sorties vont de 557 à 4 256 mots. La longueur n’est pas
une note de qualité ; elle justifie un futur test de passation plus concise.

## Ce que le pilote nous apprend

**Mémoire métier : un défaut détecté.** Dans B10-Claude, les cinq exemples
directs sont corrects, mais des hypothèses nouvelles se retrouvent dans
`PROJECT.md` sous « Décisions actées ». Le point de blocage à la confirmation
et la référence au dernier taux approuvé ne viennent pas des messages client.
La réponse ordonne aussi d’appliquer ses hypothèses si les réponses tardent.
Le critère critique `memory` est donc rejeté : citer les messages sources ne
suffit pas si on leur attribue des décisions qu’ils ne contiennent pas.

**Grille : un angle mort détecté.** B03-Claude satisfait les six critères v1,
mais retient par défaut l’approbation des devis existants et avance une voie
technique avant vérification du standard. Ces réserves restent visibles ; nous
n’avons pas changé le barème après lecture pour fabriquer un échec. Le prochain
barème devra couvrir la propagation des hypothèses dans toutes les sections.

**QA : résultat encourageant, avec un point à arbitrer.** Les deux réponses B06
refusent le faux vert basé sur admin et zéro test. B06-Claude ne demande pas
clairement un accès direct aux devis interdits indépendant du bouton. Ses tests
`with_user()` pourraient couvrir une partie du besoin ; le critère `matrix`
reste `uncertain` au lieu d’une validation implicite. Sa formulation sur admin
et certains passages qui présentent une régression comme acquise sont aussi
signalés hors grille.

**Bon cas discriminant à conserver.** B10-Claude ajoute un devis non partenaire
approuvé à 16 %, puis réduit à 14 %. Ce cas teste la baisse tout en restant
au-dessus du seuil de 10 % ; il distingue une vraie conservation de l’approbation
d’un simple retour sous le seuil. Une réponse défaillante peut aussi apporter
un bon test : conserver le signal sans promouvoir l’ensemble.

## Portée et limites

- Modèles demandés : Codex `gpt-6-astra` / effort `high` ; Claude `opus` / effort
  `medium`. Claude retourne `claude-opus-5` ; Codex ne retourne pas le modèle
  effectif dans les événements exploités. L’effort effectif n’est pas retourné.
- Une seule répétition, ordre fixe, configurations différentes, effets de cache
  possibles : aucune supériorité générale ou causalité entre outils ne découle
  de ces résultats. Les données d’usage restent brutes, pas un coût facturé.
- Le juge est le Codex orchestrateur qui a conçu le banc : revue manuelle
  exploratoire, non aveugle, sans validation humaine indépendante. Les verdicts
  sont auditables via les réponses et les preuves ; les ambiguïtés restent ouvertes.
- Les rôles sont injectés explicitement dans un dossier sans outils. Le routage
  natif des skills, la mémoire persistante entre sessions et les chaînes complètes
  ne sont pas testés. B10 simule un historique dans un seul dossier.
- **Développement : non mesuré.** Aucun code ni test métier n’a tourné dans Odoo.
  Une fraction de critères réussis n’est pas une moyenne de qualité globale.
- Les paquets, cas et rôles ont été figés par empreinte. Le lanceur était un
  prototype en arbre de travail depuis `9541bba`, corrigé pour le DNS avant les
  réponses exploitables ; le reporting a évolué pendant la campagne. Le pilote
  n’est pas présenté comme une expérience sur une révision déjà publiée.

## Décisions et suite

Conserver la référence active. Terminer le pilote ici, conformément au format
court autorisé. La [prochaine expérience](../NEXT-EXPERIMENT.md) vise un seul
mécanisme : éviter de transformer une hypothèse en décision client, puis comparer
une version de consignes plus courte à qualité constante. Les variantes doivent
être testées avant adoption, sur des cas réservés et avec répétitions.

Le [rapport détaillé](REPORT.md) distingue les dimensions. Les six fichiers de
réponse et leurs fichiers `.review.json` conservent les preuves ;
[measurements.json](measurements.json) contient les réglages, empreintes et mesures.
Les journaux fournisseurs et identifiants de session restent hors du dépôt.

## Validation de l’outillage

35 tests unitaires passent, contre 23 avant ce chantier. Ils couvrent notamment
la contamination par le corrigé, les paquets altérés, l’arrêt/reprise, l’absence
de rejeu automatique, le faux succès, les appels d’outils interdits, les preuves
d’évaluation et l’absence de compensation d’un échec critique.
Le graphe conserve ses 52 nœuds et 115 arêtes. La génération dans un répertoire
isolé vérifie 20 fichiers et deux blocs d’aiguillage. La syntaxe shell et les
espaces du diff sont contrôlés. Le dépôt actif reste propre à `9541bba`.
