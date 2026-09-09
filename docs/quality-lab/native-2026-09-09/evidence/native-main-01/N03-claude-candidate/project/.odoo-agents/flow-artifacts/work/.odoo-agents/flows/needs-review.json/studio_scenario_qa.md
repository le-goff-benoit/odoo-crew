# Fragment QA — scénarios rejoués (contrôle indépendant)

## Scénario XML-RPC — `test_1_needs_review.py`
```
OK   C12  un seul x_studio_needs_review sur x_lab_request — 1 trouvé(s)
OK   C10  type booléen — boolean
OK   C8   champ stocké — store=True
OK   C10  dépendances déclarées — 'x_studio_days,x_studio_kind'
OK   C10  champ manuel en lecture seule — state=manual readonly=True
OK   C10  code du calcul conforme à D-22 — "for record in self:\n    record['x_studio_needs_review'] = record['x_studio_kind'] == 'rental' and record['x_studio_days'] >= 7\n"
OK   C12  un seul identifiant externe pour le champ — 1 trouvé(s)
OK   C10  identifiant externe dans studio_customization, noupdate — studio_customization.revue_requise_demand_924627ca-0724-4389-b944-ba45837bd3c3 noupdate=True
OK   C10  nommé par Odoo (suffixe uuid), pas à la main — revue_requise_demand_924627ca-0724-4389-b944-ba45837bd3c3
OK   C11  champ existant x_name inchangé — studio_customization.lab_seed_x_name
OK   C11  champ existant x_studio_days inchangé — studio_customization.lab_seed_x_studio_days
OK   C11  champ existant x_studio_kind inchangé — studio_customization.lab_seed_x_studio_kind

INFO  table de vérité D-22 non jouable en RPC : <Fault 4: "You are not allowed to access 'Demande Aster' (x_lab_request) records.\n\nNo group currently allows this operation.\n\nContact your administrator to request access if necessary.">
INFO  → jouée en ORM superutilisateur par test_1_needs_review_orm.py

RECETTE VERTE — 12 contrôle(s), 0 échec(s)
rc=0
```

## Scénario ORM — `test_1_needs_review_orm.py`
```
OK   C8   colonne x_studio_needs_review présente en base
OK   C9   reprise des 3 enregistrement(s) antérieur(s) — reprise location 9 jours=True, reprise location 2 jours=False, reprise prêt 20 jours=False
OK   C1   location 7 jours — seuil inclus → True — lu True
OK   C2   location 6 jours — sous le seuil → False — lu False
OK   C3   location 30 jours → True — lu True
OK   C4   prêt 7 jours — exclu → False — lu False
OK   C4   prêt 30 jours — exclu → False — lu False
OK   C5   sans type → False — lu False
OK   C5   location 0 jour → False — lu False
OK   C5   location -3 jours → False — lu False
OK   C6   prêt 10 j avant bascule → faux
OK   C6   prêt 10 j passé en location → vrai
OK   C7   location 10 j avant bascule → vrai
OK   C7   location 10 j ramenée à 3 j → faux
OK   C8   recherche serveur sur l'indicateur — 3 enregistrement(s) à vrai
OK   —    nettoyage des données de recette — 0 restant(s)
RECETTE VERTE — 16 contrôle(s), 0 échec(s)
```

## Écran

Aucune vue n'est modifiée par ce point, et `x_lab_request` n'a aucune
`ir.ui.view` : **aucune capture n'est requise** (règle du rôle : capture
seulement si une vue change).

## Rouge avant / vert après

Les deux scénarios ont été joués **avant** la configuration : rouges
(`qa/1_rpc_avant.log`, `qa/1_orm_avant.log`). Verts après, y compris après
reconstruction de l'état par le seul `pack.json`
(`qa/1_pack_double_application.log`).
