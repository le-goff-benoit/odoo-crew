# Q4 — versions et navigateur, 9 septembre 2026

Résultat borné : le même témoin ORM est exécuté en 18.0 et 19.0 ; le vrai parcours Chrome19 confirme la fiche et le résultat serveur. La contre-épreuve serveur volontairement fausse est rejetée après le même clic navigateur.

| Essai | Durée | Résultat Odoo | Verdict indépendant |
|---|---:|---|---|
| Initial 18 positif | 8.971s | 4tests,0échec | ORM conforme |
| Initial 19 positif | 26.504s | 5tests,0échec,mais navigateur SKIP | refusé, incident banc |
| Initial 19 mutant | 25.006s | 5tests,0échec,mais navigateur SKIP | contre-épreuve non exécutée |
| Reprise 19 positif | 17.226s | 5tests,0échec,Chrome+serveur prouvés | conforme |
| Reprise 19 mutant | 16.822s | 1échec/5tests,code1 | faux état serveur correctement rejeté |

Le lanceur initial montait `/var/lib/odoo` en tmpfs sans mode. Docker lui donnait root:root0750 ; l'utilisateur odoo100:101 ne pouvait créer son profil Chrome. Les diagnostics isolés avant/après prouvent le défaut de droits et le DOM produit avec `mode=1777`. Aucun changement dans les images partagées. La reprise utilise aussi un réseau Docker interne, sans port publié.

`runs/` conserve les trois exécutions originales et leur oracle original. Cet oracle refusait déjà le faux succès, mais son indicateur skip était trop étroit. `initial-reevaluation.json` relit exactement ces logs avec le détecteur corrigé. `replay/` conserve les deux nouveaux essais autorisés par amendement. `replay-reevaluation.json` impose en plus que le clic soit un message de console `.browser`, pas une chaîne présente dans le code JS journalisé. Les deux résultats restent corrects ; aucune réécriture de preuve initiale.

Le positif prouve : formulaire réel du témoin Browser witness, clic object action_confirm, statut Confirmed affiché, cache ORM invalidé, statut serveur confirmed et montant30. Le mutant prouve une assertion serveur échouée exactement sur confirmed != draft, après la même action UI. HTTP200 seul, code de sortie0 seul et Odoo0échec seul ne sont pas des validations navigateur.

Nettoyage vérifié dans les deux bilans `result.json` : zéro conteneur et zéro réseau correspondant au préfixe dédié ; bases temporaires détruites avec PostgreSQL tmpfs, aucun volume client. Sources18/19 uniquement lues, leurs empreintes sont conservées dans `source-evidence.json`. Les modules exécutés exacts sont sous chaque scénario/project. Les lanceurs initial, reprise et final sont conservés séparément.

Quatre tests déterministes de l'oracle passent. Ruff scripts/tests passe ; pour les fixtures Odoo, F401/B018 sont exclus (imports d'enregistrement et manifest dictionnaire), Odoo déclaré first-party. Pas de changement fonctionnel des fixtures après exécution. La recette globale dépôt est à consolider par l'orchestrateur.

Limites : un scénario synthétique, utilisateur admin, 18/19 seulement ; aucune qualification d'une base cliente, d'une version SaaS/17, des droits, de la robustesse statistique ou de la productivité des agents. Ces essais valident le transport navigateur et le témoin métier, pas une chaîne autonome LLM de bout en bout. Aucun appel LLM payant.
