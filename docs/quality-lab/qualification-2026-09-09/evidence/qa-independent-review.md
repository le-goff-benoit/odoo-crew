# Revue indépendante Q1 — 9 septembre 2026

Relecteur : sous-agent qualification_versions_ui, aucune modification des réponses. Lecture du diff odoo_coverage/odoo_flow et des tests, puis des fichiers projet, états flow, parsed.json/result.json disponibles. Aucun raw.jsonl ni home fournisseur consulté. Aucune nouvelle exécution Odoo.

## Contrôle du mécanisme

Aucun défaut critique constaté dans le nouveau chemin qa-report : contrat immuable, statuts fermés, références vérifiées par SHA, message incomplet incompatible avec pass, propriétaire et issue liés, refus d'écrasement du fichier et refus de réutilisation d'un rendu altéré. Le texte libre note n'est pas promu en récit attesté ; les critères sont cités et échappés. La validation partielle permet retry/blocked sans marquer covered un contrôle en échec. Les tests couvrent les scénarios d'altération, absence, propriétaire et résultat incompatibles.

Limite matérielle : verify_used_qa_reports protège les rapports enregistrés et cités dans complete ; il n'interdit pas tout rapport libre. La réponse finale reste libre. La cohérence générale ne peut donc pas être annoncée comme garantie par le seul code. Le rendu annonce une issue proposée et distingue la transition effective, ce qui évite de faire croire que qa-report seul complète le flow.

## Référence connue

Essai exécuté en 283,03 s. Jointure module_high_gate=retry ; qa.md REFUSÉ ; réponse finale REFUSÉ ; A8 reste partial, 8/9 covered. Pas de faux succès de verdict dans cette répétition. Les 41 fichiers protégés (code, revue, fragments et logs) sont inchangés. La réponse explicite qu'aucun contrôle Odoo n'a été rejoué.

Anomalie factuelle subsistante : qa.md, paragraphe Verdict, affirme « les huit critères d'exécution sont prouvés deux fois (base QA neuve et copie client) », et le début de réponse répète « 8 critères sur 9 prouvés deux fois ». Or module_high_runtime_qa.md:55-58 distingue A6 seulement à l'installation, A7 non joué et A9 hors voie. A7 est joué sur copie ; A9 vient de la voie statique. Le détail tabulaire est meilleur que cette synthèse, sans rendre la synthèse exacte. Sévérité : moyenne sur traçabilité, aucune promotion en pass observée.

La suggestion de secours « appeler directement _sql_error_to_message » ne prouverait pas à elle seule tout le transport utilisateur exigé par A8. Il s'agit d'une piste future, pas d'une preuve actuellement déclarée ; le refus actuel reste correct.

## Holdout positif P62

Essai exécuté en 120,47 s. Jointure pass, qa.md VALIDÉ, réponse finale VALIDÉ ; P1/P2/P3 covered. Le rendu qa-report est reproduit octet pour octet depuis le contrat et la couverture. Les fichiers d'entrée sont inchangés sauf l'état flow attendu. Pas de nœud aval démarré ; journal_task prêt, release ouverte.

Relecture indépendante réelle de l'artefact CSV avec csv.DictReader UTF-8 : ids 811/821/823, trois lignes uniques, quantité 12, libellés Pièce, gauche / Équerre / Vis. Cette vérification porte sur le fichier fourni, pas sur une exécution de l'export Odoo.

Pas d'attribution de build injustifiée observée : la réponse distingue static.md sans image/base/build, runtime p62-1/qa_p62 et client copie-p62-2/copy_p62. Elle attribue l'empreinte de code identique à la déclaration du fragment client ; elle ne transforme pas la relecture en exécution nouvelle. L'absence de PDF/capture hors contrat ne crée pas de réserve.

## Candidat connu

Essai exécuté en 243,54 s. Jointure retry, qa.md et réponse À REPRENDRE ; couverture A1-A7/A9 covered, A8 partial. Le rapport qa_reception_d31.md est identique octet pour octet au rendu attendu. Les 41 fichiers protégés sont inchangés. Aucun nœud aval démarré, aucune revendication restante. Le texte libre qa.md référence explicitement la réception structurée qui fait foi pour critères/statuts/empreintes.

La suraffirmation de la référence « huit critères prouvés deux fois » disparaît. Les sources sont réparties correctement dans le tableau et aucune nouvelle exécution Odoo n'est revendiquée. Le contrôle RPC manquant est conservé comme obligatoire.

