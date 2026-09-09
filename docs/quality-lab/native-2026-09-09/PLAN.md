# Campagne native et adoption des améliorations — 9 septembre 2026

Autorisation : poursuivre les propositions de l'analyse, modifier les profils sur
la base des essais, valider, installer et publier sur GitHub. Les mesures seules
ne constituent pas la livraison attendue.

| Étape | État | Preuve attendue |
|---|---|---|
| Relier les propositions aux changements | fait | `docs/IMPROVEMENTS.md` |
| Figer référence et dispositif du 8 septembre | fait | `9541bba` / `5868225`, archives de Git, profils réellement générés |
| Étalonner les contrats métier | fait | N01–N05 : réalisation correcte acceptée, mutation rejetée |
| Exécuter les workflows natifs | terminé avec réserves documentées | Revue, code/configuration, QA, copie, journal, flows, réponse finale |
| Développer les propositions restantes | qualifié | Plan/reprise, contexte sourcé, scénarios métier, clôture, assainissement, optimisations |
| Rejouer après correction des profils | fait | Comparaison et non-régression ; code produit non corrigé par le banc |
| Adopter les corrections justifiées | adoptées et installées | Décision par changement, défaut initial et preuve après |
| README, analyse, profils actifs, GitHub | livré, installé et CI verte | Build complet, CI, publication et vérification |

Le pont du banc conserve les vrais scripts QA de chaque variante ; les CLI
utilisent leurs outils natifs et les skills générés. Les rôles sont appliqués par
un même orchestrateur, sans délégation. Le navigateur, la production et les autres
séries ne sont pas mesurés par ces demandes. Les tests de l'outillage couvrent
séparément les nouvelles commandes et contrôles de clôture.

Incidents de banc conservés : réseau Docker interne sans port publié (corrigé par
un proxy de boucle locale vers la seule copie) ; archivage trop strict des liens
de virtualenv installé par l'agent (corrigé en excluant les dépendances locales
non livrables, pas les liens du code). Les essais interrompus par ces incidents ne
sont pas comptés comme défauts des modèles.

Rapport et décisions détaillées : [README.md](README.md).

Livraison : `959708f` sur `origin/main`, profils actifs régénérés et contrôlés
(26 fichiers, deux blocs et pointeur personnel). Les deux jobs Python 3.10/3.12
ont réussi : [CI de livraison](https://github.com/le-goff-benoit/odoo-skills/actions/runs/34301119016).
Les instructions générées remplacées sont sauvegardées localement ; aucun projet
client modifié. Ouvrir une nouvelle conversation pour charger les nouveaux profils.
