#!/usr/bin/env python3
"""Fabricated unit fixtures ONLY: never count as native receipts or campaign results."""
import copy,json,shutil,tempfile
from pathlib import Path
from materialize import dump,sha
from check import check

def fixture(root):
    p=root/'project';r=p/'changelog/ordered';r.mkdir(parents=True);(p/'.odoo-agents/flows').mkdir(parents=True)
    for name,text in [('PROJECT','Décision A : référence dossier visible.\n'),('JOURNAL','Contrôle documentaire A exécuté.\n')]:
        (r/(name+'.md')).write_text(text);(p/'.odoo-agents'/(name+'.md')).write_text(text)
    (r/'spec.md').write_text('Référence dossier visible.\n')
    bundle={'groups':{'spec':[{'path':'changelog/ordered/spec.md','sha256':sha(r/'spec.md')}]},'code':{},'memory':[{'target':'.odoo-agents/'+n+'.md','draft':{'path':'changelog/ordered/'+n+'.md','sha256':sha(r/(n+'.md'))}} for n in ['PROJECT','JOURNAL']]}
    dump(r/'bundle.json',bundle);dump(r/'review.json',{'bundle_sha256':sha(r/'bundle.json')})
    registry=p/'.odoo-agents/resource-locks.json';dump(registry,{'claims':[]})
    state={'status':'active','events':[{'node':'module_task_gate','outcome':'pass'}],'claims':{},'resource_registry':str(registry),'task_reception':{'path':'changelog/ordered/bundle.json','sha256':sha(r/'bundle.json')},'accepted_reception':{'path':'changelog/ordered/review.json','sha256':sha(r/'review.json')}}
    flow=p/'.odoo-agents/flows/ordered-a.json';dump(flow,state)
    dump(root/'oracle.json',{'case':'O02','flow':str(flow.relative_to(p)),'immutable':{}})
    events=[]
    for i,event in enumerate(['A_PREPARED','A_REVIEWED','A_ACCEPTED','A_RESUME_START','A_FINISHED']):
        if event=='A_FINISHED':state['status']='complete';state['events'].append({'node':'journal_task','outcome':'done'});dump(flow,state)
        snap=root/'checkpoints'/event;snap.mkdir(parents=True);shutil.copytree(p,snap/'project');(snap/'trace').write_text('FABRICATED CALIBRATION ONLY\n')
        row={'seq':i,'event':event,'utc_ns':i+1,'monotonic_ns':i+1,'agent':['author','reviewer','coordinator','resume','resume'][i],'trace':str((snap/'trace').relative_to(root)),'trace_sha256':sha(snap/'trace'),'snapshot':str((snap/'project').relative_to(root)),'hashes':{str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}}
        if event=='A_REVIEWED':row['artifact']={'path':'changelog/ordered/review.json','sha256':sha(r/'review.json')}
        events.append(row)
    dump(root/'events.json',events)

def main():
    results=[]
    with tempfile.TemporaryDirectory(prefix='ordered-calibration-') as tmp:
        root=Path(tmp)/'valid';fixture(root)
        def test(name,expected,mutate):
            trial=Path(tmp)/str(len(results));shutil.copytree(root,trial);mutate(trial);got=check(trial);results.append({'name':name,'expected':expected,'actual':got['mechanical_pass'],'matched':expected==got['mechanical_pass'],'failures':[r['name'] for r in got['checks'] if not r['passed']]})
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
        def same_context(t):
            f=t/'events.json';v=json.loads(f.read_text());v[3]['agent']=v[0]['agent'];dump(f,v)
        test('reused author context rejected',False,same_context)
    result={'scope':'Fabricated checker unit fixtures. NO native execution or real reception claimed. Semantic paraphrase is audit-only, intentionally not hardcoded.','checks':results,'passed':all(r['matched'] for r in results)}
    dump(Path(__file__).with_name('calibration.json'),result);print(json.dumps(result,indent=2));assert result['passed']
if __name__=='__main__':main()