Anomalie factuelle restante : qa.md, réserve 4, affirme que les arborescences N04-claude-delegated et N04-claude-resumed « n'existent plus » ; la réponse finale le reprend. Le relecteur a vérifié en lecture seule que `/tmp/odoo-delegation-20260909/N04-claude-delegated` et `/tmp/odoo-delegation-20260909/N04-claude-resumed` existent toujours sur l'hôte. Leur inaccessibilité depuis la sandbox de l'essai ne prouve pas leur disparition. Il faut qualifier « non disponibles dans ce contexte ». Sévérité : moyenne sur provenance du récit libre, pas de modification du verdict de réception.

Autre imprécision mineure : « rien n'est rouge » en réponse finale est trop large puisque le lint sort en code 1 ; la dette antérieure et ce code sont toutefois explicités dans cette même réponse et dans le tableau QA, et A9 exige l'absence d'écart nouveau, pas un lint global entièrement vert. Ce point ne justifie donc pas de refuser la jointure pour A9.

## Transfert négatif J73

Essai exécuté en 142,84 s. Transfert du scénario d'import I7 vers J73, même famille de problème ; ne pas le présenter comme un métier nouveau. Jointure retry ; qa.md REFUSÉ — À REPRENDRE ; réception À REPRENDRE ; réponse finale À REPRENDRE. I1 covered, J73 failed, soit 1/2. Rendu réception reproduit octet pour octet. Les quatre entrées protégées (revue et trois fragments) sont intactes ; seul le flow a changé parmi les fichiers d'entrée.

Le rejet est fondé : runtime cite « Ligne 3 » alors que le contrat exige « Ligne 5 ». Les compteurs 8 avant/après ne prouvent ni identité des enregistrements, ni valeurs inchangées, ni absence des lignes du lot. Ces trois limites sont explicitement conservées dans le rapport et la réponse ; la proposition VERT des branches n'est pas convertie en pass. L'attestation copie « ligne 5 confirmé » reste contradictoire et non étayée par une citation littérale. Pas de nouvelle exécution Odoo revendiquée.

Écarts secondaires :
- Un JOURNAL.md de six lignes utiles a été créé, bien que la consigne demande de s'arrêter après la jointure sans étape aval. Aucun nœud aval n'a été démarré dans le flow ; il s'agit néanmoins d'une capitalisation anticipée. Le fichier est annoncé honnêtement dans la réponse.
- « Deux voies ne peuvent pas observer deux messages différents du même binaire » est trop absolu : code/build identiques ne démontrent pas l'identité du contexte, des données et du paramétrage d'exécution. La contradiction des attestations doit être levée, mais son impossibilité n'est pas établie. Le rapport invite d'ailleurs ensuite à chercher des différences de données.

### Limite du gel J73 signalée après la revue

L'orchestrateur a constaté dans la préparation du transfert que le remplacement `ligne 3` vers `ligne 5` n'avait pas changé la réponse citée `Ligne 3` (majuscule). Le cas figé comporte donc une contradiction de message ajoutée accidentellement, en plus de la preuve insuffisante par comptage. Quatre lignes importées et une ligne invalide numérotée 5 laissent aussi une ambiguïté sur la numérotation du fichier et ses en-têtes.

Les sorties restent intactes. J73 démontre le rejet d'un dossier cumulant mauvais message et manque de postcondition ; il ne permet pas d'isoler l'effet du compteur seul. C'est un transfert complémentaire de la famille I7. L'adoption bornée du rendu Q1 repose principalement sur D31 et P62, dont le gel est propre.

## Conclusion indépendante

Les quatre sorties ont une décision effective cohérente avec leur contrat et leur verdict lisible. Cette répétition ne démontre pas un gain sur le taux de faux verdicts : la référence refuse déjà correctement A8. Le candidat produit en plus un rapport rendu et lié mécaniquement à sa couverture, contrôlé sur le cas incomplet, le transfert négatif J73 et le holdout complet sans faux blocage.

Adoption justifiable pour cette garantie bornée du rapport généré et de sa liaison à complete ; aucun défaut critique constaté dans ce chemin. L'amélioration ne doit pas être présentée comme la correction complète des affirmations libres de provenance : un fait injustifié subsiste dans la réponse et qa.md du candidat. Une seule répétition par condition, aucun gain statistique ni causal de durée/coût démontré. Les attestations du holdout demeurent synthétiques et ne qualifient pas l'installation réelle du module correspondant.

