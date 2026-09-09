# Réception indépendante — 09/09/2026

**Module :** `lab_rental` · **Série :** 19.0, origine : manifest `19.0.1.2.0`, corroboré par `.odoo-agents/config:1` · **Mode :** réception documentaire sur archives.

**Verdict global : REFUSÉ en l'état documentaire.** La réalisation locale D-03 et ses résultats techniques sont étayés. La demande exige aussi de reprendre la mémoire : celle-ci contient encore une consigne D-02 active, une confusion sur le prix des prêts et des généralisations historiques injustifiées. Il faut corriger ces formulations, sans invalider les tests D-03 ni les rejouer pour cette seule raison.

Seul ce fichier est créé. Aucun fichier reçu, flow, code ou journal n'est modifié. Aucun test Odoo ni script d'archive n'est exécuté. Les chemins historiques ne sont pas des environnements disponibles. `LAB.md:2-4` décrit un projet synthétique et des appels Odoo historiques ; leurs résultats sont cités comme preuves archivées, jamais comme des exécutions faites pendant cette réception.

Conventions : `R/` = `changelog/2026-09-09_01_frais-de-preparation-des-locations/` ; `P/` = `.odoo-agents/flow-artifacts/frais-preparation-d03/`. Les références ci-dessous sont relatives au projet reçu.

| Axe | Verdict | Motif |
|---|---|---|
| Demande ↔ contrat | À corriger dans les formulations et la portée | Formule D-03 fidèle ; exclusions, hypothèses et rédaction sur les prêts à préciser |
| Contrat → preuves | Acquis techniques D-03 conservés | 12 tests, reprise, stabilité et périmètre documentés ; limites de preuve ci-dessous |
| Sources → mémoire | REFUSÉ | D-02 encore prescriptive, gratuité erronée, historique et obligations extrapolés |

## 1. Demande ↔ contrat

La demande originale (`demande.md:1`, également `R/demande.md:1`) exige le « total calculé et stocké », « sans changer les écrans ni facturer », les « tests métier et la QA de tâche puis le journal » et une release ouverte. Le complément `R/demande.md:7` précise « D-03 remplace D-02 », « jours × tarif inchangé » et « Reprends le travail et la mémoire dans la release ouverte ».

`decisions/2026-09-09.md:1` fixe « + 15 EUR si type=location ET jours >= 5, sinon jours × tarif_jour », « Prêts exclus » et « Validation locale seulement ; aucune production ni déploiement ». `decisions/2026-09-08.md:1` apporte les contraintes non contradictoires : « Montants hors taxes, une seule monnaie EUR, aucun arrondi supplémentaire », valeurs positives ou nulles, absence de changement de droits, comptabilité et documents historiques ; « Tous les enregistrements du bac sont des essais modifiables ».

| Obligation / portée | Contrat reçu | Appréciation |
|---|---|---|
| Total automatique et stocké de `lab.rental`, utilisé par le gestionnaire | `R/revue_fonctionnelle_point2.md:17`, `:84`, `:88-92` | Fidèle ; aucune demande de canal graphique nouveau ou d'acteur supplémentaire |
| +15 fixes une seule fois, locations ≥5 inclus ; sinon produit jours × tarif | `R/revue_fonctionnelle_point2.md:76-77`, `:88-90`, critères `:114-124` | Fidèle, y compris 4 jours sans forfait, tarif nul et prêts sans forfait |
| Pas d'écran, facturation, droits ou comptabilité | `R/revue_fonctionnelle_point2.md:18`, `:94-110` | Fidèle ; le vocabulaire « prêt payant » au critère C06 est toutefois faux, voir B2 |
| HT, EUR, aucun arrondi supplémentaire, domaine non négatif | D-02 précitée ; revue initiale `:55-56`, modèle conservé selon revue point 2 `:84` | Contraintes à maintenir explicitement dans la synthèse actuelle ; D-03 change le forfait, pas tout le contrat |
| Essais locaux modifiables, aucun document historique réel modifié | Revue point 2 `:73-75` : « Rétroactif sans réserve » ; `:110` exclut « application sélective à des documents historiques » | Acceptable pour toutes les lignes du bac autorisé ; aucune autorisation de reprise générale de documents réels n'en découle |
| Tests, QA et mémoire, release laissée ouverte ; aucun déploiement | `R/README.md:1-7`, point 2 `:14`, QA et journal | Travail technique documenté, release ouverte respectée ; mémoire non conforme, portée locale à rendre explicite |

