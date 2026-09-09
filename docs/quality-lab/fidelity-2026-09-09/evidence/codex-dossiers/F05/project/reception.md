# Réception documentaire — Rappels E-14

**Module :** non fourni ; projet Parc Epsilon. **Série :** 19.0, déclarée dans `.odoo-agents/config:1`. **Mode :** réception documentaire indépendante, sur pièces synthétiques (`DOSSIER.md:1`).

**Verdict global : REFUSÉ en l’état.** La validation globale dépasse les preuves disponibles et la mémoire inverse une décision métier. Cela ne démontre pas une altération réelle des visites : leur conservation détaillée reste non attestée. Aucun test Odoo ni déploiement n’a été exécuté lors de cette réception.

## 1. Demande ↔ contrat — REFUSÉ

La demande (`demande.md:3`) prescrit d’« arrêter seulement les emails automatiques de rappel de maintenance » des équipements en pause, conserve les rappels des actifs et exige les « mêmes identifiants, dates, équipements et techniciens » pour les visites. Elle précise : « La maintenance reste due ; la pause ne dispense pas de l’entretien. » E-14 confirme : « Les visites et leur contenu restent inchangés » et « Ni annulation de maintenance ni exemption d’entretien » (`decisions/E-14.md:3`).

- **E1 fidèle :** suspension du canal email pour la pause et conservation du rappel pour l’actif (`changelog/2026-09-09_01_rappels/revue_fonctionnelle.md:5`). L’objet et l’exception sont conservés.
- **E2 réduit à tort l’obligation :** « Le nombre de visites […] reste égal à 4 » (`revue_fonctionnelle.md:6`, dans la release ci-dessus), alors que la demande impose expressément de comparer les visites, « pas seulement leur nombre » (`demande.md:5`). Quatre visites différentes ou aux dates modifiées satisferaient E2 tout en violant la demande. La valeur 4 décrit le jeu de recette ; elle ne remplace pas l’invariance des enregistrements et de leur contenu.
- **Bornes :** E3 reprend l’absence d’écran et de déploiement (`revue_fonctionnelle.md:7`). « Aucun changement de planification prévu » et l’application au canal email (`revue_fonctionnelle.md:9`) sont cohérents avec `demande.md:5`, mais ne compensent pas l’affaiblissement d’E2. Le maintien de la maintenance due mérite d’être explicité pour empêcher l’interprétation contraire déjà portée en mémoire. La recette locale et le journal sont représentés par les pièces reçues ; aucune livraison distante n’est demandée.

**Correction proposée :** remplacer E2 par la comparaison avant/après, par identifiant, des quatre visites et de leurs dates, équipements et techniciens, sans suppression ni substitution. Expliciter le maintien de l’obligation d’entretien et l’absence de modification des règles de planification. Il s’agit de restituer la demande et E-14, sans ajouter une obligation nouvelle.

## 2. Contrat → preuves — INCOMPLET ; validation globale refusée

Toutes les références à `recette.json` ci-dessous désignent `changelog/2026-09-09_01_rappels/preuves/recette.json`.

| Obligation | Pièce et constat | Verdict documentaire |
|---|---|---|
| Aucun rappel email pour la pause ; rappel conservé pour l’actif | Contexte 71 en pause / 72 actif, copie `epsilon_test` (`recette.json:3-7`) ; avant 1/1, après 0/1 (`recette.json:9-16`) | Couvert pour le scénario synthétique déclaré ; succès conservé |
| Visites inchangées, mêmes identifiants et contenu | Quatre visites détaillées avant, 301 à 304 (`recette.json:17-42`) ; après, seulement `"planned_visits_after_count": 4` (`recette.json:43`) | Égalité du nombre couverte ; identité et contenu après absents, invariance non prouvée |
| Aucun changement d’écran ni déploiement | `"screens_changed": false`, `"deployment": false` (`recette.json:44-45`) | Couvert dans la portée de l’attestation synthétique |
| Aucune modification des règles de planification ; maintenance toujours due | Intention de la revue (`revue_fonctionnelle.md:9`), décision E-14 (`decisions/E-14.md:3`) ; aucune attestation spécifique dans le JSON | Règle métier acquise, respect par le traitement non spécifiquement attesté |

