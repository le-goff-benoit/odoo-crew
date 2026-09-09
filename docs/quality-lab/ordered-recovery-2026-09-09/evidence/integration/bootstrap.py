#!/usr/bin/env python3
import hashlib
import json
import time
import uuid
from pathlib import Path
import runtime as r


def main():
    if r.STATE.exists():raise RuntimeError('Bootstrap already recorded; refusing recreate')
    owner=uuid.uuid4().hex
    prefix='ordered-recovery-'+owner[:12]
    s={'owner':owner,'prefix':prefix,'network':prefix,'postgres':prefix+'-pg',
       'containers':[prefix+'-pg'],'project':str(r.ROOT/'run/project'),
       'databases':['ordered_seed','ordered_copy'],'images':{},'kind':'synthetic dump/restore copy; no customer data'}
    r.save(s)
    try:
        for image in ('odoo-qa:19.0','postgres:16'):
            _,out,_=r.command(['docker','image','inspect',image],'image-inspect')
            obj=json.loads(out)[0];s['images'][image]={'id':obj['Id'],'digests':obj.get('RepoDigests',[])}
        r.save(s)
        r.command(['docker','network','create','--internal','--label',r.LABEL+'='+owner,s['network']],'network-create')
        r.command(['docker','run','-d','--name',s['postgres'],'--label',r.LABEL+'='+owner,'--network',s['network'],
                   '--tmpfs','/var/lib/postgresql/data','-e','POSTGRES_USER=odoo','-e','POSTGRES_PASSWORD=synthetic-lab-only',
                   s['images']['postgres:16']['id']],'postgres-create')
        for _ in range(30):
            if r.command(['docker','exec',s['postgres'],'pg_isready','-U','odoo'],'pg-ready',check=False)[0]==0:break
            time.sleep(1)
        else:raise RuntimeError('PG readiness timeout')
        r.command(['docker','container','inspect',s['postgres']],'postgres-identity')
        r.command(['docker','network','inspect',s['network']],'network-identity')
        if r.odoo('run','ordered_seed')[0]:raise RuntimeError('Initial module installation failed')
        seed="""records=env['lab.qualification'].create([
{'name':'ordered-seed-draft-zero','state':'draft','quantity':0,'unit_price':10},
{'name':'ordered-seed-draft-positive','state':'draft','quantity':3,'unit_price':10},
{'name':'ordered-seed-confirmed-positive','state':'confirmed','quantity':3,'unit_price':10},
])
env.flush_all()
env.cr.commit()
print('ORDERED_SEED_IDS='+repr(records.ids))
"""
        (r.ROOT/'seed.py').write_text(seed)
        if r.odoo('shell','ordered_seed',script=seed)[0]:raise RuntimeError('Seed failed')
        before,beforepath=r.inventory('ordered_seed')
        r.command(['docker','exec',s['postgres'],'pg_dump','-U','odoo','-Fc','-f','/tmp/ordered_seed.dump','ordered_seed'],'dump-seed')
        r.command(['docker','cp',s['postgres']+':/tmp/ordered_seed.dump',str(r.LOGS/'ordered_seed.dump')],'archive-dump')
        r.command(['docker','exec',s['postgres'],'createdb','-U','odoo','ordered_copy'],'create-copy')
        r.command(['docker','exec',s['postgres'],'pg_restore','-U','odoo','--exit-on-error','-d','ordered_copy','/tmp/ordered_seed.dump'],'restore-copy')
        after,afterpath=r.inventory('ordered_copy')
        assert before['records']==after['records'] and len(before['records'])==3
        assert [(x['state'],x['quantity'],x['unit_price'],x['amount']) for x in before['records']]==[('draft',0,10.,0.),('draft',3,10.,30.),('confirmed',3,10.,30.)]
        initial_hashes={str(p.relative_to(r.ROOT/'run/project')):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((r.ROOT/'run/project/lab_qualification').rglob('*')) if p.is_file()}
        result={'ready':True,'initial_module_hashes':initial_hashes,'seed_inventory':str(beforepath),'copy_inventory':str(afterpath),
                'preserved_ids_values':True,'dump':str(r.LOGS/'ordered_seed.dump'),'dump_sha256':hashlib.sha256((r.LOGS/'ordered_seed.dump').read_bytes()).hexdigest()}
        (r.LOGS/'bootstrap-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result))
    except BaseException:
        r.cleanup()
        raise


if __name__=='__main__':main()
