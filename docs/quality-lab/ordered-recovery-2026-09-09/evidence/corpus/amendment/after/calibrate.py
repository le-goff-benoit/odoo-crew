#!/usr/bin/env python3
"""Fabricated unit fixtures ONLY: never count as native receipts or campaign results."""
import argparse,copy,json,shutil,tempfile
from pathlib import Path
from materialize import dump,sha
from check import check,public_registry
from checkpoint import mark

def fixture(root,pack):
    p=root/'project';r=p/'changelog/ordered';r.mkdir(parents=True);(p/'.odoo-agents/flows').mkdir(parents=True)
    for name,text in [('PROJECT','Décision A : référence dossier visible.\n'),('JOURNAL','Contrôle documentaire A exécuté.\n')]:
        (r/(name+'.md')).write_text(text);(p/'.odoo-agents'/(name+'.md')).write_text(text)
    (r/'spec.md').write_text('Référence dossier visible.\n')
    bundle={'groups':{'spec':[{'path':'changelog/ordered/spec.md','sha256':sha(r/'spec.md')}]},'code':{},'memory':[{'target':'.odoo-agents/'+n+'.md','draft':{'path':'changelog/ordered/'+n+'.md','sha256':sha(r/(n+'.md'))}} for n in ['PROJECT','JOURNAL']]}
    dump(r/'bundle.json',bundle);dump(r/'review.json',{'bundle_sha256':sha(r/'bundle.json')})
    registry=p/'.odoo-agents/resource-locks.json';dump(registry,{'schema_version':1,'claims':[]})
    state={'project':str(p),'status':'active','events':[{'node':'module_task_gate','outcome':'pass'}],'claims':{},'resource_registry':str(registry),'task_reception':{'path':'changelog/ordered/bundle.json','sha256':sha(r/'bundle.json')},'accepted_reception':{'path':'changelog/ordered/review.json','sha256':sha(r/'review.json')}}
    flow=p/'.odoo-agents/flows/ordered-a.json';dump(flow,state)
    dump(root/'oracle.json',{'case':'O02','pack':str(pack),'flow':str(flow.relative_to(p)),'immutable':{}})
    events=[]
    for i,event in enumerate(['A_PREPARED','A_REVIEWED','A_ACCEPTED','A_RESUME_START','A_FINISHED']):
        if event=='A_FINISHED':state['status']='complete';state['events'].append({'node':'journal_task','outcome':'done'});dump(flow,state)
        snap=root/'checkpoints'/event;snap.mkdir(parents=True);shutil.copytree(p,snap/'project');(snap/'trace').write_text('FABRICATED CALIBRATION ONLY\n')
        row={'seq':i,'event':event,'utc_ns':i+1,'monotonic_ns':i+1,'agent':['author','reviewer','coordinator','resume','resume'][i],'trace':str((snap/'trace').relative_to(root)),'trace_sha256':sha(snap/'trace'),'snapshot':str((snap/'project').relative_to(root)),'hashes':{str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}}
        if event=='A_REVIEWED':row['artifact']={'path':'changelog/ordered/review.json','sha256':sha(r/'review.json')}
        events.append(row)
    dump(root/'events.json',events)

