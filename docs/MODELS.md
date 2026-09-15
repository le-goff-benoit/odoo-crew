# Modèles : héritage et essais par rôle

L'orchestrateur utilise le modèle principal de la session. Les rôles héritent de
ce modèle par défaut ; aucune réduction automatique liée au quota. La politique
exécutable est [model-policy.json](../workflows/model-policy.json), résolue par
`python3 scripts/odoo_models.py <codex|claude> <rôle> --principal <modèle> --risk normal`.

`--candidate` est un essai explicitement demandé sur une tâche locale bornée,
avec critères et outils fixés. Le catalogue ne garantit pas la disponibilité du
modèle dans un abonnement ; les CLI natifs restent l'autorité de l'essai. Une
indisponibilité est un incident distinct d'une erreur métier, jamais un repli caché.

| Domaine | Politique |
|---|---|
| Orchestration, ambiguïté, QA décisionnelle, finance, droits, données existantes | Principal |
| Développement, Studio, support bornés | Héritage ; Terra/Sonnet candidats expérimentaux |
| Exécution prescrite | Commande déterministe si suffisante ; Luna/Haiku expérimentaux |

La qualification compare dans un même fournisseur : mêmes cas/contrats/outils,
référence et candidat, ordre alterné, cas inédit figé avant correction, qualité,
durée jusqu'à réception et reprises comprises. Les jetons/cache sont observés
si retournés ; l'effort effectif inconnu n'est pas inventé. Un échec critique ne
se compense pas par la vitesse. Un dossier documentaire ou un outil Python ne
qualifie pas le développement Odoo ni une release complète.

Résultats et limites : [catalogue du laboratoire](quality-lab/README.md),
[premiers essais documentaires](quality-lab/models-2026-09-15/README.md).
Les essais natifs sont explicitement lancés, plafonnés et archivés ; aucun appel
payant pendant les tests ordinaires, la génération des profils ou la CI.

La [campagne d'implémentation Python](quality-lab/implementation-2026-09-15/README.md)
obtient huit réceptions acceptées, sans reprise. Les candidats demandés sont
plus rapides sur les deux tâches locales, avec tests exécutés et oracle séparé.
Deux cas et une répétition ne qualifient pas les autres rôles ou Odoo ; l'héritage
reste la règle. Le [profil QA compact](quality-lab/profiles-2026-09-15/README.md)
réduit le texte lu mais ne montre pas de gain de latence sur ces quatre paires.
