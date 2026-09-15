# Procédure — qa-reception

Chargement conditionnel depuis le profil canonique. Les chemins `docs/…` et
`roles/…` sont relatifs à `~/.odoo19-agents/`.

### Réception documentaire : s'arrêter après ce mode

Ce mandat prime sur les étapes de lint, exécution et navigateur ci-dessous.
Lis la demande originale et les décisions applicables avant la synthèse QA.
Tu ne modifies ni les archives, ni la revue, ni la couverture, ni la mémoire,
ni le flow. Écris seulement le fragment de réception demandé ; ne délègue pas
à ton tour. Un contexte neuf, distinct des auteurs du dossier, permet une
réception indépendante. Une relecture dans leur conversation reste une
auto-relecture : l'identité déclarée ne prouve pas l'indépendance.

Examine ensemble trois axes, en citant les passages des deux côtés :

- **Demande ↔ contrat** : retrouve chaque obligation originale avec son objet,
  opération, acteur, canal, bornes, exceptions et effets interdits. Qualifie
  les ajouts de la revue (conséquence justifiée, hypothèse, choix technique ou
  obligation supplémentaire à clarifier). Une difficulté d'outillage ne réduit
  pas la demande. Un critère écrit supplémentaire ne disparaît pas silencieusement
  après l'obtention des résultats.
- **Contrat → preuves** : vérifie l'opération et le contexte effectivement
  attestés, ainsi que toutes les conditions des critères composés. Distingue
  ce qui réussit de ce qui manque ; un artefact voisin ou un titre « couvert »
  ne prouve pas l'action demandée. Conserve les succès techniques établis.
- **Sources → mémoire** : confronte les phrases nouvelles ou modifiées aux
  décisions et preuves. Préserve portée, négations, exclusions et formules ;
  distingue résultat local, livraison et historique réellement disponible.
  Vérifie les remplacements nécessaires, pas seulement les ajouts.

En reprise après conflit mémoire, compare aussi les copies de base figées aux
nouveaux drafts : les contributions déjà publiées par les autres tâches doivent
rester présentes et garder leur sens. Vérifie également que la nouvelle entrée
transmet le résultat effectivement reçu (réussite, échec ou limite), pas seulement
l'existence ou la conservation d'une preuve. Une chronologie de reprise ne
remplace pas ce résultat. Refuse cette perte même si tous les hashes sont frais.
Cite ces bases lorsqu'elles figurent dans le bundle. Le code et la QA reçus auparavant restent acquis seulement si leurs
empreintes et leur contrat sont inchangés ; le renouvellement de la mémoire ne
permet pas de les requalifier.

Avec un bundle de réception, lis `docs/TASK_RECEPTION.md` du référentiel et
produis le JSON `odoo-task-reception/1` dans le fichier isolé demandé. Le helper
`python3 ~/.odoo19-agents/scripts/odoo_reception.py draft <bundle> --reviewer <identité>`
fournit son squelette. Renseigne les trois axes avec citations exactes et
explications ; ne copie pas un verdict suggéré par l'orchestrateur.

Sans bundle, pour une réception d'archives, écris `reception.md` (ou le chemin
demandé) : verdict par axe, citations localisées, conclusion et corrections
justifiées. Ne rouvre pas le flow historique. Une fixture déclarée documentaire
se juge dans cette portée : ne réclame pas une nouvelle exécution pour accepter
un dossier cohérent et étayé. Une correction de mémoire ne justifie pas à elle
seule de rejouer des tests encore valides. Termine après ce fragment.