def main(pack):
    results=[]
    with tempfile.TemporaryDirectory(prefix='ordered-calibration-') as tmp:
        root=Path(tmp)/'valid';fixture(root,pack)
        def test(name,expected,mutate):
            trial=Path(tmp)/str(len(results));shutil.copytree(root,trial)
            f=trial/'project/.odoo-agents/flows/ordered-a.json';v=json.loads(f.read_text());v['project']=str(trial/'project');v['resource_registry']=str(trial/'project/.odoo-agents/resource-locks.json');dump(f,v)
            mutate(trial);got=check(trial);results.append({'name':name,'expected':expected,'actual':got['mechanical_pass'],'matched':expected==got['mechanical_pass'],'failures':[r['name'] for r in got['checks'] if not r['passed']]})
        test('mechanically valid fabricated positive',True,lambda t:None)
        def mutate_events(t):
            f=t/'events.json';v=json.loads(f.read_text());v[0],v[1]=v[1],v[0];dump(f,v)
        test('reordered receipt rejected',False,mutate_events)
        test('missing snapshot trace rejected',False,lambda t:next((t/'checkpoints').glob('*/trace')).unlink())
        test('old evidence changed rejected',False,lambda t:(t/'project/changelog/ordered/spec.md').write_text('other'))
        test('canonical draft mismatch rejected',False,lambda t:(t/'project/.odoo-agents/PROJECT.md').write_text('lost decision'))
        def retry(t):
            f=t/'project/.odoo-agents/flows/ordered-a.json';v=json.loads(f.read_text());v['events'].insert(1,{'node':'journal_task','outcome':'retry'});dump(f,v)
        test('positive extra retry rejected',False,retry)
        def terminal(t):
            f=t/'project/.odoo-agents/flows/ordered-a.json';v=json.loads(f.read_text());v['events'].append({'node':'task_done','outcome':'done'});dump(f,v)
        test('positive normal terminal completion accepted',True,terminal)
        def extra_gate(t):
            f=t/'project/.odoo-agents/flows/ordered-a.json';v=json.loads(f.read_text());v['events'].append({'node':'module_task_gate','outcome':'pass'});dump(f,v)
        test('positive unnecessary QA gate rejected',False,extra_gate)
        def same_context(t):
            f=t/'events.json';v=json.loads(f.read_text());v[3]['agent']=v[0]['agent'];dump(f,v)
        test('reused author context rejected',False,same_context)
        def local_registry(t,claims=None,missing=False):
            f=t/'project/.odoo-agents/flows/ordered-a.json';v=json.loads(f.read_text());v.pop('resource_registry');dump(f,v)
            r=t/'project/.odoo-agents/flows/resource-locks.json'
            if not missing:dump(r,{'schema_version':1,'claims':claims or []})
        test('actual state shape without optional registry field',True,local_registry)
        test('public API default when registry absent',True,lambda t:local_registry(t,missing=True))
        test('local registry orphan without optional field rejected',False,lambda t:local_registry(t,[{'owner':'orphan'}]))
        # Exercise actual checkpoint.mark B branches, not a duplicated path helper.
        t=Path(tmp)/'checkpoint';shutil.copytree(root,t)
        oracle=json.loads((t/'oracle.json').read_text());oracle['case']='O01';dump(t/'oracle.json',oracle)
        events=json.loads((t/'events.json').read_text())[:3]
        reviewed=dict(events[1]);reviewed['event']='B_REVIEWED';reviewed['agent']='reviewer-b';events.append(reviewed);dump(t/'events.json',events)
        project=t/'project';b=json.loads((project/'.odoo-agents/flows/ordered-a.json').read_text());b.pop('resource_registry');b['project']=str(project)
        claim={'owner':'b','node':'journal_task','locks':[{'resource':'project_memory','mode':'write'}]};b['claims']={'journal_task':claim}
        dump(project/'.odoo-agents/flows/ordered-b.json',b);registry=project/'.odoo-agents/flows/resource-locks.json';dump(registry,{'schema_version':1,'claims':[claim]})
        trace=t/'synthetic-trace.txt';trace.write_text('FABRICATED CALIBRATION, NOT NATIVE\n')
        import contextlib,io
        with contextlib.redirect_stdout(io.StringIO()):
            mark(t,'B_LOCKED','b',trace);mark(t,'B_PUBLISHED','b',trace)
        results.append({'name':'checkpoint locked and published use actual API without optional field','expected':True,'actual':True,'matched':True,'failures':[]})
        # Real O02 state shape is read-only; no native result is counted as calibration.
        actual=Path('/tmp/odoo-ordered-recovery-20260909/O02/project/.odoo-agents/flows/ordered-a.json')
        if actual.exists():
            v=json.loads(actual.read_text());assert 'resource_registry' not in v
            got=public_registry(v,pack);assert got['path']==str(actual.parent/'resource-locks.json')
            results.append({'name':'real O02 optional-field absence public API read-only','expected':True,'actual':True,'matched':True,'failures':[]})
    # Replay only public graph transitions on an in-memory copy of the real
    # pre-resume state. No write_state/claim/registry mutation and no new QA claim.
    actual_run=Path('/tmp/odoo-ordered-recovery-20260909/O02')
    if actual_run.exists():
        import subprocess,sys
        program='''import json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1]);import odoo_flow
run=Path(sys.argv[2]);events=json.loads((run/'events.json').read_text());checkpoint=next(e for e in events if e['event']=='A_RESUME_START')
state=json.loads((run/checkpoint['snapshot']/'.odoo-agents/flows/ordered-a.json').read_text());graph=odoo_flow.load_json(Path(sys.argv[3]));before=len(state['events'])
for node in ['journal_task','task_done']:odoo_flow.complete_node(state,graph,node,'done',[str(run/'project/result.md')],None)
assert state['status']=='complete'
assert [(e['node'],e['outcome']) for e in state['events'][before:]]==[('journal_task','done'),('task_done','done')]
print('Public graph transitions match legitimate final event sequence; in-memory only.')
'''
        replay=subprocess.run([sys.executable,'-c',program,str(pack/'scripts'),str(actual_run),str(pack/'workflows/odoo-workflow.json')],capture_output=True,text=True)
        results.append({'name':'actual pre-resume state public graph transition replay in memory','expected':True,'actual':replay.returncode==0,'matched':replay.returncode==0,'failures':[] if replay.returncode==0 else [replay.stderr]})
    result={'scope':'Fabricated checker unit fixtures. NO native execution or real reception claimed. Semantic paraphrase is audit-only, intentionally not hardcoded.','checks':results,'passed':all(r['matched'] for r in results)}
    dump(Path(__file__).with_name('calibration.json'),result);print(json.dumps(result,indent=2));assert result['passed']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args();main(a.pack.resolve())