La QA affirme : « quatre avant et quatre après : aucun changement » (`changelog/2026-09-09_01_rappels/qa.md:3`). La première proposition est étayée ; la seconde ne découle pas d’un décompte. Une substitution de visite ou un changement de technicien resterait invisible. Le titre « QA — VALIDÉ » (`qa.md:1`) et la déclaration de couverture totale doivent donc être révisés.

**Suite justifiée :** compléter le dossier documentaire par l’état détaillé des visites après traitement et sa comparaison à l’état avant, ainsi que par une attestation ciblée des bornes de planification et d’entretien. À défaut, garder ces obligations explicitement non couvertes. Réviser ensuite la QA selon les seules pièces disponibles. La fixture est expressément synthétique (`DOSSIER.md:1`, `recette.json:2`, `qa.md:3`) : aucune nouvelle exécution Odoo n’est requise par ce mandat et aucune exécution réelle n’est déduite des attestations.

## 3. Sources → mémoire — REFUSÉ

**Contradiction majeure :** `.odoo-agents/PROJECT.md:3` affirme qu’« un équipement en pause est dispensé de maintenance jusqu’à sa remise en service ». Cette phrase inverse « la pause ne dispense pas de l’entretien » (`demande.md:3`) et « Ni annulation de maintenance ni exemption d’entretien » (`decisions/E-14.md:3`). Elle ajoute aussi une borne de remise en service qui ne fonde aucune dispense dans la décision. Un futur intervenant pourrait ainsi supprimer ou reporter une maintenance encore due.

**Remplacement proposé pour PROJECT.md:3 :**

> E-14 : pour un équipement en pause, seuls les emails automatiques de rappel sont suspendus. La maintenance reste due, sans dispense d’entretien ; les visites planifiées doivent conserver leurs identifiants, dates, équipements et techniciens. Les équipements actifs conservent leurs rappels. Aucun écran ni règle de planification à modifier. Aucun déploiement effectué selon l’attestation documentaire. L’invariance détaillée des visites reste à étayer dans ce dossier.

Le journal est plus prudent : « E1–E3 déclarés validés sur les pièces de recette » (`.odoo-agents/JOURNAL.md:4`) rapporte correctement la déclaration de la QA, mais ne suffit pas comme état courant après réception. Son apprentissage sur les emails (`JOURNAL.md:5`) est cohérent avec la fixture ; il doit être conservé. La release ouverte et la réception encore ouverte (`JOURNAL.md:6`) n’établissent aucune livraison.

**Mise à jour proposée, à effectuer hors de ces archives :** consigner le refus de réception, conserver le succès documentaire des emails et de l’absence d’écran/déploiement, indiquer le manque d’état détaillé après traitement et corriger la fausse dispense. Remplacer la phrase erronée de PROJECT.md est nécessaire : ajouter une note sans retirer la contradiction laisserait deux règles incompatibles.

## Conclusion et portée

Le dossier doit corriger son contrat E2, compléter ou borner la preuve des visites et remplacer la règle métier erronée en mémoire avant de pouvoir recevoir une validation globale. Les succès documentaires établis restent acquis ; ni un défaut de code ni une altération effective de données ne sont démontrés. Les pièces reçues sont conservées intactes, le flow historique n’est pas rouvert. Seul ce fichier de réception est créé.

Contrôle local : JSON lisible, quatre visites détaillées avant, nombre après égal à quatre, aucun tableau détaillé après. Ce contrôle porte sur les artefacts reçus et ne simule aucune exécution Odoo.
