#!/usr/bin/env python3
"""Matérialiser les réponses B12 sans les corriger, puis exécuter l'oracle Odoo."""
import argparse
import ast
import json
from pathlib import Path

import odoo_bench as bench
from odoo_bench_judge import parse_json
from odoo_bench_runtime import campaign


def extract(answer):
    data = parse_json(answer)
    if not isinstance(data, dict) or set(data) != {'code'} or not isinstance(data['code'], str) or not data['code'].strip():
        raise ValueError('un objet JSON contenant seulement code est requis')
    ast.parse(data['code'])  # analyse syntaxique, aucune exécution sur l'hôte
    return data['code']


def execute(runs, output):
    candidates, identities, invalid = {}, {}, {}
    for number, run in enumerate(runs):
        state = bench.read_json(run / 'state.json')
        if state['status'] not in ('executed', 'executed_with_errors'):
            raise ValueError('générations encore actives : ' + str(run))
        for trial in state['trials']:
            if trial['case'] != 'B12' or trial['status'] != 'completed':
                continue
            folder = run / trial['id']
            answer = folder / 'answer.md'
            if bench.digest(answer.read_bytes()) != trial['answer_sha256']:
                raise ValueError('réponse altérée : ' + str(answer))
            label = f'run{number+1}-{trial["provider"]}-{trial["config"]["effort"]}'
            identities[label] = (run, trial)
            try:
                code = extract(answer.read_text())
                path = folder / 'candidate.py'
                path.write_text(code)
                candidates[label] = path
            except (ValueError, SyntaxError) as exc:
                invalid[label] = str(exc)
    result = campaign(output, candidates)
    by_name = {t['name']: t for t in result['trials']}
    for label, (run, trial) in identities.items():
        if label in invalid:
            grade, evidence = 'fail', 'Réponse non matérialisable sans correction : ' + invalid[label]
        else:
            observed = by_name[label]
            grade = 'pass' if observed['passed'] else 'fail'
            evidence = f"Oracle Odoo 19 réel, code inchangé : {output / observed['log']}, SHA256={observed['log_sha256']}, bilan={observed['proof']['summaries']}"
        bench.review_trial(run, trial['id'], {'reviewer': 'oracle Odoo 19 / contrat synthétique S-01',
                                            'answer_sha256': trial['answer_sha256'],
                                            'criteria': {'runtime': {'grade': grade, 'evidence': evidence}}})
    bench.atomic_json(output / 'mapping.json', {'trials': {k: {'run':str(r), 'trial':t['id']} for k,(r,t) in identities.items()}, 'invalid': invalid})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', nargs='+', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.runs, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
