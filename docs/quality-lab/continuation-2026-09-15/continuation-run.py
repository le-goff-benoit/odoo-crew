import json,os,selectors,shlex,signal,subprocess,time
from pathlib import Path
BASE=Path('/tmp/tricorder-native-continuation-20260915')
CREW=Path('/home/blegoff/.odoo19-agents')
PROBE=CREW/'tests/fixtures/orchestration_probe.py'
results=[]
for provider,model in [('codex','gpt-6-astra'),('claude','opus')]:
    root=BASE/provider
    subprocess.run(['python3',str(PROBE),'prepare',str(root)],check=True,capture_output=True)
    node="const {prepareLaunch}=require('/home/blegoff/odoo-tricorder/electron/provider-launch.cjs'); process.stdout.write(JSON.stringify(prepareLaunch(JSON.parse(process.argv[1]))));"
    params=dict(provider=provider,id='native-'+provider,folder=str(root/'observations'),backend='/home/blegoff/odoo-tricorder/backend',home=str(root),project=str(root),crew=str(CREW))
    launch=json.loads(subprocess.check_output(['node','-e',node,json.dumps(params)],text=True))
    prompt=f"Ceci est un essai natif synthétique borné du hook de continuation, sans projet ni base Odoo. Les tâches A,B,C sont autorisées par l'humain. Exécute maintenant python3 {PROBE} run {root} A puis termine ce tour en annonçant que tu vas exécuter B. N'exécute pas B avant de recevoir un rappel de continuation. Si un rappel arrive, utilise réellement la même commande pour les autres tâches autorisées prêtes jusqu'à réception. Aucun autre outil, aucun autre fichier à lire ou modifier."
    args=shlex.split(launch['command'])
    if provider=='codex':
        args=[args[0],'exec',*args[1:],'--ignore-user-config','--ignore-rules','--ephemeral','--json','--skip-git-repo-check','--sandbox','workspace-write','--model',model,'--dangerously-bypass-hook-trust','-c','model_reasoning_effort="medium"','-c','web_search="disabled"','--disable','apps','--disable','plugins','--disable','multi_agent','-']
    else:
        args+=['--print','--restricted','--strict-mcp-config','--setting-sources','','--tools','Bash','--allowedTools',f'Bash(python3 {PROBE} *)','--no-session-persistence','--output-format','stream-json','--verbose','--include-hook-events','--model',model,'--effort','medium','--max-turns','8']
    start=time.monotonic(); identity=None; activated=False; count=0
    with (root/'native.jsonl').open('w') as out,(root/'native.stderr').open('w') as err:
        process=subprocess.Popen(args,cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1,start_new_session=True)
        process.stdin.write(prompt); process.stdin.close()
        sel=selectors.DefaultSelector(); sel.register(process.stdout,selectors.EVENT_READ)
        while time.monotonic()-start<90:
            found=sel.select(.2)
            if not found and process.poll() is not None: break
            for key,_ in found:
                line=key.fileobj.readline()
                if not line: sel.unregister(key.fileobj); continue
                out.write(line); out.flush()
                try: event=json.loads(line)
                except ValueError: continue
                identity=identity or event.get('thread_id') or (event.get('session_id') if event.get('type')=='system' else None)
                if identity and not activated:
                    activate=['python3',str(CREW/'scripts/odoo_orchestrate.py'),'activate','--project',str(root),'--release',str(root/'changelog/probe'),'--owner',provider+'-orchestrator-probe','--provider',provider,'--model',model,'--session-id',identity,'--task','A','--task','B','--task','C']
                    result=subprocess.run(activate,capture_output=True,text=True)
                    activated=result.returncode==0
                count+=1
            if process.poll() is not None and not sel.get_map(): break
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGTERM)
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(process.pid,signal.SIGKILL); process.wait()
    launches=[json.loads(l) for l in (root/'launches.jsonl').read_text().splitlines()] if (root/'launches.jsonl').exists() else []
    result=dict(provider=provider,model=model,activated=activated,events=count,returncode=process.returncode,elapsed_seconds=round(time.monotonic()-start,3),launches=launches)
    results.append(result)
    (BASE/'results.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(result),flush=True)
