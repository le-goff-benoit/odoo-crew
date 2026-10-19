# Consultant unique et fiches d'apprentissage

## Résultat

L'entrée habituelle est `odoo-consultant`. Le principal applique les compétences
BA, conseil client/AM, expertise métier, configuration, développement, support et
QA dans la même session. La délégation exige une demande explicite. Les anciennes
commandes et les contrats des flows existants restent compatibles ; aucun garde
de réception indépendante déjà lié n'est désactivé.

Le pack Tricorder 0.4.0 ne propose que le consultant. Ses anciennes sections
restent présentes pour les workflows déjà configurés ; pas de migration automatique
des workflows externes. Les profils CLI historiques restent générés et disponibles.

Les procédures de conseil client distinguent estimation humaine et exécution IA,
préparation/reprise/ateliers/contrôles, hypothèses, responsabilités et réception.
L'expertise métier distingue comportement du code, configuration observée et
règle officielle, dans la série et le pays concernés.

## Mémoire

Les découvertes de release acceptées alimentaient déjà `LEARNINGS.json`.
Le nouvel export produit `.odoo-agents/learnings/index.json` et une fiche JSON
par apprentissage. `odoo_work.py prepare` le déclenche ; il est aussi utilisable
seul avec `odoo_learnings.py PROJET`.

Les fiches conservent l'origine, la portée, les exceptions et les preuves. Elles
signalent les apprentissages périmés et remplacés ; une proposition n'est pas
promue. Le registre et les contributions restent les autorités. Les notes
personnelles sont préservées. L'export ne copie rien entre clients et ne lance
aucun modèle. La promotion d'une règle générale conserve le parcours d'amélioration.

## Vérifications du 19 octobre 2026

Référence de départ : `75612ee195f08b5a764e5aac303d453741666457`.

- `python3 scripts/odoo_flow.py validate` : 59 nœuds, 129 arêtes, graphe valide.
- Suite complète `python3 -m unittest discover -s tests -v` : 442 tests réussis
  dans le build final. Une socket Unix de laboratoire nécessite une exécution
  hors du bac à sable restrictif ; aucun test n'a été ignoré pour contourner ce blocage.
- Six tests de fiches : proposition, portée/exceptions, idempotence, source
  périmée, remplacement, conservation de fichier personnel, traversée de chemin
  et reprise par `prepare`/release suivante.
- Build isolé puis installation locale : 40 sorties générées conformes, deux
  blocs d'aiguillage et pointeur personnel vérifiés ; `build.sh --check` réussi.
- Validation du skill `odoo-consultant` par `quick_validate.py` : réussie.
- `bash -n build.sh` et `git diff --check` : réussis.

## Limites et utilisation

Pas de campagne LLM comparative ni de validation native dans un Tricorder externe.
Les tests prouvent les contrats et la mécanique de mémoire, pas une expertise
universelle ou un gain mesuré de qualité des réponses. L'auto-relecture est
explicitement non indépendante. Aucun projet ou base client n'a été modifié.

Installation locale via le lien `~/.odoo19-agents` vers le checkout et `build.sh`.
Ouvrir une nouvelle session pour la découverte du nouveau skill ; les anciennes
sessions ne rechargent pas nécessairement leur catalogue. La PR doit être revue
avant fusion ; l'installation locale utilise le checkout de la branche de travail.
