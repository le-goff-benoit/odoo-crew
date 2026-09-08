# Revue des arbitrages — orchestrateur, non aveugle

Les scores du README restent ceux du correcteur masqué. Cette revue de
l'orchestrateur qui a conçu le banc est complémentaire, non indépendante ; elle
ne transforme pas ces scores en vérité de référence.

- Les quatre rejets de la référence Claude comportent des preuves explicites :
  par exemple B11-r2 demande que « le développeur les implémente telles quelles »
  alors que les options H1–H5 restent à arbitrer. B10-r1 affirme une couverture
  standard chiffrée sans inspection. Ces défauts justifient la non-adoption de
  comportements qui assimilent une hypothèse à une décision.
- B10-Claude-fidélité-r1 est accepté par le juge, mais sa fin présente l'incrément 1
  comme démarrable en l'état, après l'avoir conditionné à une réponse Q2. Plusieurs
  critères fixent aussi la confirmation comme point de blocage. Une passation
  destinée à une exécution réelle demanderait une clarification de ce statut ;
  la note automatique ne vaut donc pas feu vert de développement.
- Pour B10-Claude-compact-r1, le juge hésite sur R-6, un refus côté serveur décrit
  comme exigence de passation à confirmer. Le contrôle serveur n'est pas en soi
  une décision métier nouvelle : il rend effective l'interdiction explicite.
  La formulation « à confirmer, mais à implémenter par défaut » reste maladroite,
  et le point exact du workflow doit rester distinct de ce principe de sécurité.
  Ne pas apprendre au rôle à retirer les contrôles serveur pour améliorer son score.
- Un test de borne omis, alors que d'autres tests existent, produit parfois
  `uncertain` plutôt que `fail`. Les deux empêchent un verdict entièrement conforme ;
  le prochain étalonnage doit clarifier cette granularité du jugement.

Aucune variante d'analyse n'est promue sur la seule base de ce tableau. Pour une
prochaine campagne, ajouter des exemples limites au calibrage et faire relire
un échantillon par un autre évaluateur métier. Préserver les avis initiaux et les
motifs d'arbitrage, au lieu de régler le juge pour qu'il favorise une variante.

Pour le code, les corrections de l'oracle sont fondées sur S-01/S-02, qui n'imposent
pas une classe précise d'exception. Les sorties des modèles sont inchangées, les
mutants restent rejetés, et tous les candidats utilisent l'oracle final commun.
La consigne développeur V2 est retenue pour le défaut concret reproduit ; cette
adoption n'affirme pas que les codes testés sont prêts pour un client réel.
