# Délégation réelle et couverture du dispositif — 9 septembre 2026

Suite demandée explicitement par l'utilisateur après le constat que la
campagne native n'avait pas mesuré la délégation. Référence figée :
`ddc8f7d29b83feee5d9699ed6fe53b6a5f007188`.

**La délégation et la reprise sont désormais observées sur de vrais sous-agents
Claude. La qualité du verdict final n'est pas validée : la consolidation
déclare satisfait un critère utilisateur resté sans preuve.** Les corrections
de mesure sont livrées ; une consigne supplémentaire a été testée puis non
adoptée faute de gain démontré.

| Essai | Exécution observée | Résultat et limite |
|---|---|---|
| N04, délégation initiale | 5 sous-agents : analyse, développement, 3 QA ; les 3 QA travaillent avec un chevauchement observé | Limite de 600,01 s atteinte ; QA et consolidation inachevées. Oracle copie 1/4 vrai, mise à niveau non effectuée avant interruption. Incident conservé |
| N04, reprise en contexte neuf | 3 nouveaux testeurs, 3 terminés ; chevauchement conservateur des 3 activités : **40,932 s** | 477,15 s ; 3 revendications abandonnées libérées, nouvelles QA, code conservé. Oracle Odoo **4/4 vrai**, flow terminé ; **verdict global refusé en relecture externe pour A8** |
| Consolidation sur dossiers | Référence : `retry` ; candidat : `retry` ; contre-épreuve valide : `pass` | Aucun gain démontré de la consigne ajoutée. Non adoptée ; ces réponses ne réparent pas le verdict du parcours natif |

Le chevauchement est calculé entre premières et dernières progressions natives
des enfants, avec un horodatage de réception par le superviseur. Il ne mesure
pas du calcul simultané côté fournisseur. Le résultat natif confirme trois
enfants terminés à la reprise, profondeur 1 et aucun enfant lancé par un autre
enfant. Modèle effectivement retourné : `claude-opus-5`.

## Pourquoi la campagne précédente ne la mesurait pas

Le runner `scripts/odoo_bench_native.py` désactive `multi_agent` pour Codex,
n'expose pas l'outil de délégation à Claude et demande expressément d'appliquer
les rôles sans sous-agent dans `_trial`. C'est donc une exclusion explicite
du banc. Elle est consignée dans le protocole précédent, mais cela ne justifie
pas l'absence d'une campagne complémentaire. Aucun motif historique plus
précis n'est établi ici.

## Défaut reproduit et correction adoptée localement

`odoo_flow.py status` annonçait « Agents délégués N actif(s) » à partir des
revendications du graphe. Une revendication réussie sans aucun lancement de
modèle suffisait à faire monter ce compteur. Le refus fournisseur de cette
session rend la distinction particulièrement utile.

Le compteur affiche maintenant **« Nœuds agent N revendiqué(s) »**. Il décrit
exactement l'information disponible. Les transitions, verrous et formats JSON
restent compatibles ; aucun mécanisme de mesure des processus n'est inventé.

- Régression : un nœud revendiqué localement ne doit pas annoncer un sous-agent
  vivant ; la référence échoue sur cette propriété.
- Contre-épreuve : même propriété sur un parcours séquentiel, hors du fork initial.
- Incident : libération avec motif, refus d'un autre propriétaire, conservation
  des jetons et événements, maintien de la branche voisine, réattribution puis
  jointure seulement après la dernière preuve.
- Avant : 4 échecs parmi 31 tests du graphe. Après : 31/31 verts, suite complète
  126/126 à cette étape, puis **129/129** après l'ajout du mode du banc. Les deux nouveaux tests du graphe sont des contrôles déterministes ; ils ne
  prouvent pas la capacité d'un LLM à reprendre seul après une interruption.

Preuves : [rouge](evidence/flow-red.log), [vert](evidence/flow-green.log).
Cette correction porte sur la véracité de l'affichage, pas sur l'amélioration
du raisonnement des agents. Aucun rôle n'est modifié sur cette seule observation.
La distribution isolée et les profils actifs ont été reconstruits : 26 fichiers,
deux blocs et le pointeur personnel conformes. Les contrôles sont conservés dans
[suite finale](evidence/suite-final.log), [build isolé final](evidence/build-isolated-final.log) et
[build actif](evidence/build-active.log).

Le runner maintenu expose maintenant **`--delegate-claude`**, désactivé par
défaut. L'option et son relevé natif restent **expérimentaux** : les commandes
et la consigne sont équivalentes à l'adaptation réellement exécutée, et le
compteur a été rejoué sur ses événements originaux. Les tests vérifient
activation explicite, exclusion des processus Bash, échec d'un enfant et
interruption. La description de `/odoo-improve` est actualisée dans sa source
canonique ; aucune règle de raisonnement QA n'est ajoutée.

## Essai natif complémentaire

Le premier appel réel `collaboration.spawn_agent` (`/root/audit_couverture`)
échoue avant de produire un travail : quota Codex. C'est un incident fournisseur,
pas un échec d'analyse. Il reste enregistré dans [protocol.json](protocol.json).

Un test Claude isolé de disponibilité dépasse 90 secondes dans le sandbox réseau ;
le même test, avec l'accès réseau autorisé et l'isolation bubblewrap conservée,
répond `PRET`. Il n'a lancé aucun sous-agent et ne compte pas comme une mesure
de délégation.

La suite réutilise N04, cas SQL déjà étalonné du banc : vraie base Odoo 19,
PostgreSQL jetable, contraintes et tests ORM contrôlés par l'oracle externe.
Le runner expérimental ajoute seulement les outils natifs `Agent`, `TaskOutput`,
`TaskStop` et remplace la consigne interdisant la délégation. Les profils et
l'oracle restent ceux de la référence. Un essai, Claude `opus` / `medium`,
600 secondes maximum pour chaque appel principal ; aucun classement ni gain de
vitesse causal ne peut être déduit de cet effectif.

