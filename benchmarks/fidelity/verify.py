#!/usr/bin/env python3
"""Verify corpus bytes and optional manually adjudicated citation records.

This verifier never turns keywords into a semantic success verdict.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(output_root=None, evaluation=None):
    manifest = json.loads((HERE / 'cases.json').read_text())
    oracle = json.loads((HERE / 'oracle.json').read_text())
    cases = {case['id']: case for case in manifest['cases']}
    checked = 0
    for case_id, case in cases.items():
        by_target = {item['target']: item for item in case['files']}
        assert len(by_target) == len(case['files']), case_id
        for item in case['files']:
            assert sha(ROOT / item['source']) == item['sha256'], item['source']
            if output_root:
                assert sha(Path(output_root) / case_id / 'project' / item['target']) == item['sha256'], item['target']
            checked += 1
        for check in oracle['cases'][case_id]['checks']:
            for anchor in check['anchors']:
                item = by_target[anchor['path']]
                source = ROOT / item['source']
                assert sha(source) == anchor['sha256'], anchor['path']
                text = source.read_text()
                assert anchor['quote'] in text, anchor['path']
                assert text[:text.index(anchor['quote'])].count('\n') + 1 == anchor['line']
    if evaluation:
        evaluation = Path(evaluation)
        verdict = json.loads(evaluation.read_text())
        case_id = verdict['case']
        response = (evaluation.parent / verdict['response_path']).read_text()
        expected = {check['id'] for check in oracle['cases'][case_id]['checks']}
        rows = verdict['decisions']
        assert len(rows) == len(expected)
        assert {row['check_id'] for row in rows} == expected
        by_target = {item['target']: item for item in cases[case_id]['files']}
        for row in rows:
            assert row['verdict'] in ('pass', 'fail', 'uncertain')
            assert row['reason'].strip()
            # An omission can have no response quote; it must be identified
            # explicitly, not supplied with a fabricated quotation.
            assert row['response_quotes'] or row.get('absence_observed') is True
            for quote in row['response_quotes']:
                assert quote and quote in response
            assert row['source_anchors']
            for anchor in row['source_anchors']:
                item = by_target[anchor['path']]
                text = (ROOT / item['source']).read_text()
                assert anchor['quote'] and anchor['quote'] in text
    return {'source_files_checked': checked, 'cases': len(cases), 'semantic_verdict': 'manual_review_required'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--evaluation', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.output_root, args.evaluation)))
