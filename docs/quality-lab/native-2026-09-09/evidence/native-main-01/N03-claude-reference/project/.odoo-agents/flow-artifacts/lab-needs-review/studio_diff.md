# Fragment QA — cohérence du pack et double application

## 1. Diff initial (pack ↔ copie, aucune écriture)
```
Comparaison de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json avec http://127.0.0.1:46487 / lab_client (aucune écriture) :
0 / 0 / 1 à créer / à modifier / inchangés sur http://127.0.0.1:46487 / lab_client
```

## 2. État de la copie avant application
```
champs du modèle : ['create_date', 'create_uid', 'display_name', 'id', 'write_date', 'write_uid', 'x_name', 'x_studio_days', 'x_studio_kind', 'x_studio_needs_review']
occurrences de x_studio_needs_review : 1
identifiants externes studio_customization : 5
    lab_seed_model | noupdate= True | studio= True
    lab_seed_x_name | noupdate= True | studio= True
    lab_seed_x_studio_days | noupdate= True | studio= True
    lab_seed_x_studio_kind | noupdate= True | studio= True
    x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826 | noupdate= True | studio= True
modèles x_lab_request en ir.model : 1
```

## 3. Première application
```
Application de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json sur http://127.0.0.1:46487 / lab_client :
0 / 0 / 1 créés / modifiés / inchangés sur http://127.0.0.1:46487 / lab_client
```

## 4. Seconde application
```
Application de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json sur http://127.0.0.1:46487 / lab_client :
0 / 0 / 1 créés / modifiés / inchangés sur http://127.0.0.1:46487 / lab_client
```

## 5. État après deux applications
```
champs du modèle : ['create_date', 'create_uid', 'display_name', 'id', 'write_date', 'write_uid', 'x_name', 'x_studio_days', 'x_studio_kind', 'x_studio_needs_review']
occurrences de x_studio_needs_review : 1
identifiants externes studio_customization : 5
    lab_seed_model | noupdate= True | studio= True
    lab_seed_x_name | noupdate= True | studio= True
    lab_seed_x_studio_days | noupdate= True | studio= True
    lab_seed_x_studio_kind | noupdate= True | studio= True
    x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826 | noupdate= True | studio= True
modèles x_lab_request en ir.model : 1
```

## 6. Diff final
```
Comparaison de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json avec http://127.0.0.1:46487 / lab_client (aucune écriture) :
0 / 0 / 1 à créer / à modifier / inchangés sur http://127.0.0.1:46487 / lab_client
```

---

# Fragment QA — double application depuis une copie sans le champ

## 1. Retrait du champ (retour à l'état d'avant la tâche)
```
champ retiré : [3740] | identifiant externe retiré : [26986]
reste : 0
```

## 2. Diff : le pack voit bien un enregistrement à créer
```
Comparaison de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json avec http://127.0.0.1:46487 / lab_client (aucune écriture) :
  + ir.model.fields studio_customization.x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826
1 / 0 / 0 à créer / à modifier / inchangés sur http://127.0.0.1:46487 / lab_client
```

## 3. Première application
```
Application de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json sur http://127.0.0.1:46487 / lab_client :
  + ir.model.fields studio_customization.x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826
1 / 0 / 0 créés / modifiés / inchangés sur http://127.0.0.1:46487 / lab_client
```

## 4. Seconde application
```
Application de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json sur http://127.0.0.1:46487 / lab_client :
0 / 0 / 1 créés / modifiés / inchangés sur http://127.0.0.1:46487 / lab_client
```

## 5. État final : un seul champ, un seul identifiant externe
```
champs du modèle : ['create_date', 'create_uid', 'display_name', 'id', 'write_date', 'write_uid', 'x_name', 'x_studio_days', 'x_studio_kind', 'x_studio_needs_review']
occurrences de x_studio_needs_review : 1
identifiants externes studio_customization : 5
    lab_seed_model | noupdate= True | studio= True
    lab_seed_x_name | noupdate= True | studio= True
    lab_seed_x_studio_days | noupdate= True | studio= True
    lab_seed_x_studio_kind | noupdate= True | studio= True
    x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826 | noupdate= True | studio= True
modèles x_lab_request en ir.model : 1
```

## 6. Diff final
```
Comparaison de /work/changelog/2026-09-09_01_indicateur-de-revue-sur-les-demandes-ast/studio/pack.json avec http://127.0.0.1:46487 / lab_client (aucune écriture) :
0 / 0 / 1 à créer / à modifier / inchangés sur http://127.0.0.1:46487 / lab_client
```

## 7. Le script de construction reconnaît le champ posé par le pack
```
champ déjà conforme : x_lab_request.x_studio_needs_review (id 3742) — rien à faire
identifiant externe : studio_customization.x_studio_needs_revie_05e329b9-1499-4502-af5f-f553d3fb9826 (noupdate=True)
```
