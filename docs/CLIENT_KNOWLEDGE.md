# Décisions, contexte et scénarios métier

`PROJECT.md` décrit le métier courant, `JOURNAL.md` garde l'historique bref et les
releases portent le détail. `DECISIONS.json` est facultatif pour les projets
simples ; il rend explicites les propositions, décisions confirmées, remplacements,
questions ouvertes et états de réalisation. Son schéma est dans
`docs/quality-lab/TOOLING-CHANGES.md`. Aucune conversion automatique d'une phrase
historique en décision actuelle : l'agent doit citer la source de l'arbitrage.

Pour préparer un contexte ciblé et vérifier une passation :

```bash
python3 scripts/odoo_context.py PROJET --query 'locations frais' \
  --budget 12000 --output PROJET/changelog/RELEASE/contexte-T01.json
python3 scripts/odoo_context.py PROJET --verify PROJET/changelog/RELEASE/contexte-T01.json
```

Le budget porte sur le texte entier, index des omissions compris ; un socle
obligatoire trop long produit explicitement `budget_status: insufficient`.
Un bloc trop long est omis entier avec un lien : ses exceptions ne sont jamais
coupées. La recherche lexicale ne garantit pas le rappel complet ; l'agent lit les
sources signalées dès qu'une règle ou un ancien arbitrage devient pertinent.
La vérification compare les empreintes, pas le sens métier. Une modification de
source déclenche une nouvelle lecture, pas le simple renouvellement d'un hash.

Pour la mémoire partagée pendant toute la release, les pièces complémentaires
et l'index des sources Odoo/custom : [KNOWLEDGE.md](KNOWLEDGE.md).

Un catalogue facultatif `.odoo-agents/SCENARIOS.json` relie les règles aux tests :

```json
{"schema":1,"scenarios":[{"id":"S01","rule":"Le document validé reste figé",
 "source":{"path":"decisions/D12.md","sha256":"EMPREINTE_REELLE"},
 "actor":"Gestionnaire, société A","setup":"Copie neutralisée avec un dossier validé",
 "expected":"Le total validé ne change pas","forbidden":"Modifier le document historique",
 "triggers":["module_custom/*","dependance_custom/*"],"scopes":["module_custom","dependance_custom"],
 "group":"server","module":"module_custom",
 "command":["/chemin/odoo-test.sh","module_custom","--quick","--tags","/module_custom:TestFrozenDocument"]}]}
```

```bash
python3 scripts/odoo_scenarios.py select PROJET --changed module_custom/models/record.py
python3 scripts/odoo_scenarios.py run PROJET --ids S01 --output PROJET/changelog/RELEASE/preuves/campagne-1
```

Une dépendance inconnue élargit la sélection ; une source métier modifiée bloque
jusqu'à relecture du scénario. Les attendus viennent du contrat client, pas de
la méthode testée. La source de décision entre dans la preuve : un nouveau contrat
invalide une preuve antérieure même si le code n'a pas encore changé.

Les groupes `server`, `browser`, `data` sont des classifications déclarées. Ils
ne réécrivent pas les tags d'Odoo : vérifier que chaque commande correspond
réellement au groupe annoncé. Ne pas prétendre avoir exclu les tours sur le seul
nom du groupe. Une incertitude sur la couverture impose d'élargir les tests.

La QA peut réutiliser une preuve valide après relecture. Outre l'empreinte du
code, elle doit vérifier l'image, les dépendances, les données et les paramètres
réels : un même fichier de test sur une autre base ne constitue pas la même preuve.
L'état d'une base ne devient pas immuable parce qu'un log existe.
