# Réception indépendante B — PASS

Projet : O01/project ; aucun module ni série Odoo applicable. Mode : réception documentaire sur bundle B, sans test Odoo.

| Axe | Verdict | Constat |
|---|---|---|
| Demande → contrat | pass | Priorité manuelle, absence de tri et consignation mémoire respectées dans la portée documentaire. |
| Contrat → preuve | pass | Assertion exacte sur le seul fichier B, sortie 0 et résultat passed ; log et empreintes concordants. |
| Sources → mémoire | pass | Bases conservées ; décisions A/B sourcées ; succès B et limites repris dans les deux drafts. |

La demande B (demande-B.md:1) exige « Conserver la priorité manuelle du tableau de suivi. Ne pas ajouter de tri automatique. » Le contrat (spec-B.md:2) précise « Le contrôle porte uniquement sur documentary/B/priority.txt. » La consignation, peu détaillée dans ce contrat abrégé, est bien présente dans les deux propositions.

La preuve evidence-B.json:16 contrôle l'égalité intégrale avec `priority=manual` et un saut de ligne ; evidence-B.json:18–19 porte un code de sortie nul et le résultat `passed`. Le log référencé est cohérent. Dix empreintes ont été vérifiées : sources, contrat, preuve, bases, drafts, fichier contrôlé et log. Aucune nouvelle exécution n'a été demandée.

PROJECT-propose.md:9 dit « Le contrôle documentaire B a réussi : documentary/B/priority.txt contient exactement `priority=manual`. » JOURNAL-propose.md:10 reprend le même succès. Leurs lignes 10 et 12 respectives précisent « aucun contrôle Odoo ». Ce résultat demeure limité à l'artefact synthétique ; il n'atteste aucun comportement applicatif.

Les bases PROJECT et JOURNAL (lignes 1–2 de chacune) restent intégralement présentes. Elles n'ont aucun résultat A. Les ajouts A, PROJECT-propose.md:5 et JOURNAL-propose.md:5, reproduisent la décision de demande-A.md:1 : référence visible dans la fiche interne et interdiction de tri. Ils n'affirment aucun contrôle, implémentation ou livraison A. L'absence de preuve A n'est donc pas transformée en succès A ; le contrôle B conserve son périmètre.

Les citations exactes et explications complètes sont dans review-B.json. Ce reçu juge les bases figées ; il ne certifie pas la fraîcheur d'une cible mémoire concurrente lors de la publication. Aucun état, aucune mémoire canonique ni ancien artefact modifié.
