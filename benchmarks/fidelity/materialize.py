#!/usr/bin/env python3
"""Materialize immutable reception dossiers; no model or Odoo calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def materialize(case_id, output):
    manifest = json.loads((HERE / 'cases.json').read_text())
    case = next(item for item in manifest['cases'] if item['id'] == case_id)
    output = Path(output)
    if output.exists():
        raise ValueError(f'Output must be new: {output}')
    project = output / 'project'
    project.mkdir(parents=True)
    for item in case['files']:
        source = ROOT / item['source']
        if digest(source) != item['sha256']:
            raise ValueError(f'Frozen source changed: {source}')
        target = project / item['target']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (output / 'prompt.txt').write_text((HERE / 'prompt.txt').read_text())
    (output / 'input-sha256.json').write_text(json.dumps({item['target']: item['sha256'] for item in case['files']}, indent=2, ensure_ascii=False) + '\n')
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=['F01', 'F02', 'F03', 'F04', 'F05'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(materialize(args.case, args.output))
