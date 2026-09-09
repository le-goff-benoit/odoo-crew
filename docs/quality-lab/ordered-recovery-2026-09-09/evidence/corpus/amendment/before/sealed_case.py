#!/usr/bin/env python3
"""JUDGE ONLY: do not disclose until candidate freeze. Inject after actual A_ACCEPTED."""
import argparse,json
from pathlib import Path
from materialize import sha,dump

def inject(folder):
    oracle=json.loads((folder/'oracle.json').read_text());events=json.loads((folder/'events.json').read_text())
    assert oracle['case']=='O03' and events[-1]['event']=='A_ACCEPTED'
    assert 'judge_mutation' not in oracle
    project=folder/'project';state=json.loads((project/oracle['flow']).read_text());path=project/state['accepted_reception']['path'];before=sha(path)
    # A receipt whose parsed verdict is unchanged but whose accepted bytes changed.
    # The real original is retained in the immutable A_ACCEPTED snapshot.
    path.write_bytes(path.read_bytes()+b'\n')
    oracle['judge_mutation']={'path':str(path.relative_to(project)),'before':before,'after':sha(path),'reason':'accepted receipt integrity breach; semantic JSON unchanged; no memory or scoped source conflict'}
    dump(folder/'oracle.json',oracle)
    print('Sealed judge mutation applied; preserve original snapshot and modified receipt.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();inject(a.folder.resolve())
