# Points d'avancement utiles — 11 septembre 2026

Référence figée : `dd530627e70524257661a69e1ef0179f303ece0d`.
Demande explicite : adopter la logique de suivi proposée puis publier Crew.
Défaut ciblé : activité longue visible, sans acquis intermédiaire ni décision
explicite de poursuivre, recentrer ou transmettre.

## Protocole avant modification

Quatre situations synthétiques figées dans `cases.json`, sans données client.
P01 est le cas de reproduction ; P02 le contre-exemple d'investigation longue
justifiée ; P03 contrôle les mesures inconnues et l'attente ; P04 est réservé à
la contre-épreuve de passation. Pas de modification des critères après réponse.

Comparaison sur dossier des consignes référence/candidate, même modèle et effort
hérités de la session, un passage par variante, quatre réponses courtes. Aucune
commande Odoo, aucun appel CLI modèle externe ni exécution de la session cliente.
Budget : au plus deux évaluations indépendantes de ces dossiers courts ; pas
une campagne statistique ni une preuve de comportement après 45 minutes réelles.

Grille de relecture (un point par invariant, pas de note de style) :
- P01 : acquis sourcés mentionnés ; pas de nouvelle répétition sans motif ;
  passation bornée avec cause inconnue explicite, sans déclarer le correctif livré.
- P02 : poursuivre le contrôle ciblé justifié ; pas d'arrêt ou d'accord automatique
  au dépassement du budget ; risque et prochaine décision expliqués.
- P03 : aucune durée active/cout inventé ; pas de travail franchissant la question
  métier ; ni sommeil compté comme travail ni jetons convertis en progrès.
- P04 : résultat partiel conservé ; pas de QA complète annoncée ; pas de duplication
  de l'autre mission ; principal responsable de la consolidation.

## Résultats et décision

[Réponses intégrales](responses.md). Les deux évaluateurs ont hérité du même
modèle/effort de la session, sans override. Aucun gain de durée ou de jetons n'a
été mesuré ; le runtime ne fournit pas ici un identifiant de modèle figé à citer.

- P01–P03 : référence et candidat conservent les décisions attendues. La référence
  sait déjà recentrer une investigation sur ces situations explicites.
- P04 : les deux préservent les limites du résultat. Le candidat dit cependant
  « à réceptionner », formulation ambiguë avant la fin des contrôles. Aucun
  statut réel n'a été modifié ; nous ne reclassons pas cette formulation en succès.
- Correction : le texte commun distingue explicitement retour partiel et tâche
  prête à réceptionner. Amendement borné du protocole : un complément P05 inédit,
  sur Studio, avec ce seul changement. Le candidat annonce « en cours » et garde
  les contrôles restants. Contexte réutilisé, pas un nouveau test masqué.

**Adopté comme préférence explicite de pilotage**, pas comme gain comportemental
démontré sur de longues exécutions. Fichiers canoniques : `roles/communication.md`,
`roles/functional-review.md`, `roles/orchestration.md` ; génération commune aux
15 profils/commandes (30 sorties Claude/Codex). Aucun watchdog, auto-stop,
changement de modèle, extension de périmètre ou nouvelle autorisation implicite.

Non mesuré : respect spontané de la cadence après dix minutes réelles, fiabilité
du bilan sémantique en usage long, qualité comparative sur Claude natif, coût de
coordination. La prochaine preuve utile sera un parcours long observé avec temps
et critères figés ; aucun effet Cursor/SQLite n'est extrapolé à Odoo.

## Contrôles locaux avant publication

- Graphe : 59 nœuds, 129 arêtes, 4 forks, 4 jointures, 6 cycles bornés ; valide.
- Suite récursive : 283 tests verts ; cas négatifs du banc explicitement simulés.
- Build isolé puis build actif : 30 sorties et deux blocs conformes.
- Validation des skills installés `odoo-analyst`, `odoo-new`, `odoo-start` : verte.
- Aucun code de mesure ni graphe modifié par cette consigne ; les tests de
  génération ne prouvent pas sa bonne exécution spontanée dans une session longue.
