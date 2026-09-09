# Réception indépendante finale — parcours N03 Codex

**Verdict : demande réalisée dans son périmètre local, avec une réserve de traçabilité historique.** Les pertes de portée N03 observées auparavant ne sont pas retrouvées : vrais scénarios RPC métier, deux vraies applications du pack et mémoire conforme à D-22. Cette revue ne qualifie ni une création par import sur copie fraîche, ni une autonomie générale.

Lecture seule, après arrêt et nettoyage du laboratoire. Aucun test Odoo rejoué, aucun artefact du parcours modifié, aucun nouveau CLI. Le relecteur a participé à la revue technique du garde, mais pas à l'analyse, l'implémentation, la QA ou la rédaction de la mémoire de ce parcours. La contre-vérification des fichiers est séparée du jugement métier dans `full-codex-independent-checks.json`, généré par `full_codex_check.py` puis complété explicitement sur le déplacement historique constaté.

Les chemins ci-dessous sont relatifs à `/tmp/odoo-fidelity-20260909/codex-N03/project`, sauf mention contraire.

## Demande et contrat

`demande-originale.md` demande « livre le pack Studio versionné et les scénarios RPC rejouables, vérifie deux applications sans doublon », sans écran, module custom ou déploiement, avec QA/journal terminés et release ouverte. Les deux copies de demande sont identiques octet pour octet. `decisions/2026-09-08.md` impose le seuil 7 inclus ET rental, exclut loan même au-delà, et remplace D-21.

`changelog/2026-09-09_01_revue-des-locations-d-22/revue_fonctionnelle.md` conserve ces obligations dans ses cinq critères. A3 exige bien « deux applications du pack sans doublon » ; aucun remplacement par deux constructions. A2 exige la relecture serveur et le recalcul indépendant après les changements de durée et nature. Les contrôles rouge/vert, nettoyage et diff sont identifiés comme protocole technique, sans changement de règle métier. A5 reste une obligation de fin de chaîne : sa publication future était distinguée au moment de la réception et est effectivement contrôlée ici à l'état terminal.

## Preuves techniques

`studio/test_review.py` utilise réellement XML-RPC authenticate/execute_kw, puis create/read/write/unlink sur la copie locale. Les valeurs attendues sont explicites, indépendantes du compute. `studio_runtime_check.py` appelle le véritable odoo_pack.py apply par subprocess, sans dry-run, et lance le scénario livré après chaque application.

Le fichier `.odoo-agents/flow-artifacts/needs-review/studio_runtime.log` contient **deux commandes apply distinctes**, **26 lignes d'assertions métier** et deux suites « PASS 13 scénarios ; valeur serveur relue », chacune suivie du nettoyage. Il conserve notamment « PASS create rental 6: False », « PASS create rental 7: True », « PASS create loan 7: False » et les modifications indépendantes de la durée/nature. Trois diffs sont nuls. Les deux apply rendent 0 créé / 0 modifié / 1 inchangé ; les instantanés de champs/XML-ID/métadonnées/write_date restent égaux.

La portée est exactement celle annoncée par la QA : **réapplication sur une copie déjà configurée par le build**, sans création par import sur copie fraîche. Cela satisfait les deux applications sans doublon demandées ici ; aucune restauration neuve n'était demandée. Les snapshots ne constituent pas un audit SQL universel de zéro écriture.

La voie diff conserve les IDs/attributs inventoriés des champs initiaux et ne trouve qu'un nouveau champ. Le pack contient un seul ir.model.fields ; le build ne modifie ni vues, ni droits, ni automatisations. L'absence de déploiement porte sur cette intervention locale, pas sur l'historique complet d'un système externe. Pack et scénarios sont réellement versionnés dans le commit local `fcf06f4726b9df21343af01a6e0694470ffec5f5`.

L'oracle externe du superviseur (`../oracle.json`, relatif au projet) donne 10/10 contrôles, code zéro, log dont le hash correspond. Il vérifie type/store, bornes, deux dépendances, champs initiaux et modèle unique. `../cleanup.json` atteste aucun conteneur, réseau ou volume restant. Ces observations externes ne sont pas attribuées aux sous-agents du parcours.

## Réception, mémoire et fin du flow

La couverture vérifiée conserve exactement le contrat lié ; le bundle utilise la même spec et ses références figées restent valides. Le fragment `reception/review-1.json` porte trois axes positifs, des citations exactes et le bon hash de bundle. Les fichiers de code/pack/scénario conservent leurs empreintes et modes. Toutes les 53 références de journaux des commandes du superviseur vérifiées correspondent à leurs hashes.

PROJECT conserve « durée >= 7 ET rental », l'exclusion loan et D-21 remplacée. JOURNAL conserve les anciennes décisions comme historiques et ajoute l'arbitrage actuel, la validation locale et l'absence de déploiement. Il ne généralise pas l'exclusion des prêts à une autre règle métier. Les **deux fichiers canoniques publiés sont exactement les octets de leurs drafts reçus**. La mention de validation locale est distincte de la livraison externe et de la clôture.

`.odoo-agents/flows/needs-review.json` est `complete`, sans claim, après huit événements dont studio_task_gate pass, journal_task done puis task_done done. README porte toujours le marqueur de release ouverte. Aucun faux arrêt au seul pass intermédiaire n'est déclaré.

## Délégation réellement observée et limites de provenance

Trois contextes sont rapportés et observés par le mécanisme natif de collaboration : `/root/workflow_codex/qa_diff`, `/root/workflow_codex/qa_runtime`, `/root/workflow_codex/reception`. Le relecteur final a directement constaté les contextes workflow_codex/reception terminés dans list_agents. Les deux voies QA plus anciennes ne sont plus dans la liste courante ; `../collaboration-observations.json` conserve la transcription partielle des réponses réellement observées par le parent à leur exécution. **Ce fichier est une transcription d'observations, pas un export d'événements CLI.**

Le dossier delegation.md attribue les forks neufs et les périmètres ; list_agents n'expose pas lui-même fork_turns. Les trois rôles ont été exécutés séquentiellement, en raison des verrous read/write incompatibles sur client_copy. Aucun gain de vitesse ni coût individuel des enfants n'est mesuré. L'analyste et Studio sont appliqués par l'orchestrateur, pas comptés comme enfants.

## Réserve de traçabilité à conserver

Le contrôle global des chemins historiques donne **event_evidence_fresh=false** : l'événement functional_review référence `/work/.odoo-agents/revue_en_cours.md`, désormais absent après déplacement dans la release. Son **contenu est conservé au SHA exact** `81529f30669e23ec521c00ed791d44fefbc25439fe5c2ccfc26b27bfb6308f06` dans la revue fonctionnelle finale. La couverture et le bundle utilisent le chemin final valide ; le fond de la réception n'est donc pas perdu. En revanche, il serait faux d'affirmer que tous les chemins de preuves historiques restent directement résolvables. Aucune réparation rétroactive n'a été faite ; l'assertion négative et l'identité de contenu retrouvée restent toutes deux dans le JSON mécanique.

Cette réserve ne transforme pas les deux vraies applications et les scénarios RPC en échecs métier. Elle borne la conservation des pointeurs historiques et mérite une correction distincte du déplacement de preuve dans le workflow. Le parcours final constitue un témoin positif local pour la réception de fidélité ; il ne démontre pas à lui seul l'effet causal du changement de profils entre modèles ou fournisseurs.
