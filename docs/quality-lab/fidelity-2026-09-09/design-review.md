# Réception indépendante de fidélité — revue de conception

Lecture seule du dispositif, 09/09/2026. Aucun code, profil, graphe, dossier de preuve ou base modifié. AGENTS.md, roles/quality-improve.md, docs/IMPROVEMENTS.md et docs/quality-lab/OPERATIONS.md lus. Ce rapport est une proposition, pas une preuve d'amélioration comportementale.

## Conclusion

Réutiliser **odoo-tester avec un mode documentaire explicite de réception**, dans un contexte neuf, plutôt que créer un sixième rôle. Le changement utile n'est pas un rappel « être fidèle » : fournir d'abord la demande originale et les décisions en vigueur, puis exiger une confrontation bidirectionnelle avec la revue, les preuves et le texte de mémoire. Le relecteur ne corrige aucun de ces documents et rend un fragment isolé ; l'orchestrateur reste seul écrivain.

Pour garder le graphe actuel et ses voies de reprise, la réception doit intervenir à la jointure QA **sur la mémoire proposée**, avant `pass`, puis la publication doit conserver ce contenu reçu. Une réception seulement après `journal_task` détecte N01 tardivement mais ne possède aujourd'hui aucune transition naturelle `retry`/`blocked`. Une réception seulement avant `journal_task`, sans mémoire proposée, laisse N01 hors de son dossier.

## Défauts observés et cause commune

1. N03 initial : la revue remplace les scénarios RPC métier par ORM superutilisateur + RPC définition/refus d'accès. N03 rejeu : la revue remplace deux applications du pack par deux constructions du champ + export/diff. Les réponses annoncent ces limites ; le faux succès global vient de la réception d'une spec réduite, et non d'une invention des opérations exécutées. Preuves : `docs/quality-lab/qualification-2026-09-09/evidence/complete-independent-review.md`, sections N03 ; README de qualification lignes 136–165.
2. Q5 reprise : `recovery/final-project/changelog/2026-09-09_01_interdiction-des-durees-negatives-sur-le/revue_fonctionnelle.md:122` exige les RPC dans la suite `/bridge/labctl qa lab_rental`. Cette suite est ORM ; des appels XML-RPC externes satisfont plusieurs critères mais pas ce critère composé C08. Il doit rester partiel sous ce contrat. La demande d'origine n'imposait pas ce placement des RPC : cette précision ajoutée peut être une surspécification, mais son effacement silencieux après les résultats serait incorrect.
3. N01 : `native/complete-N01/project/.odoo-agents/PROJECT.md:6` dit « prêt (...) toujours gratuit » et ligne 21 « aucune location de 4 jours facturée ». `decisions/2026-09-09.md` conserve pourtant `jours × tarif_jour` hors forfait : seule la préparation est exclue. La mémoire suraffirme aussi l'existence d'un historique Git. QA technique et calcul ne suffisent donc pas à réceptionner la mémoire.

Les chemins abrégés ci-dessus sont relatifs à `docs/quality-lab/qualification-2026-09-09/evidence/`. Aucune nouvelle exécution n'était requise pour établir ces contradictions documentaires.

## Intégration minimale recommandée

### Contrat de la réception

Le dossier fournit les sources brutes (demande telle quelle, décisions complémentaires avec remplacement explicite), la revue et son contrat lié, la couverture, les fragments/logs pertinents, puis les changements proposés à PROJECT/JOURNAL. Le relecteur reçoit un mandat distinct de l'auteur de la revue, du développeur et de la synthèse QA. Un autre nom de propriétaire ne constitue pas à lui seul une preuve d'indépendance : consigner l'identité/contexte réellement utilisé ; sans sous-agent disponible, annoncer la relecture par l'orchestrateur et cette limite.

Une seule réception vérifie trois axes :

- **Demande vers revue et revue vers demande** : chaque obligation originale conserve acteur, objet, opération, canal, borne, exception et effets interdits. Chaque précision ajoutée est une conséquence justifiée, un choix d'implémentation non contractuel ou une exigence à clarifier ; elle n'est pas automatiquement une nouvelle obligation client. Une impossibilité d'outillage ne supprime pas une obligation.
- **Critère vers preuve** : citer le passage qui prouve les conditions précises, et ce qui reste absent. `apply` n'est pas `build`, RPC métier n'est pas RPC métadonnées, appels RPC séparés ne sont pas présence dans une suite donnée. Ces exemples appartiennent aux fixtures ; le profil doit exprimer la règle générale sans mémoriser les trois cas.
- **Source vers mémoire proposée** : relire les phrases nouvelles/modifiées et leurs sources, préserver portée et exclusions, distinguer calcul, validation locale, livraison et disponibilité d'un historique. Une absence de changement mémoire doit aussi être explicitement motivée.

Le fragment donne conforme / à reprendre / indécidable sur chacun des axes, citations localisées des deux côtés, constat et correction attendue. Ne pas remplacer toute la QA technique : une preuve encore fraîche n'est pas rejouée simplement parce qu'une phrase de mémoire doit changer. Ne pas faire passer en bloc tous les récits anciens hors périmètre dans cette nouvelle réception.

### Placement et reprise

