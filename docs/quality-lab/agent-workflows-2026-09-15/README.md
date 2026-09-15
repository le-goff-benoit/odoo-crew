# Boucle agents : correctifs Odoo et réception

Campagne ouverte le 15 septembre, exécutée les 15–16 septembre 2026.
[Protocole figé](protocol.json) · [Calibration ORM](calibration.md) ·
[Extension PDF 18/19](pdf-cohorts.md).

## Point de départ

Les six parcours W01–W06 étaient des calibrations de contrôles. Les essais de
modèles légers portaient sur des réalisations Python ; ils ne démontraient pas
une accélération des développements Odoo. La campagne mémoire conservait deux
acceptations, une réserve et un rejet, sans nouveau passage après correction.

Cette campagne ajoute deux réalisations natives :

- **N06** : réparer des brouillons tout en préservant références déjà émises et
  autre société, reprendre les données existantes, vérifier l’idempotence et les
  droits d’un utilisateur ordinaire malgré une ancienne QA trompeuse.
- **N07**, réservé : préparation périodique, saisie manuelle à zéro, copie et
  reliquat. Vrais modèles ORM synthétiques ; ce cas ne qualifie pas `stock.picking`.

Les mécanismes sont issus de régressions récentes ; la correspondance aux projets
et documents clients reste dans le dossier privé local. Aucun fichier client
n’entre dans le corpus ou dans le contexte des agents du banc.

## Reproduire la boucle

```bash
python3 scripts/odoo_bench_agent_workflows.py baseline --output /tmp/nouvelle-boucle
# Examiner les deux N06, corriger les seules causes observées, commiter le candidat.
python3 scripts/odoo_bench_agent_workflows.py candidate --output /tmp/nouvelle-boucle --candidate <commit>
python3 scripts/odoo_bench_agent_workflows.py status --output /tmp/nouvelle-boucle
```

Huit appels natifs maximum, 900 secondes par appel, deux environnements isolés.
La deuxième commande réserve six appels : N06 candidat puis N07 référence/candidat.
Aucune reprise automatique ni appel modèle en CI. Les cas, correcteurs, helpers et
révisions sont figés. Un essai interrompu reste conservé ; une phase déjà commencée
ne peut pas être relancée silencieusement.

## Mesures et interprétation

Le runner conserve préparation, durée de l’agent, commandes, modèle/effort observés,
oracle indépendant et empreintes du code avant/après chaque contrôle. Lint, QA et
update doivent concerner les sources finales. Une erreur fournisseur ne devient
pas un succès parce que le CLI a aussi émis une fin de réponse.

La porte mécanique ne remplace pas la réception sémantique. Le délai jusqu’à
réception acceptée reste **non mesuré** tant que cette réception n’a pas eu lieu.
Un échec rapide n’est pas une amélioration. Les reprises des agents sont distinctes
des nouvelles variantes d’instructions de l’expérience. Ne pas additionner les
jetons d’entrée et le cache, ni transformer un coût manquant en zéro.

Statut de la comparaison native : en cours. Les résultats définitifs et la
décision d’adoption seront ajoutés après réception des artefacts immuables.