**Qualification des ajouts de la revue.** Le forfait à tarif nul et l'exclusion des prêts à toute durée sont des conséquences de la formule, pas des besoins ajoutés. Constantes nommées, choix custom, `Float` et nouvelle migration versionnée sont des choix techniques adaptés au modèle existant. La reprise de tous les essais locaux et C12 constituent une conséquence justifiée du stockage et de l'autorisation du bac. L'idempotence des montants (C13) est un critère supplémentaire de qualité, effectivement documenté ; il ne faut pas le retirer après coup.

L'interdiction absolue de mentionner D-02 dans une communication (`R/revue_fonctionnelle_point2.md:141-142`, `R/README.md:40-41`) est une consigne éditoriale ajoutée par la revue, non une décision client. Présenter D-03 comme résultat courant est justifié ; faire de cette préférence un interdit universel ne l'est pas. Le paramétrage « si une troisième révision arrive » (`R/revue_fonctionnelle_point2.md:41-42`) reste une suggestion conditionnelle, non une nouvelle tâche autorisée.

La positivité est interprétée comme domaine d'entrée dans `R/revue_fonctionnelle.md:56`. La demande ne prescrit pas explicitement un mécanisme de rejet des valeurs négatives : pas de défaut fonctionnel déduit de l'absence de contrainte. En revanche, dire qu'une contrainte impose nécessairement un changement d'écran est une justification trop générale ; maintenir clairement l'hypothèse de domaine.

## 2. Contrat → preuves : résultats conservés

Vérification locale des empreintes : les **11 artefacts uniques** référencés par `P/coverage.json` correspondent tous à leurs SHA-256 déclarés. La revue initiale correspond également à l'empreinte `a8463954…` de `R/qa_rapport_tache1.md:9`. Une empreinte confirme l'intégrité des pièces reçues ; elle ne transforme pas cette réception en nouvelle exécution ni en certification de déploiement.

| Contrôle / critères | Preuve et citation | Conclusion exacte |
|---|---|---|
| Lint | `archives-execution/bridge-019.log:3,13-15` : « All checks passed! », « 0 erreur(s), 0 avertissement(s), 0 info(s) » | Succès archivé ; 9 conseils de séparateurs restent visibles `:6` |
| Installation et tests D-03, C01–C11 | `bridge-020.log:241,256` : « 0 failed, 0 error(s) of 12 tests », `install=ok`, 23 s | Succès archivé sur base QA neuve |
| Update et tests D-03 | `bridge-021.log:48,63` : même bilan 12 tests, `update=ok`, 8 s | Succès archivé sur base QA existante |
| Oracles métier | `lab_rental/tests/test_preparation_fee.py:29-63`, `:67-79`, `:83-103` | 3 j=30 ; 4 j=40 ; 5 j=65 ; 7 j à 20=155 ; prêts=50/100 ; zéro=0 ; tarif nul=15 ; changements de durée/type et forfait fixe vérifiés |
| Stockage et calcul | `lab_rental/models/business.py:19` : `store=True` ; `:23-26`, `:43-44` | Champ stocké et dépendances des trois entrées conservés ; calcul sans arrondi ajouté |
| C12, reprise depuis D-02 | `bridge-022.log:14-22` : 19.0.1.1.0 et montants D-02 ; `bridge-023.log:17` : « Running upgrade [19.0.1.2.0>] post-migrate » ; `bridge-024.log:14-22` | Les conditions composées sont présentes : 52→40, 152→155, 12→15 ; location 3 j, location vide et deux prêts inchangés |
| C13, seconde mise à niveau | `bridge-026.log:14` : « STABLE_APRES_2E_UPDATE True [] » | Stabilité après update ordinaire, pas preuve isolée de rejeu du post-migrate |
| C13, rappel du corps de la reprise | `.odoo-agents/shell/reprise_idempotence.py:9-15` et `bridge-027.log:14-15` : « REPRISE_REJOUEE_SANS_ECART True {} » | Stabilité exacte des montants après rappel explicite ; complète correctement la première mesure |
| C14, périmètre | `bridge-026.log:16-19` : vues/actions/menus/règles=0, accès, sept champs, dépendance `base` ; `P/diff.patch` et `P/qa_high_static.md:16-28` | Aucun ajout demandé hors périmètre ; CSV d'accès et migration 19.0.1.1.0 identiques à la copie historique D02 |
| XML-RPC et nettoyage | `bridge-029.log:1` : location 4 j=40, 5 j=65, prêt 5 j=50 ; `bridge-030.log:1`, `bridge-031.log:1` | Création/lecture des bornes et retour aux sept essais ; aucune preuve de rendu visuel ou de droits non-admin |