1. L'orchestrateur prépare un **fragment mémoire neuf**, sans publier PROJECT/JOURNAL. Il inclut les remplacements nécessaires, pas seulement les ajouts (N01 est un remplacement de phrase).
2. À `module_task_gate`, `module_high_gate` ou `studio_task_gate`, réception indépendante du dossier entier. Un défaut mémoire se corrige puis se fait relire avant `complete`; un défaut de preuve utilise `retry`/`blocked` actuels. Deux reprises maximum restent la borne.
3. Une revue erronée liée ne se réécrit pas pour obtenir le vert. Corriger une transcription de la demande avec traçabilité et nouveau flow/contrat ; une vraie ambiguïté métier exige l'arbitrage déjà prévu. Pas de nouvelle permission systématique pour réparer une erreur propre à l'agent.
4. Après `pass`, `journal_task` publie le fragment reçu. Le garde éventuel vérifie le contenu effectivement publié, sans permettre une paraphrase non relue.

Attention : le nœud QA ne détient pas `project_memory`. Le relecteur ne doit donc pas lire/écrire une cible changeante sans bornage. La solution minimale est un fragment isolé avec hashes de base et publication refusée si les régions à remplacer ont changé. Hacher tout PROJECT/JOURNAL est plus simple mais peut invalider à tort une autre tâche indépendante ; documenter cette limite plutôt qu'écraser la mémoire concurrente.

## Instructions seules ou garde outillé

**Premier candidat étroit** : mode de réception dans `roles/qa-review.md`, point d'appel et mémoire préparée dans `roles/orchestration.md`, distinction obligations/choix de preuve dans `roles/functional-review.md`. Graphe inchangé, fragments attachés aux preuves existantes. Mesure comportementale indispensable : aucun test de présence de mot n'atteste la compréhension.

**Si un garde est retenu** : activation explicite par flow, document/version optionnel séparé de `odoo-qa-coverage/1`. Le garde épingle demande/décisions/revue/couverture/fragments/mémoire proposée et receipt avec leurs hashes ; il exige une réception positive pour le pass, refuse les modifications et contrôle la publication mémoire à `journal_task`. Il ne prétend pas vérifier la vérité des interprétations. Ne pas remplacer le contrat de couverture existant ni faire un juge sémantique par regex. Les flows historiques sans activation gardent exactement leur comportement ; `retry`/`blocked` sans preuve périmée restent possibles.

**Alternative moins minimale** : nouveau nœud de réception après journal, avec transitions correction mémoire / QA / arrêt, dans les nouveaux snapshots seulement. C'est plus clair pour relire les fichiers réellement publiés mais modifie le graphe et exige des tests de migration/reprise. Ce choix ne doit pas être introduit implicitement au milieu de la campagne.

## Fichiers, fonctions et tests concernés

- `roles/qa-review.md` : nouveau mode documentaire, positionné avant les étapes qui imposent lint/runtime ; production d'un seul fragment, sources originales obligatoires. Éviter de laisser ce mode se lancer en « QA release » par défaut.
- `roles/orchestration.md:215–282` : appel avant réception positive, mémoire préparée/puis publiée, reprise par cause. Supprimer la possibilité logique de considérer la spec dérivée comme seule autorité.
- `roles/functional-review.md`, section produire la spec : séparer exigences sources, hypothèses et choix techniques ; ne pas transformer systématiquement un moyen de test en obligation.
- `roles/release-start.md:23` si le flow reçoit un garde : réutiliser le fragment indépendant dans la réception du plan ; ne pas lancer un second audit identique.
- `scripts/odoo_flow.py:complete_claimed_node` : point naturel d'un garde optionnel sous verrou, avant consommation des claims/jetons. `bind_criteria` fournit le précédent d'activation compatible. `qa_report` doit continuer à rendre la couverture plutôt que prétendre certifier la demande.
- Nouveau module de receipt éventuel, plutôt que grossir `odoo_coverage.verify` avec de la mémoire : ses invariants actuels portent précisément les critères dérivés.
- `scripts/odoo_plan.py:task_status` et `mutate(...finish...)` seulement si le receipt du plan doit vérifier ce nouveau type ; le plan hache déjà demande/critères et mémoire mais ne juge pas leur contenu.
- `tests/test_odoo_coverage.py` doit rester vert sans changer les anciennes attentes. Nouveau test de receipt : positif, statut rouge, source omise/changée, preuve ou mémoire changée, propriétaire distinct déclaré mais non preuve sémantique, conservation claims/registry/tokens sur refus, échappatoire retry/blocked, compatibilité des flows non liés, publication concurrente. `tests/test_odoo_flow.py` uniquement si transitions modifiées ; `tests/test_odoo_release_plan.py` si réception plan étendue.

Calibration comportementale : N03 refusé sans exiger une refonte technique ; Q5 C08 partiel sans nier les trois vrais RPC ; N01 mémoire refusée sans nier le calcul. Positifs symétriques : une demande qui autorise réellement ORM/build ne doit pas être refusée, un contrat autorisant une suite ORM plus RPC externes doit passer, et l'exemption de frais doit être distinguée d'un cas où la gratuité complète est explicitement décidée. Réserver un métier inédit pour la contre-épreuve. Les clauses supplémentaires choisies volontairement et approuvées doivent rester obligatoires : ne pas apprendre « ignorer tout ce que l'analyste ajoute ».

## Limites de la proposition

Aucune démonstration de gain de coût ou délai ; une réception en contexte neuf ajoute du travail. Aucun garde par hash ne protège contre un jugement sémantique faux, une demande source omise avant liaison, une identité de reviewer inventée ou une édition directe de l'état. Ne pas qualifier une nouvelle autonomie générale sur ces seuls cas. Le périmètre recommandé est réception des tâches module/Studio avec sources disponibles ; support pur, validation seule et clôture complète gardent leur fonctionnement sauf essai séparé.
