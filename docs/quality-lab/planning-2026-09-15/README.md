# Plan construit par le principal — contre-épreuves sur dossier

Huit appels explicites et bornés à 90 s : Astra et Opus, effort medium, deux
corrections au maximum et un cas inédit réservé à la contre-épreuve. Les rôles,
entrées, protocoles, sorties et compteurs natifs sont conservés par étape.
Aucun outil ni projet client accessible dans ces essais sur dossier.

## Ce que l’essai a changé

Le cas initial combine deux hiérarchies de rapport contradictoires et deux
intentions de séquence indépendantes. Les deux principaux isolent la question du
rapport. Astra conserve les valeurs finales demandées. Opus généralise trop la
préservation d’ordre et ajoute des règles de cas limites ; sa première correction
produit aussi une pseudo-commande « test à ajouter ».

Deux précisions utiles sont ajoutées à la source canonique : distinguer données
intermédiaires et résultats finaux prescrits ; confronter chaque critère à sa
phrase source et séparer commande exécutable / fichier de test à créer. La seconde
version conserve la cible exacte chez les deux fournisseurs. Un cas limite non
tranché reste une question ou un contrôle du standard, sans règle de réception
inventée. Les sorties initiales restent conservées, sans les réécrire.

Le [cas inédit](holdout/case.txt) transpose le problème : deux états de tâche
contradictoires, seuil explicite de 90 %, aucune bascule de fournisseur/modèle,
absence de quota distincte de zéro. Les [sorties Codex](holdout/codex-answer.txt)
et [Claude](holdout/claude-answer.txt) conservent ces exigences, laissent la
contradiction ouverte et prescrivent commandes/cas/environnements.

## Décision et limites

**Adopté :** consignes de traçabilité et de comparaison avec la source, contrat
schema2, preuve de chaque commande/environnement et couverture des critères.
Le résultat a été relu par l’orchestrateur contre le protocole ; aucun score de
qualité général n’est déduit de ces exemples.

Les commandes proposées restent des prescriptions pour des tests à créer :
elles n’ont pas exécuté Odoo dans ce banc. Les outils vérifient les preuves lors
de la réception, mais ne remplacent pas l’arbitrage métier du principal. Une
planification native complète sur une vraie copie client reste un pilote futur ;
aucune promesse de suppression de toutes les reprises n’est faite.
