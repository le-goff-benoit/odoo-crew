# Réception structurée des critères — 9 septembre 2026

**Adopté : un contrat QA optionnel, épinglé dans le flow, et son usage par
l'orchestrateur pour les revues au format cases à cocher.** Le candidat bloque
la réception D31 qu'une référence fraîche accepte à tort. La protection
structurelle est démontrée ; la qualité complète des rapports reste à améliorer.

## Ce qui change

`odoo_flow.py bind-criteria` extrait la section « Critères d'acceptation » de la
revue, conserve le texte intégral et son empreinte dans le flow, puis produit
une couverture initialement `missing`. Quand ce contrat est lié, `pass` des
trois jointures QA exige une couverture exhaustive : textes inchangés,
statuts `covered` et références de preuves avec empreintes valides. Une preuve
`odoo-evidence/1` garde également son contrôle de fraîcheur du code et du log,
quelle que soit son extension.

Le refus intervient avant toute consommation de jeton ou libération de
revendication. `retry` et `blocked` restent accessibles. Le graphe n'a pas
changé, et les flows non liés gardent leur comportement. Le tableau de bord
rend l'activation visible. Le rôle d'orchestration explique la liaison et la
couverture ; les détails sont dans [QA_COVERAGE.md](../../QA_COVERAGE.md).

Limites assumées : format de revue borné, toutes les cases de la section
traitées comme obligatoires, contrat lié non remplaçable dans ce premier
outil. Une revue révisée exige un nouveau flow selon l'arbitrage acté. Aucun
déploiement ou changement de données client n'est réalisé par ce mécanisme.

## Essais natifs comparables

Référence `7a0f6abddbbaace20c21381f30cebab03104cb7d`. Quatre appels Claude
isolés par bubblewrap, un contexte neuf par appel, avec les vrais profils et
outils de flow. Modèle demandé `opus`, observé `claude-opus-5` ; effort demandé
`medium`, **non attesté** par le fournisseur (`actual_effort: null`). Limite
commune de 360 s, fixée avant les essais. Les anciennes variantes textuelles
arrêtées à 180 s ne sont pas réutilisées comme groupe de comparaison.

| Cas | Variante | Issue | Durée | Coût retourné par le CLI, USD |
|---|---|---|---|---|
| D31, A8 utilisateur non prouvé | Référence fraîche | `pass`, erroné | 184,58 s | 1,7688 |
| Même dossier D31 | Contrat + rôle candidat | `blocked`, attendu | 237,93 s | 2,0921 |
| P51, export CSV entièrement prouvé, PDF hors contrat | Candidat | `pass`, attendu | 143,73 s | 0,9846 |
| I7, import : message et compte prouvés, identités/valeurs non comparées | Candidat avec correction d'extension | `blocked`, attendu | 156,71 s | 0,9646 |

Les quatre appels sont achevés. Les coûts sont ceux annoncés par le CLI, pas
un relevé de facturation. Le candidat D31 est plus lent et plus coûteux dans
cet essai ; aucune amélioration générale de vitesse ou de coût n'est établie.
Une seule exécution par condition ne suffit pas à une conclusion statistique.

La revue D31 est byte-identique entre référence et candidat
(`2061340268223878cb609c576a943d89662e04ba5cd25d5d6af003126591d513`).
Comme dans la campagne précédente, l'état avant jointure est reconstruit par
les six événements antérieurs ; les preuves originales sont conservées et
les résultats postérieurs retirés. Ce n'est pas la reconstitution du contexte
conversationnel long. Aucun test Odoo, RPC ni base n'est réexécuté dans ces
exercices de consolidation. P51 et I7 sont des attestations synthétiques,
avec critères fixés avant leurs appels.

Le candidat lie spontanément le contrat dans les trois cas, conserve A8
`partial` dans D31 et choisit directement `blocked`. **Il ne tente pas un
`pass` que l'outil refuserait dans ce parcours natif.** L'amélioration observée
porte donc sur le paquet instructions + structure ; l'intervention mécanique
du garde est démontrée séparément par la calibration et les tests.

[Protocole](evidence/protocol.json), [quatrième cas proposé indépendamment](evidence/fourth-case-protocol.json),
[résultats et empreintes des flux bruts](evidence/results.json). Les réponses,
couvertures, revues, flows, métriques fournisseur et sorties humaines des
commandes sont archivés, sans home fournisseur ni flux de prompts complets.
Les scripts gardent leurs chemins scratch d'origine ; les entrées D31 sont
reconstructibles depuis les archives de la campagne de délégation et leurs
empreintes. Aucune campagne payante n'est ajoutée à la CI.

## Calibration du garde et relecture indépendante

La [calibration](evidence/calibration.json) conserve quatre témoins :

1. L'ancienne complétion accepte une déclaration `partial`.
2. La nouvelle refuse la même déclaration, sans modifier l'état persisté.
3. La nouvelle accepte une couverture complète avec preuves.
4. Une déclaration mensongère `covered`, avec références inchangées mais
   contenu insuffisant, peut encore passer : **témoin de limite sémantique**,
   jamais compté comme réussite métier.

Un sous-agent natif indépendant (`revue_reception`, lecture seule) a relu
l'intégration, le code et les résultats. Il a trouvé un contournement réel du
contrôle de fraîcheur par renommage d'une preuve JSON en `.log` ou `.JSON`.
Deux assertions rouges le reproduisent ; la reconnaissance par contenu les
rend vertes. Les deux premiers candidats natifs utilisent le snapshot avant
cette correction ; I7 utilise le snapshot corrigé, avec le même rôle. Les
variantes exactes et les journaux rouges/verts sont conservés.

Le relecteur a aussi proposé I7 : un compte final inchangé ne prouve pas que
les anciennes lignes gardent leurs identités et valeurs. Le candidat conserve
ce critère partiel et bloque la réception. Cette revue indépendante n'est
pas une nouvelle mesure de parallélisme ni un classement de modèles.

Onze nouveaux tests couvrent les trois gates, les critères partiels/omis/
reformulés/ajoutés/déplacés, sources et preuves modifiées, preuves structurées
avec autres extensions, anciens flows, sorties de reprise, propriétaires,
rebinding identique, refus après réception et double complétion concurrente.
Suite complète : **147 tests verts**, lint bloquant vert, graphe et génération
isolée conformes. Les preuves et journaux sont hachés dans `evidence/SHA256.json`.

## Réserves d'adoption et suite

La relecture indépendante confirme deux écarts dans les réponses conservées :

- D31 candidat garde le titre **« VALIDÉ SOUS RÉSERVE »** alors qu'A8 reste
  partiel et que le flow est `blocked`. Le passage incorrect est évité, mais
  le verdict destiné à l'humain reste contradictoire.
- P51 affirme que les trois fragments portent le même build `p51-1`, alors
  que le fragment statique mentionne seulement la révision `fixture-p51`.
  La décision sur les critères reste cohérente ; cette précision de traçabilité
  n'est pas étayée et ne doit pas être reprise comme un fait.

Ces réponses n'ont pas été réécrites. Le garde ne transforme pas des références
exactes en démonstration métier, ne garantit pas la fraîcheur d'un simple
Markdown et ne protège pas contre une modification directe de l'état du flow.
La relecture du sens des preuves et l'oracle indépendant restent nécessaires.

La prochaine boucle doit faire concorder verdict lisible et issue de réception,
et éprouver les affirmations de traçabilité. Le transport RPC livré auparavant
reste à mesurer dans une chaîne complète ; droits réels multi-sociétés,
restauration/filestore, navigateur et autres séries restent des axes distincts.
