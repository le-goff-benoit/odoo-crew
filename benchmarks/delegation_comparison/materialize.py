#!/usr/bin/env python3
"""Materialize public inputs only; freeze public and private hashes separately."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

CASES = Path(__file__).resolve().parent / 'cases'


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def materialize(case, target, mode=None):
    source = CASES / case / 'public'
    if not source.is_dir():
        raise ValueError(f'Unknown case {case}')
    target = Path(target).resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError(f'Target must be absent or empty: {target}')
    shutil.copytree(source, target, dirs_exist_ok=True)
    (target / 'output').mkdir(exist_ok=True)
    task = (target / 'task.md').read_text().replace('PROJECT_PATH', str(target / 'project'))
    modes = {
        'S': '\nCondition S : travailler seul, sans sous-agent.\n',
        'D': '\nCondition D : délégation disponible à au plus deux sous-agents ; libre de travailler seul. Ne déléguer que des tâches indépendantes ; les mêmes obligations et livrables s’appliquent.\n',
    }
    (target / 'prompt.md').write_text(task + modes.get(mode, ''))
    manifest = {'case': case, 'mode': mode, 'public_hashes': hashes(source),
                'baseline_project_hashes': hashes(source / 'project'),
                'private_hashes': hashes(CASES / case / 'private')}
    # Evaluation metadata stays outside candidate project; private file contents never copied.
    manifest_path = target.parent / (target.name + '.inputs.json')
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    return {'run': str(target), 'prompt': str(target / 'prompt.md'), 'manifest': str(manifest_path)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', choices=['E01', 'E02', 'E03'], required=True)
    p.add_argument('--target', '--out', required=True)
    p.add_argument('--mode', choices=['S', 'D'])
    args = p.parse_args()
    print(json.dumps(materialize(args.case, args.target, args.mode), ensure_ascii=False))


if __name__ == '__main__':
    main()
