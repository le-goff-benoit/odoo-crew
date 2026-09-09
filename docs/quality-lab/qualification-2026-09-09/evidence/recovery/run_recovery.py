#!/usr/bin/env python3
"""One controlled native interruption and same-environment continuation; two paid calls maximum."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading
import time

ROOT = Path('/home/blegoff/.odoo19-agents')
BASE = Path('/tmp/odoo-qualification-20260909/recovery')
PACK = Path('/tmp/odoo-qualification-20260909/candidate')
RUN = BASE / 'run'
PROTOCOL = json.loads((BASE / 'protocol.json').read_text())
sys.path.insert(0, str(PACK / 'scripts'))
import odoo_bench_native as n
from odoo_bench import atomic_json, digest, parse_output, provider_environment


def proc_table():
    data = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            text = (path / 'stat').read_text()
            end = text.rfind(')')
            rest = text[end + 2:].split()
            data[int(path.name)] = {'pid': int(path.name), 'name': text[text.find('(')+1:end],
                'ppid': int(rest[1]), 'pgid': int(rest[2]), 'start_ticks': rest[19], 'state': rest[0]}
        except (OSError, ValueError, IndexError):
            pass
    return data


def descendants(pid):
    data = proc_table()
    selected = {pid}
    while True:
        new = {p for p, d in data.items() if d['ppid'] in selected or d['pgid'] == pid}
        if new <= selected:
            break
        selected |= new
    return [data[p] for p in sorted(selected) if p in data]


def run():
    RUN.mkdir()
    project, home, bridge = RUN/'project', RUN/'home', RUN/'bridge'
    n.copy_project(PACK/'benchmarks/native/cases/N04/project', project)
    for path in [home, bridge]:
        path.mkdir(mode=0o755)
    (bridge/'labctl').write_text(n.CLIENT)
    (bridge/'labctl').chmod(0o755)
    case = json.loads((PACK/'benchmarks/native/cases/N04/case.json').read_text())
    a8 = 'A8 obligatoire : le rejet d’une création avec days=-1 doit être constaté via le vrai XML-RPC et retourner le message « Le nombre de jours doit être positif ou nul. ». Vérifie la conservation des données après rejet. Le code sans appel RPC ne satisfait pas A8.'
    case['request'] += '\n' + a8
    decision = project/'decisions/2026-09-08.md'
    decision.write_text(decision.read_text()+'\n\nExtension synthétique fixée avant cette qualification de reprise : '+a8+'\n')
    n.execute(['git','init','-q',str(project)]).check_returncode()
    n.execute(['git','-C',str(project),'add','.']).check_returncode()
    n.execute(['git','-C',str(project),'-c','user.name=Quality Lab','-c','user.email=lab@example.invalid','commit','-qm','Dossier synthétique N04R initial']).check_returncode()
    config = {'model':'opus','effort':'medium','delegate':True}
    build = n.execute(n.sandbox(home, project, PACK)+['bash',str(n.HOME_PATH/'.odoo19-agents/build.sh')], env=provider_environment())
    (RUN/'build.log').write_text(build.stdout)
    build.check_returncode()
    tree = ast.parse((PACK/'scripts/odoo_bench_native.py').read_text())
    func = next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='_trial')
    assignment = next(x for x in ast.walk(func) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='operational' for t in x.targets))
    operational = eval(compile(ast.Expression(assignment.value), '<frozen operational prompt>', 'eval'), {'delegation_instruction':n.delegation_instruction,'config':config})
    (project/'LAB.md').write_text(operational)
    lab = n.Lab(RUN, PACK, project, case)
    state = {'status':'setting_up','protocol_sha256':digest((BASE/'protocol.json').read_bytes()),'calls':[], 'manual_code_repairs':0}
    server = thread = None
    def save():
        atomic_json(RUN/'state.json',state)
    def start_bridge():
        nonlocal server,thread
        socket = bridge/'control.sock'
        if socket.exists():
            socket.unlink()
        server = n.Bridge(str(socket),n.Handler)
        server.lab=lab
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
    def drain_bridge():
        nonlocal server,thread
        if server:
            server.shutdown()
            thread.join(timeout=360)
            if thread.is_alive():
                raise RuntimeError('Bridge failed to drain; continuation forbidden')
            server.server_close()
            server=thread=None
    def identity(label):
        dbid=lab.compose(['ps','-q','db']).stdout.strip()
        sql="SELECT json_build_object('cluster',(SELECT system_identifier::text FROM pg_control_system()),'postmaster',pg_postmaster_start_time()::text,'databases',(SELECT json_agg(json_build_object('name',datname,'oid',oid)) FROM pg_database WHERE datname IN ('lab_client','lab_qa')));"
        db=lab.compose(['exec','-T','db','psql','-U','odoo','-d','postgres','-Atc',sql]);db.check_returncode()
        rows=lab.compose(['exec','-T','db','psql','-U','odoo','-d','lab_client','-Atc',"SELECT COALESCE(json_agg(t ORDER BY id),'[]') FROM (SELECT id,name,days,daily_rate,amount_total FROM lab_rental) t;"])
        rows.check_returncode()
        value={'container':dbid,'postgres':json.loads(db.stdout),'project_inode':project.stat().st_ino,'git_inode':(project/'.git').stat().st_ino,
            'head':n.execute(['git','rev-parse','HEAD'],cwd=project).stdout.strip(),'rows':json.loads(rows.stdout),
            'decision_hashes':n.source_hashes(project/'decisions'),'module_hashes':n.source_hashes(project/case['module'])}
        atomic_json(RUN/(label+'-identity.json'),value)
        return value
    def native_call(index,prompt,interrupt):
        raw,errors=RUN/f'raw-{index}.jsonl',RUN/f'stderr-{index}.log'
        (RUN/f'prompt-{index}.txt').write_text(prompt)
        timeline=RUN/f'native-events-{index}.jsonl'
        started=time.monotonic(); offset=0; buffered=''; seenqa=set(); observed={}; lastflow=''; stop=False
        cmd=n.sandbox(home,project,PACK,bridge,'claude')+n.native_command('claude',config)+['--max-budget-usd','12']
        with raw.open('w') as out,errors.open('w') as err,timeline.open('w') as events:
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=out,stderr=err,text=True,env=provider_environment(),start_new_session=True)
            proc.stdin.write(prompt);proc.stdin.close()
            while True:
                for p in descendants(proc.pid):
                    observed[(p['pid'],p['start_ticks'])]=p
                with raw.open() as stream:
                    stream.seek(offset);buffered+=stream.read();offset=stream.tell()
                lines=buffered.split('\n');buffered=lines.pop()
                for line in lines:
                    try:event=json.loads(line)
                    except ValueError:continue
                    if event.get('type')=='system' and event.get('subtype') in ('task_started','task_progress','task_notification'):
                        safe={k:event[k] for k in ('type','subtype','task_type','task_id','subagent_type','status','spawn_depth','tool_use_id','last_tool_name','usage') if k in event}
                        events.write(json.dumps({'seconds':round(time.monotonic()-started,3),'event_sha256':digest(line.encode()),'event':safe})+'\n');events.flush()
                        if event.get('subtype')=='task_started' and event.get('task_type')=='local_agent' and 'tester' in str(event.get('subagent_type','')):
                            seenqa.add(event['task_id'])
                flows=[]
                for path in (project/'.odoo-agents/flows').glob('*.json'):
                    try:flows.append(json.loads(path.read_text()))
                    except ValueError:pass
                flowtext=json.dumps(flows,sort_keys=True)
                if flowtext!=lastflow:
                    with (RUN/f'flow-timeline-{index}.jsonl').open('a') as output:
                        output.write(json.dumps({'seconds':round(time.monotonic()-started,3),'flows':flows})+'\n')
                    lastflow=flowtext
                ready=any(any('implementation' in e.get('node','') for e in f.get('events',[])) and
                    len([node for node in f.get('claims',{}) if 'qa' in node])>=2 for f in flows)
                if interrupt and ready and len(seenqa)>=2 and proc.poll() is None:
                    atomic_json(RUN/'interruption-trigger.json',{'seconds':round(time.monotonic()-started,3),'qa_native_ids':sorted(seenqa),'flows':flows,'processes':list(observed.values())})
                    os.killpg(proc.pid,signal.SIGKILL);proc.wait();stop=True;outcome='controlled_interruption';break
                if proc.poll() is not None:
                    outcome='completed' if proc.returncode==0 else 'provider_error';break
                if time.monotonic()-started>=900:
                    os.killpg(proc.pid,signal.SIGKILL);proc.wait();outcome='timeout';break
                time.sleep(.1)
        parsed=parse_output(raw,'claude')
        (RUN/f'answer-{index}.md').write_text(parsed['answer'])
        # Namespace leader death and process-group termination must be demonstrated.
        for attempt in range(50):
            current=proc_table()
            alive=[p for key,p in observed.items() if p['pid'] in current and current[p['pid']]['start_ticks']==p['start_ticks'] and current[p['pid']]['state']!='Z']
            if not alive:break
            time.sleep(.1)
        item={'status':outcome,'exit_code':proc.returncode,'seconds':round(time.monotonic()-started,2),'usage':parsed['usage'],
            'actual_model':parsed['actual_model'],'provider_completed':parsed['completed_event'],'provider_error':parsed['provider_error'],
            'delegation':n.native_delegation_summary(raw,'claude'),'old_processes_absent':not alive,'remaining_processes':alive,'observed_process_count':len(observed)}
        state['calls'].append(item);save()
        print(json.dumps({'call':index,**item}),flush=True)
        if alive:raise RuntimeError('Old worker processes still alive; continuation forbidden')
        return stop
    try:
        save();lab.start();start_bridge();identity('initial')
        state['status']='first_call';save()
        stopped=native_call(0,'Lis LAB.md puis traite la demande suivante jusqu’au résultat prévu par /odoo-new.\n\n'+case['request'],True)
        drain_bridge()
        n.copy_project(project,RUN/'after-interruption')
        cut=identity('after-interruption')
        if not stopped:
            state['status']='not_qualified_no_controlled_interruption';save()
        else:
            preserved=identity('before-resume')
            state['same_environment_before_resume']=cut==preserved
            if not state['same_environment_before_resume']:
                raise RuntimeError('Environment identity changed before continuation')
            interruption_note={'reason':'Superviseur a arrêté le CLI et ses descendants au passage QA, une seule fois.',
                'old_processes_absent':state['calls'][0]['old_processes_absent'],'bridge_drained':True,'same_environment':True,
                'evidence_sha256':digest((RUN/'interruption-trigger.json').read_bytes()),'database':'lab_client et lab_qa conservées, aucune restauration ni recréation','git_head':cut['head']}
            note=project/'.odoo-agents/recovery-interruption.json';atomic_json(note,interruption_note)
            start_bridge();state['status']='second_call';save()
            prompt=('Lis LAB.md et .odoo-agents/recovery-interruption.json. Contexte neuf après interruption contrôlée du premier orchestrateur. '
                'Tous les anciens processus et sous-agents sont terminés, le pont a été drainé. Les mêmes bases lab_client/lab_qa, le module, '
                'les décisions, la release, les preuves et tout le dépôt Git sont conservés. Reprends le flow existant sans rejouer une étape '
                'valide. Libère les revendications abandonnées avec la raison et la preuve de cette interruption, puis réattribue les QA '
                'inachevées à au moins deux vrais sous-agents indépendants si les verrous le permettent. Termine la QA de tâche, la réception '
                'structurée, le journal et le flow, release ouverte. Les critères originaux restent obligatoires, dont A8 du vrai message '
                'RPC. Toute preuve manquante interdit un succès. Ne répare pas un rapport en supprimant un critère.\n\n'+case['request'])
            native_call(1,prompt,False);drain_bridge()
            state['status']='executed'
        n.copy_project(project,RUN/'final-project')
        state['final_identity']=identity('final')
        state['sql_oracle']=lab.oracle()
        # Independent final RPC oracle never changes generated project files or implementation.
        external=RUN/'external-rpc';external.mkdir()
        def rpc(label,method,args):
            file=external/(label+'.json');file.write_text(json.dumps({'model':case['model'],'method':method,'args':args,'kwargs':{}}))
            response=lab.rpc(file);(external/(label+'.log')).write_text(response.stdout)
            return json.loads(response.stdout)
        before=rpc('before','search_read',[[],['name','days','daily_rate','amount_total']])
        negative=rpc('negative-create','create',[{'name':'Independent final RPC negative','days':-1,'daily_rate':17}])
        after=rpc('after','search_read',[[],['name','days','daily_rate','amount_total']])
        state['rpc_oracle']={'negative_fault':negative.get('outcome')=='fault',
            'exact_message_received':'Le nombre de jours doit être positif ou nul.' in negative.get('fault_string',''),
            'rows_preserved':before.get('outcome')=='result' and after.get('outcome')=='result' and before['result']==after['result']}
        state['qualification_review']='pending independent review; executed does not mean qualified'
    except Exception as exc:
        state.update(status='incident',error=str(exc))
        print(json.dumps({'error':str(exc)}),flush=True)
    finally:
        drain_bridge();lab.close()
        containers=n.execute(['docker','ps','-a','--filter','name='+lab.prefix,'--format','{{.Names}}']).stdout.strip()
        networks=n.execute(['docker','network','ls','--filter','name='+lab.prefix,'--format','{{.Name}}']).stdout.strip()
        state['cleanup']={'containers':containers,'networks':networks,'verified':not containers and not networks}
        save()
    return state


if __name__=='__main__':
    result=run()
    print(json.dumps({'status':result['status'],'calls':len(result['calls']),'cleanup':result.get('cleanup')}),flush=True)
