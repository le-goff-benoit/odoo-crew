# Réception documentaire A — 2026-09-09

Relecteur : codex-o01-review-a, contexte indépendant du préparateur codex-author-a. Premier reçu réel ; aucun verdict antérieur utilisé.
Projet documentaire ; périmètre `documentary/A`. Série Odoo non applicable au contrôle de cette fixture. Aucun test Odoo ou navigateur rejoué.

**Verdict : PASS documentaire.**

| Axe | Verdict | Constat |
|---|---|---|
| Demande ↔ contrat | pass | Même référence dossier et fiche interne ; interdiction originale de tri conservée. La consigne mémoire, non répétée dans le contrat court, reste vérifiée dans les deux drafts. |
| Contrat → preuves | pass | Égalité exacte du fichier synthétique, preuve exécutée avec code zéro et log cohérent ; empreintes vérifiées. |
| Sources → mémoire | pass | Bases conservées intégralement ; décision, interdiction, succès effectif et limites transmis dans PROJECT et JOURNAL. |

Les citations exactes et explications détaillées des trois axes sont conservées dans `review-A.json`.

La demande dit « Ne pas ajouter de tri automatique. » ; le contrat dit « Aucune demande de tri automatique. ». Cette dernière formule ne supprime pas l'interdiction originale, reprise textuellement dans PROJECT et explicitement dans JOURNAL.

La QA précise : « Aucune validation Odoo ou navigateur n'a été effectuée. » Le succès reçu porte seulement sur `documentary/A/reference.txt` contenant `reference_dossier=visible` suivi d'un saut de ligne. Il ne permet aucune conclusion sur une application réelle hors de ce périmètre. PROJECT conserve « Le contrôle documentaire A a réussi » et JOURNAL « Verdict : contrôle documentaire A réussi » : le résultat est transmis sans être réduit à une trace de conservation.

Les bases « Le tableau conserve les décisions explicites. » et « Initialisation du dossier. » restent intégralement présentes. Aucun historique supplémentaire n'est disponible dans ces bases.

Intégrité vérifiée en lecture : groupes du bundle, bases, drafts, cibles actuelles, fichier du périmètre et log de la preuve. Aucun état ni mémoire n'a été modifié ou publié ; le coordinateur reste responsable du pass de porte et de la publication.