Les 14 critères de résultat sont donc étayés dans cette portée, avec la correction sémantique de C06 ci-dessous. Pour C09/C10, les tests observent le champ via l'ORM après mutation ; ils ne constituent pas une relecture SQL indépendante après changement de durée/type. Le stockage est corroboré par la définition du champ et les lectures depuis des processus distincts pour les scénarios de reprise/création. Ne pas présenter ces canaux comme une recette navigateur.

La formulation « n'écrit aucun autre champ » de `R/revue_fonctionnelle_point2.md:102-103` et `P/qa_high_static.md:18` excède les seules mesures de montants : le script d'idempotence ne compte ni écritures ni effets automatisés. Le code cible uniquement le recalcul d'`amount_total`, et les entrées métier relues restent identiques ; ne pas étendre cela en garantie universelle de zéro écriture ou d'absence d'effets automatiques. Aucun critère reçu n'impose zéro écriture au second passage : C13 porte sur « aucun montant ne change », et cette condition est documentée.

Restent hors de cette réception : rendu graphique, utilisateur non-admin, chemin direct 19.0.1.0.0→19.0.1.2.0, clôture et déploiement. `R/qa.md:104-110` distingue déjà ces limites. Elles ne justifient pas de demander aujourd'hui une nouvelle recette pour corriger la mémoire.

## 3. Sources → mémoire : corrections nécessaires

### B1 — Une consigne D-02 reste active dans le suivi courant

**Sources :** D-03 (`decisions/2026-09-09.md:1`) prescrit 15 EUR dès 5 jours. `R/revue_fonctionnelle_point2.md:139-142` décrit correctement +15 à partir de 5 jours par rapport à l'avant-release, les 4 jours et prêts inchangés.

**Mémoire opposée :** `R/README.md:44-45` : « seul le montant total des locations de 4 jours et plus augmente de 12 EUR » puis « C'est le seul point à expliquer dans la communication ». Cette dernière note est prescriptive, sans étiquette historique, malgré les marqueurs corrects de péremption aux lignes 13 et 34-41.

**Conséquence :** une préparation de communication depuis la dernière note reproduirait la règle remplacée. **Correction proposée :** remplacer cette consigne courante par : « Aucun écran ajouté. Par rapport à l'état avant release, +15 EUR pour les locations d'au moins 5 jours ; locations de 4 jours ou moins et prêts inchangés. Validation locale seulement. » Conserver D-02 comme historique identifié, pas comme instruction de livraison.

### B2 — L'exclusion du forfait devient gratuité du prêt ou absence de facturation de base

**Sources :** D-03 conserve `jours × tarif_jour` dans le cas sinon ; `R/demande.md:7` dit « jours × tarif inchangé ». `bridge-029.log:1` donne un prêt de 5 jours à 10 = **50**, et `bridge-031.log:1` un prêt de 10 jours = **100**.

**Textes opposés :** `.odoo-agents/PROJECT.md:5-6` qualifie le prêt de « toujours gratuit quelle que soit sa durée » ; `R/revue_fonctionnelle_point2.md:119` et `P/coverage.json:99` expliquent pourtant 100.0 par « aucune durée ne rend un prêt payant ». `PROJECT.md:21` dit « aucune location de 4 jours facturée » ; D-03 donne **40** à 4 jours et interdit toute facturation pour l'ensemble de la tâche, pas uniquement cette durée.

**Correction proposée :** « Les prêts sont toujours sans frais de préparation ; leur total reste jours × tarif_jour. Une location de 4 jours ne porte aucun forfait. Aucun mécanisme de facturation n'est ajouté. » La gratuité figurait déjà dans `historique/D02/.odoo-agents/PROJECT.md:6` : défaut hérité que la réception de la mémoire doit signaler, sans l'attribuer au code D-03. Les valeurs des tests sont correctes ; seules les explications sont à réparer.

### B3 — La dernière décision est présentée comme effaçant tout le contrat ancien

