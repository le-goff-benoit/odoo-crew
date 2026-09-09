# Arbitrage indépendant Q5 — couverture C08

**Verdict : C08=covered n'est pas justifié par le critère entier. La réception globale « 8/8, VALIDÉ/pass » n'est pas recevable sous le contrat rédigé et lié. Les succès techniques de reprise et les comportements SQL/XML-RPC réellement constatés sont conservés.**

Relecture seule du protocole, de la demande et de D-31, de la revue, de coverage.json, qa.md, qa_synthese.md, des fragments exécution/copie et de state.json. Aucun changement de code, de résultat ni de preuve ; aucune nouvelle exécution Odoo/LLM. Les quatre références SHA de C08 correspondent aux fichiers présents.

## Contrat utilisateur et protocole de qualification

La demande exige la contrainte SQL, zéro autorisé, total inchangé, tests des créations/modifications refusées et de conservation, QA sur copie et journal. L'extension D-31 imposée avant cette qualification ajoute un vrai rejet XML-RPC avec le message métier et des données conservées. Elle n'exige pas explicitement que cet appel RPC fasse partie de la suite automatisée du module.

Le protocole fige le test du message par contenu exact de la phrase métier dans le fault. Le préfixe standard « The operation cannot be completed: » ne constitue donc pas ici un échec du message. Les oracles externes SQL (quatre contrôles vrais) et RPC (rejet, texte, lignes préservées vrais) satisfont les comportements qu'ils vérifient. La voie copie prouve en outre les appels write négatif, zéro et relectures.

Au regard du besoin utilisateur initial et de l'extension A8, le résultat fonctionnel observé est positif. La présence de tests RPC intégrés est une exigence plus précise introduite dans la spécification par l'analyste.

## Contrat rédigé C08

Le texte conservé dans revue_fonctionnelle.md puis coverage.json/qa.md est :

> Étant donné la suite de tests du module, quand on exécute `/bridge/labctl qa lab_rental`, alors tous les tests passent, y compris les scénarios ci-dessus couverts par un vrai appel RPC (pas seulement des appels ORM internes).

Le sujet « suite de tests », le déclencheur nommé et « y compris » lient la couverture RPC à l'exécution de cette suite. La lecture contractuelle normale exige que la commande QA exécute ces scénarios en RPC. Une formulation voulant agréger librement la suite ORM et une campagne RPC distincte aurait dû le dire explicitement.

Une ambiguïté d'intention demeure : l'analyste a pu vouloir simplement exiger des preuves RPC complémentaires, conformément au besoin initial. Cette intention possible ne supprime pas la portée de la phrase effectivement rédigée. Aucune clarification formelle antérieure à la réception ne remplace cette formulation dans les pièces examinées.

## Ce que prouvent les pièces

- qa_high_runtime/fragment.md et les logs qa_fresh/qa_update prouvent cinq tests verts, sur installation puis mise à jour. Le fragment affirme explicitement qu'aucun test HTTP/RPC n'existe dans la suite du module, que tous sont ORM TransactionCase, et ne déclare pas la composante RPC satisfaite par la suite.
- qa_client/fragment.md et ses logs prouvent des appels XML-RPC réels séparés à lab_client. La voie valide ses critères C02/C03/C04/C05/C07 ; elle exclut expressément C08 de son périmètre.
- La note C08 de coverage.json reconnaît que la composante RPC est portée par les journaux de la copie et non par les tests ORM.
- qa_synthese.md classe l'absence de test RPC dans la suite parmi les réserves non bloquantes, tout en annonçant 8/8/pass et aucun critère assoupli.

Toutes les pièces nécessaires au diagnostic existent ; il ne s'agit pas seulement d'une preuve oubliée. Le rapprochement de deux voies apporte les comportements RPC et la suite ORM verte, mais ne prouve pas que l'exécution de la suite QA couvre ces comportements en RPC. Le libellé reste matériellement intact ; sa portée d'exécution est réduite lors de l'agrégation des preuves.

C08 devrait donc être **partial** : composante suite verte prouvée, intégration des scénarios RPC à cette suite absente. Aucun test rouge ne justifie de le qualifier failed. Les sept autres critères peuvent rester acquis d'après leurs preuves examinées ; ce point interdit cependant la réception complète.

## Reprise technique et verdict global

state.json distingue déjà executed d'une qualification indépendante. Il documente l'interruption contrôlée, l'absence des anciens processus avant réattribution, le même environnement avant reprise, trois nouveaux testeurs terminés, les identités PostgreSQL/Git conservées, zéro réparation manuelle, les oracles SQL/RPC vrais et le nettoyage vérifié. Ces réussites ne sont pas annulées par l'erreur de réception de C08.

La conclusion de campagne appropriée est donc : **reprise et transport RPC démontrés ; qualification globale non validée à cause d'une couverture contractuelle surévaluée à la jointure**. Le flow a réellement enregistré pass et s'est terminé ; on conserve cet état comme observation, sans le réécrire pour rendre l'essai conforme.

Deux suites possibles pour une nouvelle réception : satisfaire C08 par des tests RPC réellement exécutés par la commande de QA, ou clarifier/amender explicitement l'exigence rédigée si elle surspécifie le besoin arbitré. Dans les deux cas, la décision et les nouvelles preuves doivent être tracées avant une nouvelle réception ; aucune interprétation rétroactive ne transforme cet essai en réussite globale. Cet arbitrage ne demande pas de rejouer les succès techniques déjà établis sans motif.
