#!/usr/bin/env python3
"""Preuve de tests Odoo : résultat explicite, positif, sans échec, du module visé."""
import argparse
import json
from pathlib import Path
import re


def inspect_log(text, module=None):
    results = re.findall(r'odoo\.tests\.result:.*?(\d+) failed, (\d+) error\(s\) of (\d+) tests', text)
    reasons = []
    if not results:
        reasons.append('aucun bilan de tests reconnu')
    elif any(int(f) or int(e) for f, e, _ in results):
        reasons.append('bilan contenant des échecs ou erreurs')
    if results and not any(int(n) > 0 for _, _, n in results):
        reasons.append('zéro test exécuté')
    module_tests = None
    if module:
        counts = re.findall(r'odoo\.tests\.stats:\s*' + re.escape(module) + r':\s*(\d+) tests?\b', text)
        module_tests = sum(map(int, counts))
        if not module_tests:
            reasons.append('aucun test du module cible prouvé')
    if re.search(r'\b(?:ERROR|CRITICAL)\b.*(?:odoo\.|test)|invalid module names, ignored|\bFAIL:', text):
        reasons.append('erreur ou module ignoré dans le log')
    return {'valid': not reasons, 'reasons': reasons, 'module_tests': module_tests,
            'summaries': [{'failed': int(f), 'errors': int(e), 'tests': int(n)} for f, e, n in results]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--module')
    args = parser.parse_args()
    result = inspect_log(args.log.read_text(errors='replace'), args.module)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['valid'] else 1)
