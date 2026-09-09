# Fragment QA — scénarios RPC

## 1. Scénario sur la copie configurée par le pack
```
A1 — définition du champ
  OK   un seul champ, sans doublon — attendu 1, obtenu 1
  OK   type — attendu 'boolean', obtenu 'boolean'
  OK   champ manuel — attendu 'manual', obtenu 'manual'
  OK   stocké — attendu True, obtenu True
  OK   calculé (code non vide) — attendu True, obtenu True
  OK   dépendances — attendu 'x_studio_days,x_studio_kind', obtenu 'x_studio_days,x_studio_kind'
A2 — location de 7 jours : le seuil inclut 7
  OK   rental / 7 j — attendu True, obtenu True
A3 — location de 6 jours : sous le seuil
  OK   rental / 6 j — attendu False, obtenu False
A4 — prêts : exclus quelle que soit la durée
  OK   loan / 7 j — attendu False, obtenu False
  OK   loan / 30 j — attendu False, obtenu False
A5 — recalcul sur modification de la durée
  OK   avant : rental / 6 j — attendu False, obtenu False
  OK   après : rental / 7 j — attendu True, obtenu True
A6 — recalcul sur modification du type
  OK   avant : loan / 10 j — attendu False, obtenu False
  OK   après : rental / 10 j — attendu True, obtenu True
Bord — type non renseigné
  OK   type vide / 30 j — attendu False, obtenu False
A9 — les demandes de recette sont retirées
  OK   aucune demande de recette restante — attendu 0, obtenu 0
A9 — la copie retrouve ses droits d'origine
  OK   aucun droit d'accès sur le modèle — attendu 0, obtenu 0
  OK   aucune règle d'enregistrement sur le modèle — attendu 0, obtenu 0

VERDICT : VERT — tous les contrôles passent
code retour=0
```

## 2. Contre-épreuve : la règle D-21 (5 jours, tous types) doit rendre le scénario rouge
```
règle D-21 (5 jours, tous types) remise en place sur le champ 3742
A1 — définition du champ
  OK   un seul champ, sans doublon — attendu 1, obtenu 1
  OK   type — attendu 'boolean', obtenu 'boolean'
  OK   champ manuel — attendu 'manual', obtenu 'manual'
  OK   stocké — attendu True, obtenu True
  OK   calculé (code non vide) — attendu True, obtenu True
  OK   dépendances — attendu 'x_studio_days,x_studio_kind', obtenu 'x_studio_days,x_studio_kind'
A2 — location de 7 jours : le seuil inclut 7
  OK   rental / 7 j — attendu True, obtenu True
A3 — location de 6 jours : sous le seuil
  ÉCHEC rental / 6 j — attendu False, obtenu True
A4 — prêts : exclus quelle que soit la durée
  ÉCHEC loan / 7 j — attendu False, obtenu True
  ÉCHEC loan / 30 j — attendu False, obtenu True
A5 — recalcul sur modification de la durée
  ÉCHEC avant : rental / 6 j — attendu False, obtenu True
  OK   après : rental / 7 j — attendu True, obtenu True
A6 — recalcul sur modification du type
  ÉCHEC avant : loan / 10 j — attendu False, obtenu True
  OK   après : rental / 10 j — attendu True, obtenu True
Bord — type non renseigné
  ÉCHEC type vide / 30 j — attendu False, obtenu True
A9 — les demandes de recette sont retirées
  OK   aucune demande de recette restante — attendu 0, obtenu 0
A9 — la copie retrouve ses droits d'origine
  OK   aucun droit d'accès sur le modèle — attendu 0, obtenu 0
  OK   aucune règle d'enregistrement sur le modèle — attendu 0, obtenu 0

VERDICT : ROUGE — 6 contrôle(s) en échec : rental / 6 j, loan / 7 j, loan / 30 j, avant : rental / 6 j, avant : loan / 10 j, type vide / 30 j
code retour=1
```

## 3. Retour à D-22 par le script de construction
```
champ réaligné : x_lab_request.x_studio_needs_review → compute
identifiant externe : studio_customization.x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826 (noupdate=True)
```

## 4. Scénario de nouveau vert, et pack sans dérive
```
A1 — définition du champ
  OK   un seul champ, sans doublon — attendu 1, obtenu 1
  OK   type — attendu 'boolean', obtenu 'boolean'
  OK   champ manuel — attendu 'manual', obtenu 'manual'
  OK   stocké — attendu True, obtenu True
  OK   calculé (code non vide) — attendu True, obtenu True
  OK   dépendances — attendu 'x_studio_days,x_studio_kind', obtenu 'x_studio_days,x_studio_kind'
A2 — location de 7 jours : le seuil inclut 7
  OK   rental / 7 j — attendu True, obtenu True
A3 — location de 6 jours : sous le seuil
  OK   rental / 6 j — attendu False, obtenu False
A4 — prêts : exclus quelle que soit la durée
  OK   loan / 7 j — attendu False, obtenu False
  OK   loan / 30 j — attendu False, obtenu False
A5 — recalcul sur modification de la durée
  OK   avant : rental / 6 j — attendu False, obtenu False
  OK   après : rental / 7 j — attendu True, obtenu True
A6 — recalcul sur modification du type
  OK   avant : loan / 10 j — attendu False, obtenu False
  OK   après : rental / 10 j — attendu True, obtenu True
Bord — type non renseigné
  OK   type vide / 30 j — attendu False, obtenu False
A9 — les demandes de recette sont retirées
  OK   aucune demande de recette restante — attendu 0, obtenu 0
A9 — la copie retrouve ses droits d'origine
  OK   aucun droit d'accès sur le modèle — attendu 0, obtenu 0
  OK   aucune règle d'enregistrement sur le modèle — attendu 0, obtenu 0

VERDICT : VERT — tous les contrôles passent
code retour=0
Comparaison de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json avec http://127.0.0.1:46487 / lab_client (aucune écriture) :
0 / 0 / 1 à créer / à modifier / inchangés sur http://127.0.0.1:46487 / lab_client
```
