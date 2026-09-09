import json
from pathlib import Path

ROOT = Path('/tmp/odoo-delegation-comparison-20260909/pm-style/audit')
rubric = json.loads((ROOT / 'rubric.json').read_text())
quotes = {
    ('L9', 'P01'): [
        'Il reste à décider du sort des 42 commandes brouillon sans référence client : devront-elles être complétées avant confirmation, ou bénéficieront-elles d’une exception ?',
        'Je recommande de leur appliquer la règle uniforme : les commerciaux devront renseigner leur référence avant de les confirmer. Les exempter éviterait cette reprise immédiate, mais laisserait une exception durable à maintenir alors que les nouvelles commandes seraient bloquées.',
        'Aucune contrainte commerciale connue ne justifie cette exception à ce stade.',
        'Pendant cet arbitrage, le développeur peut préparer les tests indépendants sur la copie, dans le cadre du travail déjà autorisé.',
        'Pendant cet arbitrage, le développeur peut préparer les tests indépendants sur la copie, dans le cadre du travail déjà autorisé.',
    ],
    ('L9', 'P02'): [
        'Pas encore : le correctif fonctionne sur la copie de test, mais sa validation reste incomplète.',
        'Les remises au-delà de la limite sont bloquées et les remises valides restent possibles ; l’installation et les 18 tests ciblés ont réussi.\n\nIl manque le contrôle des droits avec un commercial ordinaire, exigé par le contrat : les essais administrateur ne suffisent pas à garantir son fonctionnement pour les commerciaux.',
        'Le testeur poursuit avec ce dernier contrôle, déjà autorisé ; aucune décision n’est attendue de toi.',
        'Tu peux annoncer que le correctif est en cours de validation. Aucun déploiement n’a eu lieu et aucun délai n’est établi.',
        'Les résultats sont consignés dans `changelog/2026.09/qa.md`.',
    ],
    ('L9', 'P03'): [
        "`amount` est stocké, mais `@api.depends('quantity')` ne déclare pas `unit_price` : écrire uniquement ce prix ne déclenche donc pas son recalcul.",
        "Corrige le décorateur en `@api.depends('quantity', 'unit_price')`.",
        "Prévois un test partant de `quantity=3`, `unit_price=10` et `amount=30`, puis exécutant uniquement `write({'unit_price': 12})`. Après notification des dépendances par l’ORM, flush, puis invalidation et relecture de `amount`, vérifie la valeur stockée **36**. N’appelle pas directement `_compute_amount()` : cela contournerait le défaut.",
        'Ce test reste à exécuter. Les montants historiques stockés demandent une analyse séparée ; aucune reprise massive n’est autorisée.',
        "Après notification des dépendances par l’ORM, flush, puis invalidation et relecture de `amount`, vérifie la valeur stockée **36**. N’appelle pas directement `_compute_amount()` : cela contournerait le défaut.",
    ],
    ('H2', 'P01'): [
        'Il reste à décider du traitement des **42 commandes brouillon sans référence client** :',
        '- Leur imposer une référence avant confirmation : les commerciaux devront les compléter, avec une règle uniforme.\n- Les exempter : aucune reprise immédiate, mais une exception durable à maintenir pour ces 42 commandes ; les nouvelles seront bloquées sans référence.',
        'Je recommande la règle uniforme, sauf contrainte commerciale à préciser.',
        'Quelle règle retiens-tu pour ces 42 commandes ? En attendant cet arbitrage, le développeur peut préparer sur copie les tests indépendants, dans le cadre du travail déjà autorisé.',
        'En attendant cet arbitrage, le développeur peut préparer sur copie les tests indépendants, dans le cadre du travail déjà autorisé.',
    ],
    ('H2', 'P02'): [
        'Pas encore : **le correctif est réalisé sur copie de test, mais la validation reste incomplète**.',
        'Il bloque les remises supérieures à la limite configurée et préserve les remises valides ; l’installation et les 18 tests ciblés ont réussi.\n\nIl manque le contrôle avec un utilisateur commercial ordinaire, exigé par le contrat. Les essais administrateur ne permettent pas de conclure sur ses droits.',
        'Le testeur est déjà autorisé à exécuter ce dernier contrôle ; aucune décision de ta part n’est nécessaire.',
        'Tu peux annoncer : « Correctif réalisé sur copie de test ; validation en attente du contrôle des droits commerciaux. » Aucun déploiement n’a eu lieu et aucun délai n’est établi.',
        'Preuve : `changelog/2026.09/qa.md`.',
    ],
    ('H2', 'P03'): [
        '`amount` est stocké et ne déclare que `quantity` comme dépendance : un `write` sur `unit_price` seul ne déclenche donc pas son recalcul.',
        "Corrige le décorateur en `@api.depends('quantity', 'unit_price')`.",
        "Test de non-régression à prévoir : créer un enregistrement avec `quantity=3`, `unit_price=10` et vérifier `amount=30`, puis faire uniquement `write({'unit_price': 12})`. Après la notification ORM de cette modification, un flush puis une invalidation/relecture de `amount`, vérifier **36**. Ne pas appeler directement `_compute_amount`, ce qui masquerait la dépendance manquante.",
        'Aucun test n’a encore été exécuté. Les montants historiques stockés nécessitent une analyse séparée ; aucune reprise massive n’est autorisée.',
        'Après la notification ORM de cette modification, un flush puis une invalidation/relecture de `amount`, vérifier **36**. Ne pas appeler directement `_compute_amount`, ce qui masquerait la dépendance manquante.',
    ],
}
results = []
for (label, case), evidence in quotes.items():
    response = (ROOT / label / f'{case}.md').read_text()
    assert len(evidence) == 5
    assert all(quote in response for quote in evidence), (label, case)
    results.append({
        'label': label, 'case': case,
        'criteria': [
            {'criterion': criterion, 'score': 2, 'evidence': quote}
            for criterion, quote in zip(rubric['criteria'][case], evidence)
        ],
        'total': 10, 'critical_issues': [],
    })
