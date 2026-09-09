```
[0/4 briefing]  lab_rental · 19.0 (manifest) · aucune release ouverte · copie lab_client
[1/4 analyst]   À DÉVELOPPER — sale_renting est Enterprise et hors sujet, 0 question bloquante → QA renforcée
[2/4 developer] 4 fichiers, 10 tests · lint : 0 erreur · ~2 min de QA Docker
[3/4 tester]    VALIDÉ — install/update OK, 10/10 tests, reprise prouvée sur lab_client, critères 12/12
[4/4 journal]   entrée écrite · PROJECT.md : 1 décision, 2 pièges ajoutés
```

# Frais de préparation des locations (D-02)

**Projet** Atelier Boréal · **série** 19.0 · **release** `2026-09-09_01_frais-de-preparation-des-locations` (point n°1, **ouverte**) · **module** `lab_rental`

## À décider
- J'ai ajouté `'author': 'Camptocamp'` au manifest : il manquait, ce qui rendait le lint rouge (dette antérieure à la tâche). Est-ce le bon auteur pour ce projet ?
- J'ai monté la version du manifest à `19.0.1.1.0` **pendant** la tâche, contre l'usage « une fois par release à la clôture ». Le dossier `migrations/19.0.1.1.0/` doit porter la version cible pour que la reprise s'exécute. À la clôture, ne pas la remonter une seconde fois si c'est bien la version livrée.

## Cadrage
Aucun module de location en Community 19.0 ; `sale_renting` est Enterprise et tarifie des lignes de commande — hors de proportion pour un forfait de 12 EUR, et contraire à « sans facturer ». Q1 et Q2 étant tranchées dans `decisions/2026-09-08.md`, aucune question bloquante. Écartés du périmètre : `Monetary`/`currency_id`, contrainte de positivité sur `days`/`daily_rate`, paramétrage du seuil.

## Réalisation
- `lab_rental/models/business.py` — le forfait est isolé dans `_preparation_fee()`, avec les constantes `PREPARATION_FEE` (12.0) et `PREPARATION_FEE_MIN_DAYS` (4) ; la docstring porte D-02 et le fait que D-01 est remplacée.
- `lab_rental/tests/test_preparation_fee.py` — 10 tests métier, dont un qui interdit le retour de D-01 (forfait identique à 10 et à 1000 EUR/jour).
- `lab_rental/migrations/19.0.1.1.0/post-migrate.py` — reprise idempotente via `env.add_to_compute`.
- `lab_rental/__manifest__.py` — version et `author`.

Aucune vue, aucun droit, aucune dépendance, aucun champ.

## QA de tâche — niveau renforcé
| Contrôle | Résultat |
|---|---|
| lint des fichiers touchés | ✅ 0 erreur, 0 avertissement |
| installation base neuve + tests ciblés | ✅ `install=ok`, 10/10, ⏱ 15 s |
| mise à jour base existante + tests ciblés | ✅ `update=ok`, 10/10, ⏱ 4 s |
| mise à niveau de la copie `lab_client` | ✅ 3 lignes sur 7 recalculées, +12.0 exactement |
| idempotence de la reprise | ✅ aucun montant ne dérive |
| périmètre en base (vues, actions, droits, champs) | ✅ inchangé |
| **critères d'acceptation** | **12/12 couverts** — `qa_rapport_tache1.md` |

**Ce que la QA a trouvé et qui a changé le code** : après mise à niveau avec le nouveau calcul mais sans reprise, une location de 4 jours restait à 40.0 sur `lab_client`. Modifier le corps d'un compute ne réécrit pas un champ stocké — la fonctionnalité aurait été verte en test et fausse sur tout l'historique. D'où le script de migration.

## Non couvert à ce stade
Rendu visuel et comportement pour un utilisateur non-admin : le passage RPC ne les prouve pas. Sans objet ici puisque rien ne change côté écrans ni droits (vérifié en base), mais c'est la recette navigateur de `/odoo-close` qui l'attestera.

## Reste à faire
Rien de rouge. Leçon candidate au dispositif : « corriger le calcul d'un champ stocké ne corrige pas les valeurs en base » figure dans le rôle développeur mais pas dans `LESSONS.md` — à promouvoir via `/odoo-feedback`.

## Release
1 point, 1 réalisé. **Release laissée ouverte** comme demandé ; aucune capture, aucun guide, aucune communication produits. Clôture et recette complète : `/odoo-close`. Rien n'est commité.