**Sources :** le complément D-03 remplace le seuil et le forfait, maintient les prêts exclus et le produit jours × tarif. D-02 documente aussi HT/EUR, aucun arrondi supplémentaire, le domaine non négatif et les exclusions de droits, comptabilité et documents historiques.

**Mémoire opposée :** `PROJECT.md:10-11` : « c'est la seule qui fasse foi. Les fichiers plus anciens et le journal décrivent des règles mortes » ; `:33-34` : « prendre le plus récent ». Cette règle de lecture fait perdre les clauses antérieures non contradictoires ; HT/EUR subsistent `:8`, mais pas toutes les limites dans une synthèse actuelle complète.

**Correction proposée :** identifier les clauses remplacées et conserver explicitement les clauses inchangées, leurs sources et « validation locale seulement ; aucune production ni déploiement ». La date seule ne remplace pas un arbitrage explicite. Borner « Rétroactif sans réserve » (`R/revue_fonctionnelle_point2.md:73`) aux essais autorisés du bac, sans généraliser à des documents clients réels.

### B4 — Chronologie inventée et suggestion conditionnelle transformée en suite acquise

**Sources :** le journal date D-01 du **01/08/2026** (`.odoo-agents/JOURNAL.md:3-4`), D-02 du **08/09**, D-03 du **09/09**. La revue point 2 `:41-42` propose le paramétrage « si une troisième révision arrive » ; `R/README.md:42-43` dit correctement « Deux révisions […] en deux jours » et maintient cette condition.

**Mémoire opposée :** `PROJECT.md:25` : « la règle a été réécrite trois fois en deux jours » ; `JOURNAL.md:45-46` : « est à reproposer (3ᵉ écriture de la règle en 2 jours) » ; `P/qa_high_static.md:32-33` répète ce motif, et `P/compte_rendu.md:25` rend la proposition inconditionnelle.

**Correction proposée :** « D-01 est connue par le journal du 01/08 ; D-02 et D-03 sont les deux décisions des 08 et 09/09. Le paramétrage reste hors périmètre ; suggestion à réexaminer si une nouvelle révision arrive ou si le client le demande. » Aucune tâche de paramétrage n'est justifiée par une troisième modification fictive.

### B5 — Confusion entre statut historique, validation et livraison

**Sources :** le journal ancien dit uniquement « Ancienne conception » et D-01 remplacée (`JOURNAL.md:3-4`). Les logs établissent les validations et reprises locales D-02/D-03 ; D-03 interdit production et déploiement. `historique/D02/` fournit un état archivé, pas l'historique Git complet.

**Mémoire opposée :** `PROJECT.md:19` affirme D-01 « jamais livrée » sans preuve de livraison ou non-livraison ; `:18` cite un « historique git » qui n'est pas fourni dans cette copie. `JOURNAL.md:38-40` appelle la QA précédente « fausse » sans borner ce jugement aux attentes devenues incompatibles.

**Correction proposée :** « D-01 : ancienne conception connue par le journal, statut de livraison non établi par les pièces. D-02 : réalisée et validée localement, désormais remplacée ; état et preuves archivés disponibles. D-03 : validation locale documentée, release ouverte, aucun déploiement autorisé. » Dire que les anciens oracles +12/≥4 sont périmés pour D-03, pas que leur succès historique ou toutes les preuves techniques sont faux. La mémoire peut recommander de présenter le résultat courant dans une communication, sans inventer un interdit client de raconter l'historique.

## Suites concrètes

1. Dans une future version documentaire, remplacer les formulations B1–B5 aux endroits signalés, y compris le README courant ; un simple ajout D-03 au journal ne suffit pas. Maintenir les archives reçues intactes.
2. Conserver les succès techniques D-03, les empreintes et la distinction entre stabilité des montants et zéro écriture. Corriger les libellés de prêt sans changer leurs valeurs attendues.
3. Faire relire la mémoire corrigée contre les mêmes décisions et preuves. **Aucun nouveau test Odoo requis pour ces corrections documentaires.** Garder la release ouverte ; confirmation de l'auteur du manifest et recette de clôture restent les suites déjà consignées, sans déploiement dans ce mandat.

**Conclusion :** règle D-03 et validation locale étayées ; réception documentaire refusée jusqu'à correction de la mémoire et des formulations de contrat signalées. Aucun défaut de calcul D-03 démontré, aucune autorisation de production déduite.
