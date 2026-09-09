# Revue des lanceurs et archives — 9 septembre 2026

Périmètre : scripts/odoo_qualify_rights.py, odoo_qualify_restore.py, odoo_qualify_versions.py et fixtures correspondantes ; archives evidence/rights, restore, versions. Aucun scénario rejoué, aucun appel Odoo ni CLI LLM, aucun fichier existant modifié pendant cette revue. La partie droits/restauration est relue par un agent distinct de ses auteurs ; la partie versions est une auto-revue par son auteur, et ne constitue donc pas une seconde revue indépendante.

## Constats sur les résultats archivés

277 entrées SHA vérifiées : droits 60, restauration 74, versions 143. Aucun fichier référencé manquant, aucune empreinte divergente, aucun chemin de manifeste sortant de sa racine. Le total compte des références, dont certaines répétées par des manifestes imbriqués.

Droits : l'oracle erroné du premier run est conservé avec status=error ; le second run conserve le témoin secure=true et le mutant secure=false. L'audit final du mutant observe réellement la valeur étrangère passée de 20 à 888 et les lignes importées en société étrangère ; le refus ne repose pas sur un incident quelconque. Le témoin conserve 20 et aucune importation étrangère. Les observations utilisateur ORM et XML-RPC sont distinguées des lectures administrateur. La réévaluation du premier run conserve son statut historique et corrige uniquement l'interprétation de faultCode=4.

Restauration : les trois scénarios ont des issues cohérentes (complet code0 ; dump absent code1 sans base ; update invalide code1 avec base inspectable neutralisée). Le ZIP contient réellement dump.sql, manifest.json et une entrée filestore ; l'ORM relit les octets attendus. Le restaurateur archivé est identique au script actuel. Le JSON Compose développé prouve réseau interne et aucune publication de port. Cleanup retourne0 et ne laisse aucun conteneur, volume ou réseau portant le label du projet.

Versions : les deux SKIP Chrome initiaux restent archivés et refusés. La reprise positive possède le message de console .browser et la confirmation serveur ; la contre-épreuve contient exactement l'assertion confirmed != draft après le clic. Les deux marqueurs ne sont pas assimilés à la seule présence du code JS dans les logs. Le montage tmpfs corrigé et le réseau interne concernent la reprise ; ne pas attribuer rétroactivement cette isolation interne au premier run, dont le lanceur conservé créait un réseau non interne. Aucun port publié dans les deux variantes. Les bilans de nettoyage ne recensent aucun conteneur ou réseau restant.

## Lacunes observées de traçabilité

1. Six fichiers périphériques de evidence/rights ne sont couverts par aucun manifeste interne présent : lint.log, RESULTS.md, briefing.txt, suite.log, oracle-reevaluation.json et project/.odoo-agents/config. Les preuves des deux runs sont couvertes ; le manifeste global final de campagne doit aussi couvrir ces compléments. Ce constat ne signifie pas qu'un fichier a été altéré.
2. L'archive restore contient le restaurateur, ses dépendances, le protocole et les sorties, mais ni copie du lanceur exécuté, ni seed.py/check.py. Le lanceur lit ces fixtures depuis le dépôt vivant (lignes119,148,150). identity.json conserve le HEAD de référence et le hash du restaurateur, sans identifier les éventuelles modifications non commitées du lanceur/oracle. La reconstruction exacte de la décision dépend donc du dépôt livré, contrairement au gel autonome des fixtures du banc droits. Le contenu des logs est cohérent, mais le gel de cette partie est incomplet.

## Limites concrètes du contrat mécanique, non faux verts observés

- Droits : import_own_succeeds ne vérifie que l'existence d'un résultat et la valeur de sa première ligne (oracle_orm.py:35, oracle_rpc.py:44). Le contrat parle d'identifiants et valeurs exacts ; l'oracle ne compare pas une liste complète d'IDs, noms et sociétés ni l'absence de ligne supplémentaire. Les final_rows archivés confirment ici les seules lignes attendues ; aucune importation superflue n'est observée.
- Droits : expectation_met du mutant accepte secure=false quelle que soit la condition fausse. L'exécution présente démontre effectivement une fuite de données, mais ce booléen seul ne suffirait pas à conclure à la réussite d'une future mutation si l'échec portait seulement sur une autre clause du contrat.
- Restauration : report.status est fixé avant le nettoyage et peut théoriquement rester pass avec cleanup en erreur. Le code de sortie final est néanmoins non nul dans ce cas ; le consommateur doit vérifier le code et le bloc cleanup. L'archive présente possède cleanup intégralement vert. source_unchanged désigne les invariants sélectionnés vérifiés, pas une identité exhaustive de toutes les données ; le README le précise. Le mot de passe administrateur n'est pas authentifié, limite également déclarée.

## Conclusion

Aucun faux vert observé dans les résultats finalement retenus, aucune incohérence de hash et aucun nettoyage échoué dans les archives examinées. Les corrections d'oracle et d'infrastructure restent visibles. Les résultats sont recevables pour leurs témoins synthétiques bornés ; aucune qualification générale des droits, de toutes les sauvegardes ou de toutes les versions n'en découle. Les lacunes de gel/archivage ci-dessus sont à traiter lors de la consolidation ; aucune nouvelle exécution métier n'est nécessaire pour constater ces limites.

## Suivi annoncé par l'orchestrateur

Après cette revue, l'orchestrateur annonce un manifeste global couvrant les six compléments droits et une correction du gel restauration : copie du lanceur exécuté et des oracles seed/check avant exécution, puis utilisation de ces copies. Une reprise séparée des trois scénarios est lancée sous `/tmp/odoo-qualification-restore-20260909-replay`. Au dernier contrôle du relecteur, son report.json n'était pas encore disponible : cette note atteste le suivi annoncé, pas un nouveau résultat vert. L'archive initiale et ses limites restent inchangées.