Le protocole et l'empreinte du runner adapté sont figés avant lancement.
Le compteur hors ligne est étalonné séparément : un événement `task_started`
de type `local_bash` ne doit pas être compté comme un agent. La première version
du compteur confondait les deux ; son résultat intermédiaire invalide et la
contre-épreuve rouge sont conservés. La version corrigée exige `local_agent`
et sera appliquée à tous les événements originaux, sans modifier les réponses. Les
événements natifs sont horodatés à leur réception par le superviseur ; les
temps de revendication ne servent pas de preuve de travail simultané.

Limite du transport : `Lab.handle` conserve un verrou commun et `Bridge` utilise
`UnixStreamServer`. Les commandes Odoo du pont sont donc sérialisées, même si
plusieurs agents travaillent. Cette campagne peut prouver une délégation et
des périodes d'activité qui se chevauchent ; elle ne mesure pas une exécution
parallèle de toutes les commandes QA. Une optimisation de ce transport exigerait
des tests distincts de synchronisation du code et d'isolation des bases.

La reprise utilise les fichiers exacts du premier essai et de nouvelles bases
synthétiques. L'orchestrateur libère les trois revendications, ne rejoue pas
l'analyse/le développement et conserve le module octet pour octet. Il exige
de nouvelles preuves runtime puisque les bases sont nouvelles. La copie est
rendue vide avec sa contrainte en place ; les conteneurs des deux essais ont
été supprimés, vérification faite après leur fermeture.

L'oracle N04 est inchangé et son [étalonnage antérieur](../native-2026-09-09/evidence/calibration/N04/calibration.json)
accepte le témoin correct et rejette le mutant sans contrainte. Il contrôle
zéro autorisé, création négative refusée, écriture négative refusée et
conservation du valide. Il ne contrôle pas le message reçu par un utilisateur.

## Défaut de consolidation et boucle de rétroaction

La spécification porte en A8 : « Le message d'erreur configuré est bien celui
remonté à l'utilisateur (non vide) ». La QA remplace ce critère par « message
configuré non vide » et annonce neuf critères satisfaits. Pourtant sa réserve
dit explicitement que ni RPC ni interface n'ont été traversés. Le terminal
`pass` du flow atteste une décision enregistrée, **pas la satisfaction de A8**.

La [relecture externe](evidence/external-review.json), non aveugle, refuse donc
le verdict global. Une reprise ou un blocage était attendu pour cette preuve
manquante ; l'oracle SQL vert ne compense pas ce défaut. Les réponses, `qa.md`,
le journal et l'état du flow sont conservés tels que produits.

Une proposition rappelant de conserver le libellé et la portée des critères
a été figée puis comparée à la référence sur un dossier reprenant ce défaut.
Un nouvel exemple d'export complet, sans exigence de PDF/écran, sert de
contre-épreuve positive. Réglages constants, aucun outil ni accès Odoo dans
ces trois probes. **Référence et candidat demandent tous deux `retry` pour
A8 ; le candidat accepte le cas valide.** La consigne n'est pas promue :
son bénéfice n'est pas démontré et son ajout ne prouve pas qu'elle corrigerait
la dérive dans un parcours long. [Protocole et verdict](evidence/gate-probes/verdict.json).

Autres réserves : `author` manque dans le manifest initial ; ce n'est pas une
régression de la tâche. L'ancien objet Git `.base` n'est pas transporté par
la copie de fichiers et la QA le signale. Une comparaison externe avec la
référence confirme les trois seuls fichiers changés et le manifest intact ;
ce contrôle n'est pas attribué rétroactivement aux agents. Le coût complet
des deux parcours n'est pas disponible, le premier ayant été interrompu
avant le bilan fournisseur. Aucun gain de vitesse n'est démontré.

## Preuves et décisions d'adoption

- [Premier essai interrompu](evidence/interrupted/state.json) et
  [chronologie sélectionnée](evidence/interrupted/native-events.jsonl).
- [Reprise](evidence/resumed/state.json), [chronologie](evidence/resumed/native-events.jsonl),
  [mesures](evidence/measurement-resumed.json), [invariants de reprise](evidence/recovery-invariants.json).
- [Équivalence du runner livré](evidence/maintained-runner-equivalence.log),
  [calibration du compteur](evidence/measurement-calibration.log),
  [réserve Git vérifiée séparément](evidence/independent-source-review.json),
  [nettoyage](evidence/cleanup.json).

Décisions : compteur d'état **adopté** ; option du banc **expérimentale,
installée** ; consigne de consolidation **non adoptée** ; qualité globale des
agents **non qualifiée par ce seul cas**. Les homes, authentifications et
événements fournisseur bruts restent hors dépôt. Les fichiers exportés sont
contrôlés par `evidence/SHA256.json`. La source de l'adaptation et la commande
locale sont conservées ; le mode maintenu se lance selon [OPERATIONS.md](../OPERATIONS.md).

## Autres éléments à tester

Le [carnet de couverture](COVERAGE.md) distingue les contrôles déjà présents des
mesures qui manquent, avec scénarios et critères : fiabilité du juge et de la QA,
droits multi-sociétés, mémoire longue et passation interrompue, restauration
complète, navigateur, autres séries et coût total de coordination.

Les règles de rôle éventuelles resteront expérimentales jusqu'à reproduction,
comparaison à réglages constants et contre-épreuve inédite. Ajouter des consignes
sur la seule base de cette liste ne constitue pas une amélioration mesurée.
