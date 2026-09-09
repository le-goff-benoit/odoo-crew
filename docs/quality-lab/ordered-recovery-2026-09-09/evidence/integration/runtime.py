#!/usr/bin/env python3
"""Runner exclusivement pour les ressources synthétiques enregistrées de cette épreuve."""
import argparse
import json
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'resources.json'
LOGS = ROOT / 'evidence'
LABEL = 'ordered-recovery-owner'


def state():
    return json.loads(STATE.read_text())


def save(s):
    STATE.write_text(json.dumps(s, indent=2) + '\n')


def command(args, label, stdin=None, timeout=360, check=True):
    LOGS.mkdir(exist_ok=True)
    token = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    base = LOGS / (label + '-' + token)
    started = time.monotonic()
    try:
        p = subprocess.run(args, input=stdin, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout)
        rc, output = p.returncode, p.stdout
    except subprocess.TimeoutExpired as e:
        rc = 124
        output = e.stdout or ''
        if isinstance(output, bytes):
            output = output.decode(errors='replace')
    base.with_suffix('.log').write_text(output)
    result = {'command': args, 'returncode': rc, 'seconds': round(time.monotonic()-started,3),
              'log': str(base.with_suffix('.log'))}
    base.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result), flush=True)
    if check and rc:
        raise RuntimeError(f'{label}: exit {rc}; {result["log"]}')
    return rc, output, base


def odoo(action, db='ordered_copy', tags='/lab_qualification:TestQuantity', script=None):
    if db not in ('ordered_seed', 'ordered_copy'):
        raise ValueError('Base non autorisée')
    s=state()
    name=s['prefix']+'-odoo-'+uuid.uuid4().hex[:10]
    s['containers'].append(name);save(s)
    args=['docker','run','--rm','-i','--name',name,'--label',LABEL+'='+s['owner'],
          '--network',s['network'],'--tmpfs','/var/lib/odoo:mode=1777',
          '--mount',f'type=bind,src={s["project"]},dst=/mnt/extra-addons,readonly',
          '--entrypoint','odoo',s['images']['odoo-qa:19.0']['id']]
    if action in ('shell','inventory'):
        args += ['shell']
    args += ['--db_host',s['postgres'],'--db_user','odoo','--db_password','synthetic-lab-only',
             '-d',db,'--addons-path','/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons',
             '--data-dir','/tmp/odoo-data','--without-demo','--no-http','--max-cron-threads','0','--workers','0']
    if action not in ('shell','inventory'):
        args += ['--stop-after-init','-i' if action=='run' else '-u','lab_qualification']
    if action=='test':
        args += ['--test-enable','--test-tags',tags,'--log-level','test']
    try:
        rc,out,base=command(args,action+'-'+db,stdin=script,check=False)
        if action=='test':
            summaries=[tuple(map(int,x)) for x in re.findall(r'(\d+) failed, (\d+) error\(s\) of (\d+) tests',out)]
            started=re.findall(r'Starting (Test\w+\.test_\w+)',out)
            valid=bool(summaries) and any(x[2]>0 for x in summaries) and bool(started)
            passed=rc==0 and valid and all(x[0]==x[1]==0 for x in summaries)
            result={'tags':tags,'process_exit':rc,'summaries':summaries,'started_tests':started,
                    'summary_present_and_tests_started':valid,'pass':passed,
                    'markers':sorted(set(re.findall(r'QUALIFICATION_PASS (\w+)',out)))}
            base.with_suffix('.tests.json').write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps(result))
            return (0 if passed else (rc or 1)),out,base
        return rc,out,base
    finally:
        # --rm normal; targeted removal also covers timeout and interrupts.
        remove_owned(name,'container',s)


def remove_owned(name,kind,s):
    rc,out,_=command(['docker',kind,'inspect',name], 'inspect-cleanup',check=False,timeout=30)
    if rc:
        return
    obj=json.loads(out)[0]
    labels=obj.get('Config',{}).get('Labels',{}) if kind=='container' else obj.get('Labels',{})
    if (labels or {}).get(LABEL)!=s['owner']:
        raise RuntimeError('Refus nettoyage ressource hors propriétaire: '+name)
    command(['docker','rm','-f',name] if kind=='container' else ['docker','network','rm',name],
            'cleanup-'+kind,timeout=30)


def cleanup():
    s=state()
    for name in reversed(s['containers']):
        remove_owned(name,'container',s)
    remove_owned(s['network'],'network',s)
    remaining=[]
    for name in s['containers']:
        rc,_,_=command(['docker','container','inspect',name],'verify-cleanup',check=False,timeout=30)
        if rc==0: remaining.append(name)
    rc,_,_=command(['docker','network','inspect',s['network']],'verify-cleanup',check=False,timeout=30)
    if rc==0:remaining.append(s['network'])
    (LOGS/'cleanup.json').write_text(json.dumps({'remaining':remaining,'verified':not remaining},indent=2)+'\n')
    if remaining:raise RuntimeError('Nettoyage incomplet')


def inventory(db):
    script="""import json
records=env['lab.qualification'].search([],order='id')
print('ORDERED_INVENTORY_JSON='+json.dumps({'database':env.cr.dbname,'records':records.read(['name','state','quantity','unit_price','amount']),'module':env['ir.module.module'].search([('name','=','lab_qualification')]).read(['name','state','installed_version'])},sort_keys=True))
"""
    rc,out,base=odoo('inventory',db,script=script)
    if rc:raise RuntimeError('ORM inventory failed')
    matches=re.findall(r'ORDERED_INVENTORY_JSON=(\{[^\n]*\})',out)
    if len(matches)!=1:raise RuntimeError('ORM inventory missing')
    data=json.loads(matches[0]);base.with_suffix('.inventory.json').write_text(json.dumps(data,indent=2)+'\n')
    sql="SELECT current_database() AS database, id, name, state, quantity, unit_price, amount FROM lab_qualification ORDER BY id; SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='lab_qualification'::regclass ORDER BY conname;"
    command(['docker','exec',state()['postgres'],'psql','-U','odoo','-d',db,'-X','-v','ON_ERROR_STOP=1','-c',sql], 'sql-inventory-'+db)
    return data,base.with_suffix('.inventory.json')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['run','update','test','shell','inventory','cleanup'])
    parser.add_argument('--db',choices=['ordered_seed','ordered_copy'],default='ordered_copy')
    parser.add_argument('--tags',default='/lab_qualification:TestQuantity')
    parser.add_argument('--script',type=Path,help='Python file for Odoo shell; otherwise stdin')
    args=parser.parse_args()
    if args.action=='cleanup':cleanup();return 0
    if args.action=='inventory':
        data,path=inventory(args.db);print(json.dumps({'inventory':str(path),'data':data}));return 0
    script=(args.script.read_text() if args.script else sys.stdin.read()) if args.action=='shell' else None
    return odoo(args.action,args.db,args.tags,script)[0]


if __name__=='__main__':
    raise SystemExit(main())
