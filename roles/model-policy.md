## Modèle par rôle

L’orchestrateur conserve toujours le modèle principal de la session, sur Codex
et Claude. Il définit les critères, les contrôles et les frontières de travail
avant délégation. Le quota restant ne change ni le modèle ni ces critères.

La politique canonique est `~/.odoo19-agents/workflows/model-policy.json`.
Avant une délégation qui change le modèle, résoudre le choix avec
`python3 ~/.odoo19-agents/scripts/odoo_models.py <codex|claude> <rôle> --risk <normal|high> --principal <modèle-de-session>`.
Les profils héritent du principal par défaut. `--candidate` désigne explicitement
un essai sur une tâche locale bornée : Terra/Sonnet pour dev, Studio ou support,
Luna/Haiku pour une exécution prescrite. Une commande déterministe suffit souvent
pour ce dernier rôle. Analyse ambiguë, QA décisionnelle, finance, droits et données
existantes restent au principal. Un modèle indisponible ne déclenche aucun repli
silencieux ; remonter la limite au principal.

Conserver dans le contrat le fournisseur, le modèle et l’effort demandés ; dans
le résultat, leur valeur observée, ou « non retournée ». Les candidats restent
expérimentaux tant qu’une comparaison avec cas inédit ne prouve pas la qualité
et le délai jusqu’à réception, reprises du principal comprises. Un test de modèle
n’autorise pas à réduire la QA. Un résultat partiel retourne au principal pour
réception ; le sous-agent ne lance pas son successeur.
