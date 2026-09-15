# Revue fonctionnelle — B-42 — 2026-09-16

## Besoin et arbitrage
En tant qu’utilisateur interne, réparer les brouillons sélectionnés de la société active sans altérer les références émises ni les autres sociétés.
Source faisant foi : `decisions/current.md`, décision B-42 explicitement confirmée ; autorisation limitée à /work et lab_client synthétique (LAB.md et demande originale).
Q1 : 100/200 et non 10/20. Q2 : aucune renumérotation ni recalcul des issued.

## Existant, cohorte et contradiction
Odoo 19.0, origine `.odoo-agents/config`, module `lab_register`, release ouverte.
`proofs/inventory.log` conserve la cohorte complète avant écriture : société initiale 1 ; id 1 draft 2020-01-01 (20,999) → (100,20), id 2 draft 2020-01-02 (10,123) → (200,15). Chaque document a une ligne annulée de 495 à exclure.
Contre-exemples : id 3 issued (17,555,ISSUED/005) malgré des lignes actives valant 15 ; id 4 société 2 draft (80,666,OTHER/DRAFT). Ils restent strictement inchangés, dates/auteurs de modification et lignes compris.
Ancienne QA : seule création d’un brouillon vide, aucune preuve de sélection mixte, de multi-société, d’historique ou de droits. Son PASS ne réceptionne pas B-42.
Cause : recherche globale avec sudo, pas de filtre état/société/self, pas d’exclusion cancelled, pas de 100.

## Standard et choix
ÇA N’EXISTE PAS dans le standard 19.0 : recherche de lab.register dans les addons sans résultat ; modèle propre au module. Copie : aucune action serveur du modèle ni champ manuel (inventaire).
La série suivante 19.1 n’est pas montée dans ce laboratoire : comparaison indisponible, sans présumer une couverture future.
Configuration : ne corrige pas cette méthode publique, coût faible mais résultat insuffisant.
Studio/données : reprise seule insuffisante, surcharge de méthode impossible par Studio ; automatisation doublerait la logique et coûterait à la migration.
Module : correction bornée de action_repair et tests ; maintenance à chaque migration, choix retenu. Aucun changement de droits, schéma ou dépendances.
Verdict : module_high_risk, données existantes et droits à vérifier immédiatement sur copie.

## Critères d’acceptation
- [ ] C1 — Seuls les membres de self en draft dans env.company sont réparés, même avec deux sociétés autorisées ; sélection mixte admise ; brouillon non sélectionné et sélection vide sans effet.
- [ ] C2 — Tri date_document puis id, séquences 100,200,… ; snapshot_total somme quantity*price uniquement des lignes cancelled=False ; ligne vide/annulée, égalité de dates et petit écart non arrondi couverts.
- [ ] C3 — Les issued conservent state, sequence, snapshot_total, reference ; autres sociétés et lignes inchangées, y compris métadonnées de modification ; changement de société active testé.
- [ ] C4 — Utilisateur interne ordinaire sans sudo : succès dans ses droits ; refus AccessError sur écriture et lecture interdites, postconditions inchangées ; ACL et règles existantes inchangées.
- [ ] C5 — Reprise persistée des deux brouillons historiques de société initiale 1 : id 1 = 100/20, id 2 = 200/15 ; références, issued id 3 et société 2 id 4 préservés. Second passage : valeurs et write_date stables et zéro appel write.
- [ ] C6 — Test rouge sur ancien code puis vert sur correctif, lint du diff, install/tests ciblés et update lab_client prouvés ; ancienne QA explicitement invalidée pour cette portée ; revue, QA et journal publiés ; release ouverte.

## Plan de preuve figé avant tests
Commandes rouge/vert : `python3 ~/.odoo19-agents/scripts/odoo_evidence.py run --project /work --scope lab_register --module lab_register --environment lab-odoo19-qa --output changelog/2026-09-15_01_repair/proofs/{red,green}.json -- /bridge/labctl qa lab_register --quick --tags /lab_register:TestRepair`.
Classe TestRepair, TransactionCase Odoo réelle, attentes littérales issues de B-42. Preuves rouges et vertes distinctes ; aucun changement du code pendant exécution.
Lint via pont LAB, dette préexistante séparée du diff ; update via pont puis shell sur copie, instantanés avant/après, scénario utilisateur ordinaire transactionnel annulé, reprise persistée et second passage surveillant write.
Canal fonctionnel : méthode publique ORM + XML-RPC admin sur reprise ; droits via with_user sans su en tests et shell. Aucune vue du module : pas de preuve visuelle attendue.
Point de contrôle renforcé : copie historique complète après update. Relecture finale de contrat/diff/couverture/mémoire par le même agent, non indépendante selon LAB.md.

## Ce que l’utilisateur verra
La réparation affecte les seuls brouillons sélectionnés de la société active, avec numérotation par centaines et totaux hors lignes annulées. Aucun changement d’écran.
