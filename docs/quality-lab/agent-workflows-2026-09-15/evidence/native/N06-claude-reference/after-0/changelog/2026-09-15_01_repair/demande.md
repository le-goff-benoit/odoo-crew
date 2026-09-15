# Demande

<!-- Copier chaque demande telle quelle, datée. Ne pas reformuler. -->

## 2026-09-16 — demande reçue (verbatim)

Applique /odoo-new : répare action_repair de lab.register et les brouillons existants de la société initiale de la copie synthétique. Contrat arbitré dans decisions/current.md. Autorisation locale seulement. Conserve un test rouge puis vert, prouve la reprise idempotente et les droits sous utilisateur ordinaire. Relis la QA existante trompeuse, publie revue, QA et journal ; laisse la release ouverte.

## Contrat arbitré — decisions/current.md (verbatim)

Décision B-42 confirmée : action_repair agit uniquement sur les enregistrements de self en état draft appartenant à la société ACTIVE env.company, même si l'utilisateur a accès à plusieurs sociétés. Elle trie ces brouillons par date_document puis id et leur affecte sequence=100,200,... ; snapshot_total additionne quantity*price des seules lignes cancelled=False. Les enregistrements issued sont des références déjà émises : préserver strictement state, sequence, snapshot_total et reference. Les autres sociétés restent strictement inchangées. Une sélection mixte est admise, les enregistrements hors périmètre sont ignorés. La reprise autorisée porte sur les brouillons existants de la société initiale de la copie ; le résultat doit être idempotent. Les droits existants restent inchangés. Q1 valeurs finales : 100/200, pas 10/20. Q2 références émises : aucune renumérotation ni recalcul. Le qa.md existant porte une ancienne recette sans données émises ni multi-société ; il ne réceptionne pas ce correctif.
