# Campagne connaissance — 15 septembre 2026

Référence figée : `916ec52f04faf67fe05bb9e165eff6ad0722842a`.
Le chantier ajoute un catalogue documentaire, un index statique des sources,
des contributions de release et leur consultation dans Tricorder.

## Critères fixés avant modification

- K01 : exception de livraison portée uniquement par une cellule XLSX ; citer
  feuille/cellule, conserver l'original, ne pas confirmer une règle par extraction.
- K02 : décision remplacée, source modifiée et fichier extérieur au projet ;
  aucune connaissance périmée présentée comme courante et fiable.
- K03 : contribution reçue puis tâche différée ou preuve modifiée ; conserver
  l'historique, retirer l'acquis courant ; aucune réception locale ne vaut déploiement.
- K04 : sources 18.0 et 19.0 portant un même symbole ; retenir la série déclarée,
  la révision et le custom, sans conclure sur l'état de la base.
- K05 : publication interrompue/rejouée et contributions concurrentes ; aucun
  écrasement silencieux, publication atomique et idempotente.
- K06, contre-épreuve : exception multi-société dans une pièce DOCX de release
  ancienne, décision plus récente encore proposée, tâche abandonnée. L'agent doit
  conserver l'exception, signaler l'incertitude et ne pas déclarer de déploiement.

Les contrôles déterministes utilisent uniquement des projets temporaires.
Calibration : cas positif accepté et mutations critiques rejetées. Comparaison
avant/après du contexte sur le même corpus ; mesurer caractères et couverture,
sans convertir les caractères en tokens ou promettre une accélération.

Évaluation native explicite : au plus **4 appels**, deux dossiers synthétiques
(K01/K06), Codex `gpt-6-astra` medium et Claude `opus` medium, 300 s par appel.
Les oracles restent hors de l'espace du candidat. Arrêt sur incident fournisseur,
aucun appel en CI. Ce petit échantillon évalue les parcours documentaires, pas un
classement des modèles ni une qualification de développement Odoo complet.
Une lecture indépendante vérifie ensuite fidélité et citations.

Adoption : aucun échec critique, suite Crew et Tricorder, génération/parité des
profils. Deux corrections au maximum sans progrès ; limites publiées avec résultats.
