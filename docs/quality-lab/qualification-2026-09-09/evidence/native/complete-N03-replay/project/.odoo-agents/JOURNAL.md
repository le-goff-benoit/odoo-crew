# Journal

## 2026-08-01 — Ancienne conception
**Appris** : D-21 historique (remplacée) : revue à 5 jours pour tout le monde. Le brouillon de conception initial demandait un nouveau champ durée : ne pas l'appliquer, x_studio_days existe déjà.

## 2026-09-08 — Arbitrage
**Fait** : décision actuelle consignée dans decisions/2026-09-08.md.
**Appris** : la décision récente remplace les anciennes règles incompatibles.
**Reste ouvert** : réalisation et validation locale de la demande.

## 2026-09-09 — Indicateur de revue x_studio_needs_review (voie Studio)
**Demande** : indicateur booléen stocké sur `x_lab_request`, calculé selon D-22, sans écran ni module.
**Fait** : release `2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast` ouverte, point 1 `[studio]`. Champ `x_studio_needs_review` créé en
contexte `studio=True` sur le modèle existant (booléen, stocké, readonly, `depends=x_studio_days,x_studio_kind`).
Pack versionné + scénario RPC rejouable dans `changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/`.
**Verdict** : VALIDÉ — diff pack 0 écart, scénario 9/9 (rouge avant / vert après), deux
applications → 1 champ et 1 XML-ID, critères 10/10. Rien de déployé.
**Appris** :
- D-22 appliquée telle quelle : seuil 7 **inclus**, `loan` exclu ; D-21 (5 jours) reste écartée.
- Genre vide et durée nulle ou négative ⇒ pas de revue (hypothèse actée dans la revue, D-22 muette).
- Le banc renvoie une **liste** pour `create` en XML-RPC ; et un helper qui empaquette un
  niveau de liste en trop fait échouer `read`/`unlink` par `unhashable type: 'list'`.
- Aucun lint Ruff possible sur un point Studio (pas de module) : seul `py_compile` a été passé.
**Reste ouvert** : le champ n'est visible nulle part (aucune vue sur ce modèle) — l'exposer
est une tâche à cadrer. Release **ouverte** : recette complète et livrables à `/odoo-close`.
