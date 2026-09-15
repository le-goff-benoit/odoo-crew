#!/usr/bin/env python3
"""Calibration N06/N07 via le Lab natif existant ; aucun appel LLM."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from odoo_bench_native import Lab


def variants(identifier):
    reference = (ROOT / 'benchmarks/native/oracles' / (identifier + '_reference.py')).read_text()
    mutations = {
        'N06': {
            'issued_rewritten': ("row.state == 'draft' and row.company_id == self.env.company", 'row.company_id == self.env.company'),
            'other_company_rewritten': ("row.state == 'draft' and row.company_id == self.env.company", "row.state == 'draft'"),
            'wrong_final_positions': ('index * 100', 'index * 10'),
        },
        'N07': {
            'zero_loses_manual_marker': ("'manual': True", "'manual': bool(quantity)"),
            'copy_inherits_state': ('copy=False', 'copy=True'),
            'remaining_ignored': ('max(record.ordered_qty - record.delivered_qty, 0)', 'record.ordered_qty'),
        },
    }[identifier]
    result = [('reference', reference, True)]
    for name, (before, after) in mutations.items():
        if before not in reference:
            raise ValueError('Mutation cible absente : ' + name)
        result.append((name, reference.replace(before, after), False))
    return result


REQUIRED_CHECKS = {
    'N06': {'legacy_drafts_repaired', 'emitted_reference_frozen', 'other_company_untouched', 'ordinary_user_mixed_selection', 'scope_remains_local', 'idempotent', 'company_rule_still_enforced'},
    'N07': {'legacy_auto_repaired', 'legacy_explicit_zero_preserved', 'legacy_partial_preserved', 'legacy_done_preserved', 'explicit_zero_not_false', 'copy_resets_operational_state', 'copy_then_cron', 'remainder_contract', 'remainder_then_cron', 'no_empty_remainder', 'negative_remaining_clamped', 'idempotent_cron'},
}
MUTATION_CHECKS = {
    'issued_rewritten': 'emitted_reference_frozen',
    'other_company_rewritten': 'other_company_untouched',
    'wrong_final_positions': 'legacy_drafts_repaired',
    'zero_loses_manual_marker': 'explicit_zero_not_false',
    'copy_inherits_state': 'copy_resets_operational_state',
    'remaining_ignored': 'legacy_auto_repaired',
}


def calibrated(identifier, label, verdict):
    checks = verdict.get('checks')
    if verdict.get('exit_code') != 0 or not isinstance(checks, dict) or set(checks) != REQUIRED_CHECKS[identifier] or not all(type(v) is bool for v in checks.values()):
        return False
    if label == 'reference':
        return verdict.get('passed') is True and all(checks.values())
    return verdict.get('passed') is False and checks[MUTATION_CHECKS[label]] is False


def run(output, identifiers):
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for identifier in identifiers:
        case = json.loads((ROOT / 'benchmarks/native/cases' / identifier / 'case.json').read_text())
        for label, code, expected in variants(identifier):
            folder = output / (identifier + '-' + label)
            folder.mkdir()
            shutil.copy2(__file__, folder / 'calibration-runner.py')
            for suffix in ('_seed.py', '_check.py', '_reference.py'):
                shutil.copy2(ROOT / 'benchmarks/native/oracles' / (identifier + suffix), folder / (identifier + suffix))
            (folder / 'case.json').write_text(json.dumps(case, indent=2, ensure_ascii=False) + '\n')
            project = folder / 'project'
            shutil.copytree(ROOT / 'benchmarks/native/cases' / identifier / 'project', project)
            lab = Lab(folder, ROOT, project, case)
            start = time.monotonic()
            try:
                lab.start()
                (project / case['module'] / 'models/business.py').write_text(code)
                updated = lab.handle(['update'])
                if updated['exit_code']:
                    raise RuntimeError('update failed')
                repair = project / 'repair.py'
                repair.write_text("env['lab.register'].search([]).action_repair()\nenv.cr.commit()\n" if identifier == 'N06' else "env['lab.preparation']._cron_prepare()\nenv.cr.commit()\n")
                repaired = lab.handle(['shell', str(repair)])
                if repaired['exit_code']:
                    raise RuntimeError('repair failed')
                verdict = lab.oracle()
                row = {'case': identifier, 'variant': label, 'expected_pass': expected, 'oracle': verdict,
                       'expectation_met': calibrated(identifier, label, verdict),
                       'seconds': round(time.monotonic() - start, 3)}
                results.append(row)
                (folder / 'result.json').write_text(json.dumps(row, indent=2) + '\n')
                print(json.dumps(row), flush=True)
                if label == 'reference' and not verdict['passed']:
                    raise RuntimeError('Witness failed; mutations not interpretable')
            finally:
                lab.close()
                (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    (output / 'SHA256.json').write_text(json.dumps({str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'SHA256.json'}, indent=2) + '\n')
    return all(row['expectation_met'] for row in results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', choices=['N06', 'N07'], default=['N06', 'N07'])
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output.resolve(), args.cases) else 1)
