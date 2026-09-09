#!/usr/bin/env python3
"""Common post-freeze receiver; mechanical results never replace semantic review."""
import argparse
import json
from pathlib import Path
from materialize import CASES, hashes

REQUIRED = {
    'E01': ['analyse.md', 'PROJECT.md', 'JOURNAL.md', 'result.md'],
    'E02': ['diagnostic.md', 'PROJECT.md', 'JOURNAL.md', 'result.md'],
    'E03': ['analyse.md', 'qa.md', 'PROJECT.md', 'JOURNAL.md', 'result.md'],
}


def judge(case, run, review=None, runtime=None):
    run = Path(run)
    public = CASES / case / 'public'
    checks = []
    def check(key, passed, detail):
        checks.append({'id': key, 'pass': bool(passed), 'detail': detail})
    for name in REQUIRED[case]:
        path = run / 'output' / name
        check('artifact:' + name, path.is_file() and bool(path.read_text().strip()), str(path))
    for name, digest in hashes(public).items():
        if name.startswith('project/'):
            continue
        target = run / name
        current = hashes(run).get(name) if target.is_file() else None
        check('preserve_input:' + name, current == digest, 'Public evidence preserved')
    baseline = hashes(public / 'project')
    actual = hashes(run / 'project')
    for name, digest in baseline.items():
        if case == 'E03' and name.startswith('lab_qualification/'):
            continue
        check('preserve:' + name, actual.get(name) == digest, 'Original input remains byte-identical')
    forbidden = [name for name in actual if name not in baseline
                 and not (case == 'E03' and name.startswith('lab_qualification/'))]
    check('no_unowned_project_files', not forbidden, forbidden)
    for name in ('PROJECT.md', 'JOURNAL.md'):
        path = run / 'output' / name
        before = (public / 'project' / '.odoo-agents' / name).read_text()
        after = path.read_text() if path.exists() else ''
        if name == 'JOURNAL.md':
            check('journal_history', after.startswith(before), 'Existing journal text preserved exactly')
            added = after[len(before):] if after.startswith(before) else after
            check('journal_15_lines', 0 < len(added.strip().splitlines()) <= 15, len(added.strip().splitlines()))
    rubric = json.loads((CASES / case / 'private/rubric.json').read_text())
    expected = {item['id'] for item in rubric['obligations']}
    review = review or {}
    semantic_checks = review.get('checks', [])
    covered = {item.get('id') for item in semantic_checks}
    check('independent_semantic_review', review.get('case') == case and review.get('independent') is True
          and bool(review.get('reviewer')), 'Independent reviewer identity and case mandatory')
    check('semantic_coverage', covered == expected and len(semantic_checks) == len(expected), sorted(expected - covered))
    for item in semantic_checks:
        check('semantic:' + str(item.get('id')), item.get('pass') is True and bool(str(item.get('evidence', '')).strip()), item.get('evidence'))
    if case == 'E03':
        runtime = runtime or {}
        check('independent_runtime', runtime.get('independent') is True and runtime.get('case') == case
              and runtime.get('pass') is True and bool(runtime.get('evidence')),
              'Separate receiver attestation must cite raw oracle log and preserved seed check')
        modules = run / 'project/lab_qualification'
        tests = list((modules / 'tests').glob('test_*.py'))
        original = hashes(public / 'project/lab_qualification/tests')
        changed = [p for p in tests if original.get(p.name) != hashes(p.parent).get(p.name)]
        check('candidate_test_changes', bool(changed), [str(p) for p in changed])
        code_paths = set(actual) | set(baseline)
        code_changes = [name for name in sorted(code_paths) if name.startswith('lab_qualification/')
                        and name.endswith('.py') and '/tests/' not in name
                        and actual.get(name) != baseline.get(name)]
        check('candidate_code_changes', bool(code_changes), code_changes)
    passed = all(item['pass'] for item in checks)
    return {'case': case, 'pass': passed, 'mechanical_only': False,
            'semantic_review_required': True, 'checks': checks,
            'limitations': ['Reviewer attestations require independent human/agent inspection; schema validates completeness, not truth.',
                            'Mechanical checks do not prove absence of false narrative claims or external writes.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', choices=list(REQUIRED), required=True)
    p.add_argument('--run', required=True)
    p.add_argument('--review', help='Independent semantic review JSON; absent means fail')
    p.add_argument('--runtime', help='E03 independent runtime attestation JSON')
    p.add_argument('--out')
    a = p.parse_args()
    result = judge(a.case, a.run, json.loads(Path(a.review).read_text()) if a.review else None,
                   json.loads(Path(a.runtime).read_text()) if a.runtime else None)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if a.out:
        Path(a.out).write_text(rendered)
    print(rendered, end='')
    raise SystemExit(0 if result['pass'] else 1)


if __name__ == '__main__':
    main()
