#!/usr/bin/env python3
"""Judge-only event ledger. Trace hashes are evidence anchors, NOT agent certification."""
import argparse, hashlib, json, shutil, time
from pathlib import Path
from materialize import sha,dump
from check import public_registry
EVENTS=['A_PREPARED','A_REVIEWED','A_ACCEPTED','B_REVIEWED','B_LOCKED','B_PUBLISHED','A_RESUME_START','A_FINISHED']
def mark(folder,event,agent,trace,artifact=None):
    events=json.loads((folder/'events.json').read_text()); oracle=json.loads((folder/'oracle.json').read_text());project=folder/'project'
    if any(e['event']==event for e in events): raise ValueError('Event already sealed')
    required={'A_REVIEWED':'A_PREPARED','A_ACCEPTED':'A_REVIEWED','B_REVIEWED':'A_ACCEPTED','B_LOCKED':'B_REVIEWED','B_PUBLISHED':'B_LOCKED','A_RESUME_START':'B_PUBLISHED' if oracle['case']=='O01' else 'A_ACCEPTED','A_FINISHED':'A_RESUME_START'}
    if event in required and required[event] not in [e['event'] for e in events]: raise ValueError('Missing predecessor '+required[event])
    if not trace.is_file() or not trace.stat().st_size: raise ValueError('Actual exported native trace required')
    state=json.loads((project/oracle['flow']).read_text())
    if event=='A_PREPARED': assert state.get('task_reception') and not state.get('accepted_reception')
    if event=='A_ACCEPTED':
        accepted=state['accepted_reception'];review=next(e for e in events if e['event']=='A_REVIEWED')
        assert accepted['sha256']==review['artifact']['sha256']
        assert any(e['node']=='module_task_gate' and e['outcome']=='pass' for e in state['events'])
    if event in ['B_LOCKED','B_PUBLISHED']:
        b=json.loads((project/'.odoo-agents/flows/ordered-b.json').read_text());claim=b['claims']['journal_task']
        registry=public_registry(b,oracle['pack'])['registry'];assert claim in registry['claims']
        assert b['accepted_reception']['sha256']==next(e for e in events if e['event']=='B_REVIEWED')['artifact']['sha256']
        if event=='B_PUBLISHED':
            bundle=json.loads((project/b['task_reception']['path']).read_text())
            assert all(sha(project/r['target'])==r['draft']['sha256'] for r in bundle['memory'])
    if event=='A_RESUME_START':
        original=next(e for e in events if e['event']=='A_PREPARED')
        assert agent != original['agent'], 'Fresh native agent/context required'
        if oracle['case']=='O01': assert not json.loads((project/'.odoo-agents/flows/ordered-b.json').read_text()).get('claims')
    snap=folder/'checkpoints'/f'{len(events):02d}-{event}';snap.mkdir(parents=True)
    shutil.copytree(project,snap/'project')
    shutil.copyfile(trace,snap/'native-trace.txt')
    row={'seq':len(events),'event':event,'utc_ns':time.time_ns(),'monotonic_ns':time.monotonic_ns(),'agent':agent,'trace':str((snap/'native-trace.txt').relative_to(folder)),'trace_sha256':sha(snap/'native-trace.txt'),'snapshot':str((snap/'project').relative_to(folder)),'hashes':{str(p.relative_to(project)):sha(p) for p in project.rglob('*') if p.is_file()}}
    if artifact:
        assert artifact.is_relative_to(project)
        row['artifact']={'path':str(artifact.relative_to(project)),'sha256':sha(artifact)}
    if event.endswith('REVIEWED'): assert artifact and agent != next(e for e in events if e['event']=='A_PREPARED')['agent']
    events.append(row);dump(folder/'events.json',events);print(json.dumps(row,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('event',choices=EVENTS);p.add_argument('--agent',required=True);p.add_argument('--trace',type=Path,required=True);p.add_argument('--artifact',type=Path);a=p.parse_args();mark(a.folder.resolve(),a.event,a.agent,a.trace.resolve(),a.artifact.resolve() if a.artifact else None)