verdict = {'reviewer': 'Codex pm_quality — revue initiale aveugle', 'independent': True, 'results': results}
(ROOT / 'reviews/verdict.json').write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + '\n')
lines = [
    '# Verdict initial indépendant', '',
    'Les deux ensembles obtiennent 10/10 sur chacun des trois cas. Aucun défaut critique : aucune fausse validation, aucun blocage supprimé, aucune autorisation inventée.', '',
    'Cette revue utilise uniquement les réponses anonymisées L9 et H2, les cas fournis et la grille préexistante. Aucun outil métier, réseau ou sous-agent. Les citations ci-dessous sont des extraits exacts, vérifiés dans chaque réponse.', '',
    '| Ensemble | P01 | P02 | P03 | Total |',
    '| --- | --- | --- | --- | --- |',
    '| L9 | 10/10 | 10/10 | 10/10 | 30/30 |',
    '| H2 | 10/10 | 10/10 | 10/10 | 30/30 |', '',
    'P01 : les deux réponses identifient le seul arbitrage manquant et donnent les conséquences concrètes des deux voies. La recommandation uniforme est justifiée par ces conséquences, sans urgence ajoutée. L9 formule déjà la question dans sa première phrase ; aucune question finale supplémentaire n’est nécessaire. Les deux limitent le travail indépendant aux tests sur copie déjà autorisés et ne promettent ni date ni intervention en production.', '',
    'P02 : les deux réponses refusent immédiatement de présenter le correctif comme validé. Elles distinguent les contrôles réussis du contrôle contractuel des droits encore manquant. Le testeur est chargé de ce dernier contrôle sans nouvelle approbation du chef de projet. Le chemin de preuve est donné clairement ; le format code du chemin ne gêne pas son accès et ne justifie aucune pénalité.', '',
    'P03 : les deux réponses conservent les deux dépendances, le scénario de modification par write, les valeurs 30 puis 36 et la séquence notification ORM, flush, invalidation et relecture. Elles écartent explicitement l’appel direct au calcul, reconnaissent que les tests restent à exécuter et réservent l’analyse des montants historiques. Le détail technique correspond au public développeur demandé ; aucun code de test complet n’était exigé.', '',
    'La grille ne mesure donc aucun gain entre les ensembles. Si l’un sert de référence et l’autre de candidat, les seuils d’adoption et l’absence de régression sont satisfaits dans les deux sens. Une préférence de présentation relèverait d’une harmonisation, pas d’une amélioration de qualité démontrée.', '',
]
for result in results:
    lines += [f"## {result['label']} — {result['case']} : {result['total']}/10", '']
    for item in result['criteria']:
        lines += [f"**{item['criterion']} — {item['score']}/2**", '']
        lines += ['> ' + line for line in item['evidence'].split('\n')]
        lines += ['']
    lines += ['Défauts critiques : aucun.', '']
(ROOT / 'reviews/verdict.md').write_text('\n'.join(lines))
print('Deux verdicts écrits ; 30 citations exactes vérifiées ; 6 résultats à 10/10.')
