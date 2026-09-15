#!/usr/bin/env python3
"""Campagnes natives isolées : vrais CLI, profils figés, outils et Odoo synthétique.

Le pont labctl ne permet que QA, mise à niveau et shell Odoo sur la copie du run.
Aucun socket Docker ni corrigé n'est monté dans l'espace de l'agent.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import signal
import select
import socket
import socketserver
import subprocess
import tarfile
import threading
import time
import uuid
import xmlrpc.client

from odoo_bench import atomic_json, digest, now, parse_output, provider_environment
from odoo_test_result import inspect_log

ROOT = Path(__file__).resolve().parents[1]
HOME_PATH = Path.home()


class RpcTransport(xmlrpc.client.Transport):
    def make_connection(self, host):
        connection = super().make_connection(host)
        connection.timeout = 5
        return connection


CLIENT = '''#!/usr/bin/env python3
import json, socket, sys
s=socket.socket(socket.AF_UNIX); s.connect('/bridge/control.sock')
s.sendall((json.dumps({'args':sys.argv[1:]})+'\\n').encode());s.shutdown(socket.SHUT_WR)
data=b''
while True:
 chunk=s.recv(65536)
 if not chunk:break
 data+=chunk
r=json.loads(data);print(r.get('output',''),end='');sys.exit(r['exit_code'])
'''


def execute(args, *, cwd=None, env=None, input=None, timeout=300):
    return subprocess.run(args, cwd=cwd, env=env, input=input, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)


def inside(path, root):
    path = Path(path)
    if path.is_absolute():
        path = Path(str(path).removeprefix('/work/')) if str(path).startswith('/work/') else path
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise ValueError('fichier hors du projet synthétique ou absent')
    return resolved


def source_hashes(folder):
    return {str(p.relative_to(folder)): digest(p.read_bytes()) for p in sorted(folder.rglob('*'))
            if p.is_file() and not p.is_symlink() and '.git' not in p.parts and '__pycache__' not in p.parts}


def runtime_reception(state, events, module_hashes):
    """A mechanical gate, never a substitute for independent semantic reception."""
    checks = {
        'provider_completed': state.get('status') == 'executed'
                              and not any(turn.get('error') for turn in state.get('turns', [])),
        'oracle_passed': state.get('oracle', {}).get('passed') is True,
    }
    for action in ('lint', 'qa', 'update'):
        matching = [event for event in events if event.get('args', [None])[0] == action
                    and event.get('module_sources_before') == module_hashes
                    and event.get('module_sources_after') == module_hashes]
        # A later failed check cannot be hidden by an earlier successful run.
        latest = matching[-1] if matching else {}
        checks[action + '_final_sources'] = bool(module_hashes) and latest.get('exit_code') == 0
        if action == 'qa':
            checks['qa_final_sources'] &= latest.get('test_result', {}).get('valid') is True
    return {'passed': all(checks.values()), 'checks': checks,
            'semantic_review': 'pending', 'time_to_accepted_receipt_seconds': None}


def copy_project(source, target):
    excluded = {'.git', '__pycache__', '.tools', '.cache'}
    # Les environnements installés par les agents sont des dépendances locales,
    # pas des livrables. Leurs liens vers Python système ne sortent pas du sandbox.
    virtualenvs = {p.parent for p in source.rglob('pyvenv.cfg')}
    def ignored(path):
        return any(part in excluded for part in path.relative_to(source).parts) or any(path.is_relative_to(v) for v in virtualenvs)
    for p in source.rglob('*'):
        if not ignored(p) and p.is_symlink():
            raise ValueError('lien symbolique interdit dans les livrables du banc : ' + str(p))
    def ignore(directory, names):
        return [name for name in names if ignored(Path(directory) / name)]
    shutil.copytree(source, target, ignore=ignore)
    for p in [target, *target.rglob('*')]:
        p.chmod(0o755 if p.is_dir() else 0o644)


def export_revision(revision, target):
    archive = execute(['git', 'rev-parse', '--verify', revision + '^{commit}'], cwd=ROOT)
    archive.check_returncode()
    sha = archive.stdout.strip()
    target.mkdir(parents=True)
    data = subprocess.check_output(['git', 'archive', sha], cwd=ROOT)
    import io
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for item in tar.getmembers():
            if item.issym() or item.islnk() or not (target / item.name).resolve().is_relative_to(target):
                raise ValueError('archive non sûre')
        tar.extractall(target)
    return sha


def sandbox(home, workspace, pack, bridge=None, provider=None):
    args = ['bwrap', '--die-with-parent', '--unshare-pid', '--unshare-ipc', '--unshare-uts',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64',
            '--symlink', 'usr/bin', '/bin', '--ro-bind', '/etc', '/etc', '--proc', '/proc', '--dev', '/dev',
            '--tmpfs', '/tmp', '--tmpfs', '/run', '--bind', str(home), str(HOME_PATH),
            '--ro-bind', str(pack), str(HOME_PATH / '.odoo19-agents'),
            '--bind', str(workspace), '/work', '--chdir', '/work', '--dir', '/opt']
    resolver = Path('/etc/resolv.conf').resolve()
    if str(resolver).startswith('/run/'):
        args += ['--ro-bind', str(resolver), str(resolver)]
    for series in ('19.0', '19.0-enterprise'):
        sources = HOME_PATH / 'odoo-sources' / series
        if sources.is_dir():
            args += ['--ro-bind', str(sources), str(sources)]
    if bridge:
        args += ['--ro-bind', str(bridge), '/bridge']
    if provider:
        # Les profils/outils sont visibles, jamais les cas, corrigés ou rapports du banc.
        for relative in ('benchmarks', 'tests', 'docs/quality-lab'):
            if (pack / relative).exists():
                args += ['--tmpfs', str(HOME_PATH / '.odoo19-agents' / relative)]
        auth_rel = '.codex/auth.json' if provider == 'codex' else '.claude/.credentials.json'
        auth = HOME_PATH / auth_rel
        if not auth.is_file():
            raise ValueError('authentification locale absente : ' + provider)
        (home / Path(auth_rel).parent).mkdir(parents=True, exist_ok=True)
        args += ['--ro-bind', str(auth), str(auth)]
        binary = Path(shutil.which(provider) or '')
        if provider == 'codex':
            node = binary.parent.parent
            if not (node / 'bin/node').is_file():
                raise ValueError('installation npm Codex requise')
            args += ['--ro-bind', str(node), '/opt/node']
        else:
            args += ['--ro-bind', str(binary.resolve()), '/opt/claude']
    return args


def native_command(provider, config):
    if provider == 'codex':
        if config.get('delegate'):
            raise ValueError('option de délégation native prise en charge uniquement pour Claude dans ce banc')
        args = ['/opt/node/bin/codex', 'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral',
                '--json', '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox',
                '--model', config['model'], '-c', 'model_reasoning_effort=' + json.dumps(config['effort']),
                '-c', 'web_search="disabled"']
        for feature in ('apps', 'plugins', 'multi_agent', 'memories', 'hooks', 'browser_use', 'computer_use', 'image_generation'):
            args += ['--disable', feature]
        return args + ['-']
    tool_names = 'Bash,Read,Write,Edit,Glob,Grep,Skill'
    if config.get('delegate'):
        tool_names += ',Agent,TaskOutput,TaskStop'
    return ['/opt/claude', '--print', '--dangerously-skip-permissions', '--strict-mcp-config',
            '--mcp-config', '{"mcpServers":{}}', '--no-session-persistence', '--output-format', 'stream-json',
            '--verbose', '--tools', tool_names, '--model', config['model'],
            '--effort', config['effort']]


def delegation_instruction(config):
    if not config.get('delegate'):
        return 'Dans cette campagne, applique les rôles toi-même (pas de sous-agent). '
    return ('Dans cet essai de délégation réelle, utilise les sous-agents natifs avec les profils générés. '
            'Délègue au moins deux voies QA indépendantes dans une même vague si leurs verrous sont compatibles. '
            'L’orchestrateur seul pilote le graphe et fusionne les preuves. '
            'Donne à chaque enfant son rôle, périmètre, preuve isolée et briefing. '
            'Les autres agents travaillent dans le même projet : aucune modification hors du périmètre attribué, '
            'aucun retour sur les modifications d’autrui. '
            'Une délégation refusée ou inachevée reste un incident explicite, sans faux succès. ')


def native_delegation_summary(raw, provider):
    """Compter les enfants attestés ; un lancement n'est ni un succès ni un gain."""
    if provider != 'claude':
        return {'supported': False}
    tasks = {}
    provider_summary = None
    for line in Path(raw).read_text(errors='replace').splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get('type') == 'system':
            task_id = event.get('task_id')
            if event.get('subtype') == 'task_started' and event.get('task_type') == 'local_agent' and task_id:
                tasks[task_id] = {'role': event.get('subagent_type'), 'tool_use_id': event.get('tool_use_id'),
                                  'spawn_depth': event.get('spawn_depth'), 'progress_events': 0, 'status': 'incomplete'}
            elif task_id in tasks:
                if event.get('subtype') == 'task_progress':
                    tasks[task_id]['progress_events'] += 1
                elif event.get('subtype') == 'task_notification':
                    tasks[task_id]['status'] = event.get('status', 'incomplete')
        elif event.get('type') == 'result' and not event.get('parent_tool_use_id'):
            provider_summary = event.get('subagent_stats')
    return {'supported': True, 'started': len(tasks),
            'with_progress': sum(bool(t['progress_events']) for t in tasks.values()),
            'completed': sum(t['status'] == 'completed' for t in tasks.values()),
            'tasks': tasks, 'provider_summary': provider_summary}


class Lab:
    def __init__(self, folder, pack, project, case):
        self.folder, self.pack, self.project, self.case = folder, pack, project, case
        self.backend = folder / 'backend'
        self.backend.mkdir()
        for name in ('scripts', 'stack', 'addons'):
            (self.backend / name).mkdir()
        for name in ('odoo-test.sh', 'series-env.sh', 'odoo_test_result.py', 'odoo_series.py'):
            if (pack / 'scripts' / name).exists():
                shutil.copy2(pack / 'scripts' / name, self.backend / 'scripts' / name)
        shutil.copy2(pack / 'stack/odoo.conf', self.backend / 'stack/odoo.conf')
        self.prefix = 'quality-native-' + uuid.uuid4().hex[:10]
        compose = {'name': self.prefix, 'services': {
            'db': {'image': 'postgres:16', 'environment': {'POSTGRES_USER': 'odoo', 'POSTGRES_PASSWORD': 'odoo'},
                   'tmpfs': ['/var/lib/postgresql/data'], 'mem_limit': '512m'},
            'odoo': {'image': 'odoo-qa:19.0', 'environment': {'HOST': 'db', 'USER': 'odoo', 'PASSWORD': 'odoo'},
                     'read_only': True, 'tmpfs': ['/tmp', '/var/lib/odoo:mode=1777'], 'mem_limit': '2g',
                     'volumes': [str(self.backend / 'addons') + ':/mnt/extra-addons:ro',
                                 str(HOME_PATH / 'odoo-sources/19.0-enterprise') + ':/mnt/enterprise-addons:ro',
                                 str(self.backend / 'stack/odoo.conf') + ':/etc/odoo/odoo.conf:ro',
                                 str(self.backend / 'stack/artifacts') + ':/mnt/artifacts']},
        }, 'networks': {'default': {'internal': True}}}
        (self.backend / 'stack/docker-compose.yml').write_text(json.dumps(compose))
        (self.backend / 'stack/artifacts').mkdir(mode=0o777)
        (self.backend / 'stack/artifacts').chmod(0o777)
        self.env = dict(os.environ, ODOO_SERIES='19.0', ODOO_ADDONS_DIR=str(self.backend / 'addons'),
                        COMPOSE_PROJECT_NAME=self.prefix, XDG_CACHE_HOME=str(self.backend / 'cache'))
        self.proxy = None
        self.events = []
        self.lock = threading.Lock()

    def compose(self, args, **kw):
        return execute(['docker', 'compose'] + args, cwd=self.backend / 'stack', env=self.env, **kw)

    def sync(self):
        module = self.case['module']
        if module:
            dest = self.backend / 'addons' / module
            if dest.exists():
                shutil.rmtree(dest)
            copy_project(self.project / module, dest)

    def odoo(self, extra, script=None):
        args = ['run', '--rm', '-T', '--no-deps', 'odoo', 'odoo']
        if script is not None:
            args += ['shell']
        args += ['-c', '/etc/odoo/odoo.conf', '-d', 'lab_client', '--no-http', '--max-cron-threads=0',
                 '--without-demo=all', '--stop-after-init'] + extra
        return self.compose(args, input=script)

    def start(self):
        self.compose(['up', '-d', 'db']).check_returncode()
        for _ in range(60):
            if self.compose(['exec', '-T', 'db', 'pg_isready', '-U', 'odoo']).returncode == 0:
                break
            time.sleep(.5)
        else:
            raise RuntimeError('PostgreSQL indisponible')
        self.sync()
        module = self.case['module'] or 'web_studio'
        r = self.odoo(['-i', module])
        (self.folder / 'setup.log').write_text(r.stdout)
        r.check_returncode()
        self.compose(['exec', '-T', 'db', 'createdb', '-U', 'odoo', 'lab_qa']).check_returncode()
        seed = (ROOT / 'benchmarks/native/oracles' / (self.case['id'] + '_seed.py')).read_text()
        r = self.odoo([], seed)
        (self.folder / 'seed.log').write_text(r.stdout)
        r.check_returncode()
        if 'LAB_SEEDED' not in r.stdout:
            raise RuntimeError('amorçage non attesté')
        self.url = None
        if self.case['kind'] == 'studio':
            self.start_http()
        atomic_json(self.folder / 'environment.json', {
            'prefix': self.prefix, 'image_id': execute(['docker', 'image', 'inspect', '--format={{.Id}}', 'odoo-qa:19.0']).stdout.strip(),
            'series': '19.0', 'database': 'lab_client', 'qa_database': 'lab_qa', 'url': self.url,
            'initial_project': source_hashes(self.project)})

    def start_http(self):
        # Port aléatoire de boucle locale seulement, aucune exposition distante.
        r = self.compose(['run', '-d', '--no-deps', '--name', self.prefix + '-web',
                          'odoo', 'odoo', '-c', '/etc/odoo/odoo.conf',
                          '-d', 'lab_client', '--db-filter=^lab_client$', '--max-cron-threads=0'])
        r.check_returncode()
        networks = json.loads(execute(['docker', 'inspect', self.prefix + '-web', '--format={{json .NetworkSettings.Networks}}']).stdout)
        target_ip = next(iter(networks.values()))['IPAddress']
        self.proxy = Proxy(('127.0.0.1', 0), ProxyHandler)
        self.proxy.target = (target_ip, 8069)
        threading.Thread(target=self.proxy.serve_forever, daemon=True).start()
        self.url = 'http://127.0.0.1:' + str(self.proxy.server_address[1])
        for _ in range(90):
            try:
                with xmlrpc.client.ServerProxy(self.url + '/xmlrpc/2/common', transport=RpcTransport()) as rpc:
                    if not rpc.authenticate('lab_client', 'admin', 'admin', {}):
                        raise RuntimeError('auth synthétique non prête')
                break
            except Exception:
                time.sleep(.5)
        else:
            (self.folder / 'web-error.log').write_text(execute(['docker', 'logs', self.prefix + '-web']).stdout)
            raise RuntimeError('HTTP synthétique indisponible')

    def stop_http(self):
        if self.proxy:
            self.proxy.shutdown()
            self.proxy.server_close()
            self.proxy = None
        execute(['docker', 'rm', '-f', self.prefix + '-web'], timeout=30)
        self.url = None

    def rpc(self, script):
        """Traverser le vrai service, dans le modèle et la base synthétiques du cas.

        Un serveur neuf à chaque appel évite de tester un ancien registre après
        sync/update. Le code de sortie signale le Fault, pas un verdict de QA.
        """
        request = json.loads(script.read_text())
        if (not isinstance(request, dict) or set(request) != {'model', 'method', 'args', 'kwargs'}
                or request['model'] != self.case['model']
                or not isinstance(request['method'], str)
                or not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]*', request['method'])
                or not isinstance(request['args'], list) or not isinstance(request['kwargs'], dict)):
            raise ValueError('RPC : model du cas, method publique, args liste et kwargs objet requis ; aucune cible externe')

        try:
            self.start_http()
            with xmlrpc.client.ServerProxy(self.url + '/xmlrpc/2/common', transport=RpcTransport()) as common:
                uid = common.authenticate('lab_client', 'admin', 'admin', {})
            if not uid:
                raise RuntimeError('authentification synthétique RPC refusée')
            try:
                with xmlrpc.client.ServerProxy(self.url + '/xmlrpc/2/object', transport=RpcTransport(), allow_none=True) as rpc:
                    value = rpc.execute_kw('lab_client', uid, 'admin', request['model'], request['method'],
                                           request['args'], request['kwargs'])
                result = {'transport': 'xmlrpc', 'outcome': 'result', 'result': value}
                code = 0
            except xmlrpc.client.Fault as exc:
                result = {'transport': 'xmlrpc', 'outcome': 'fault',
                          'fault_code': exc.faultCode, 'fault_string': exc.faultString}
                code = 1
            return subprocess.CompletedProcess(['rpc'], code, json.dumps(result, ensure_ascii=False, default=str) + '\n')
        finally:
            self.stop_http()

    def handle(self, args):
        with self.lock:
            started = time.monotonic()
            if not isinstance(args, list) or not args or any(not isinstance(a, str) for a in args):
                raise ValueError('commande absente ou invalide')
            self.sync()
            module = self.case.get('module')
            module_before = source_hashes(self.project / module) if module else None
            if args[0] == 'qa':
                if not self.case['module'] or len(args) < 2 or args[1] != self.case['module']:
                    raise ValueError('seul le module du cas peut être testé')
                options = args[2:]
                pos = 0
                while pos < len(options):
                    if options[pos] == '--tags':
                        pos += 1
                        if pos >= len(options) or not re.fullmatch(r'[A-Za-z0-9_/:.,+ -]+', options[pos]):
                            raise ValueError('tags invalides')
                    elif options[pos] not in ('--quick', '--fresh', '--no-template', '--update', '--keep'):
                        raise ValueError('option QA interdite')
                    pos += 1
                r = execute(['bash', str(self.backend / 'scripts/odoo-test.sh'), *args[1:], '--keep'],
                            cwd=self.backend, env=dict(self.env, ODOO_TEST_DB='lab_qa', ODOO_TEST_DB_EXPLICIT='1'))
            elif args == ['lint', self.case['module']] and self.case['module']:
                r = execute(['bash', str(self.pack / 'scripts/odoo-lint.sh'),
                             str(self.backend / 'addons' / self.case['module'])],
                            cwd=self.backend, env=self.env)
            elif args == ['update'] and self.case['module']:
                r = self.odoo(['-u', self.case['module']])
            elif args[0] == 'shell' and len(args) == 2:
                script = inside(args[1], self.project)
                if script.stat().st_size > 1024 * 1024:
                    raise ValueError('script trop volumineux')
                r = self.odoo([], script.read_text())
            elif args[0] == 'rpc' and len(args) == 2 and self.case['module']:
                script = inside(args[1], self.project)
                if script.stat().st_size > 1024 * 1024:
                    raise ValueError('requête trop volumineuse')
                r = self.rpc(script)
            else:
                raise ValueError('actions autorisées : qa MODULE [options], lint MODULE, update, shell FICHIER, rpc FICHIER.json (module)')
            index = len(self.events)
            log = f'bridge-{index:03d}.log'
            (self.folder / log).write_text(r.stdout)
            event = {'args': args, 'seconds': round(time.monotonic() - started, 2), 'exit_code': r.returncode,
                     'log': log, 'sha256': digest(r.stdout.encode()), 'project_sha256': digest(json.dumps(source_hashes(self.project), sort_keys=True).encode())}
            event['module_sources_before'] = module_before
            event['module_sources_after'] = source_hashes(self.project / module) if module else None
            if args[0] == 'qa':
                logs = sorted((self.backend / 'stack/artifacts').glob('*.log'), key=lambda p: p.stat().st_mtime)
                event['test_result'] = inspect_log(logs[-1].read_text(errors='replace'), self.case['module']) if logs else {'valid': False}
            self.events.append(event)
            atomic_json(self.folder / 'bridge-events.json', self.events)
            return {'exit_code': r.returncode, 'output': r.stdout}

    def oracle(self):
        self.sync()
        # Conserver l'état réel de la copie : aucune reprise/réparation faite par l'oracle.
        script = (ROOT / 'benchmarks/native/oracles' / (self.case['id'] + '_check.py')).read_text()
        result = self.odoo([], script)
        history = self.folder / f'oracle-{len(list(self.folder.glob("oracle-*.log"))):03d}.log'
        history.write_text(result.stdout)
        (self.folder / 'oracle.log').write_text(result.stdout)
        marker = re.findall(r'^LAB_ORACLE (.+)$', result.stdout, re.M)
        return {'exit_code': result.returncode, 'checks': json.loads(marker[-1]) if marker else None,
                'passed': result.returncode == 0 and bool(marker) and all(json.loads(marker[-1]).values()),
                'log_sha256': digest(result.stdout.encode()), 'log': history.name}

    def close(self):
        self.stop_http()
        self.compose(['down', '--volumes', '--remove-orphans'], timeout=60)


class Proxy(socketserver.ThreadingTCPServer):
    daemon_threads = True


class ProxyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        with socket.create_connection(self.server.target, timeout=5) as target:
            sockets = [self.request, target]
            while True:
                readable, _, _ = select.select(sockets, [], [], 30)
                if not readable:
                    return
                for source in readable:
                    data = source.recv(65536)
                    if not data:
                        return
                    (target if source is self.request else self.request).sendall(data)


class Bridge(socketserver.UnixStreamServer):
    allow_reuse_address = True


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            request = json.loads(self.rfile.readline(65536))
            response = self.server.lab.handle(request['args'])
        except Exception as exc:
            response = {'exit_code': 2, 'output': str(exc) + '\n'}
        self.wfile.write(json.dumps(response).encode())


def trial(folder, pack, case, provider, config, timeout):
    try:
        return _trial(folder, pack, case, provider, config, timeout)
    except Exception as exc:
        # Une préparation/fermeture ratée ne doit pas effacer les autres essais.
        folder.mkdir(parents=True, exist_ok=True)
        statefile = folder / 'state.json'
        state = json.loads(statefile.read_text()) if statefile.exists() else {
            'case': case['id'], 'provider': provider, 'config': config, 'turns': []}
        state.update(status='incident', error=str(exc))
        atomic_json(statefile, state)
        print(json.dumps({'trial': folder.name, 'error': str(exc)}), flush=True)
        return state


def _trial(folder, pack, case, provider, config, timeout):
    trial_started = time.monotonic()
    trial_started_at = now()
    folder.mkdir()
    project = folder / 'project'
    copy_project(ROOT / 'benchmarks/native/cases' / case['id'] / 'project', project)
    home = folder / 'home'; home.mkdir()
    bridge = folder / 'bridge'; bridge.mkdir()
    (bridge / 'labctl').write_text(CLIENT); (bridge / 'labctl').chmod(0o755)
    for directory in (home, folder, project, bridge):
        directory.chmod(0o755)
    execute(['git', 'init', '-q', str(project)]).check_returncode()
    execute(['git', '-C', str(project), 'add', '.']).check_returncode()
    execute(['git', '-C', str(project), '-c', 'user.name=Quality Lab', '-c', 'user.email=lab@example.invalid', 'commit', '-qm', 'Dossier synthétique initial']).check_returncode()
    # Older revisions use unittest imports relative to the pack, not /work.
    # Identical transport adaptation for reference and candidate; no pack edits.
    built = execute(sandbox(home, project, pack) + [
        '--chdir', str(HOME_PATH / '.odoo19-agents'),
        'bash', str(HOME_PATH / '.odoo19-agents/build.sh')], env=provider_environment())
    (folder / 'build.log').write_text(built.stdout); built.check_returncode()
    lab = Lab(folder, pack, project, case)
    state = {'case': case['id'], 'provider': provider, 'config': config, 'status': 'setting_up',
             'started_at': trial_started_at, 'turns': []}
    atomic_json(folder / 'state.json', state)
    server = None
    try:
        lab.start()
        state['setup_seconds'] = round(time.monotonic() - trial_started, 3)
        operational = ('# Environnement du laboratoire\nProjet entièrement synthétique ; série 19.0. '
                       'Tu exécutes le workflow natif avec les profils générés sous ~/.codex/skills ou ~/.claude/commands '
                       'et ~/.claude/agents. Lis /odoo-new et les rôles concernés, pilote le vrai graphe. '
                       + delegation_instruction(config)
                       + 'Le dépôt du dispositif et les sources Odoo sont en lecture seule. '
                       'Le projet /work est modifiable. Aucun accès à un projet client ou au socket Docker.\n'
                       '## Transport des outils Odoo (adaptation du banc, identique entre variantes)\n'
                       'Docker est supervisé hors du sandbox. Utilise `/bridge/labctl qa MODULE --quick` '
                       '(options --tags, --fresh, --no-template, --update disponibles) : cette commande appelle '
                       'le vrai odoo-test.sh de ta version sur une base QA séparée. '
                       'Utilise `/bridge/labctl lint MODULE` pour le lint complet avec Ruff disponible dans l’image QA ; '
                       'les écarts de dette antérieure restent à distinguer du diff de la tâche. '
                       'Utilise `/bridge/labctl update` pour mettre à niveau le module sur la copie existante lab_client. '
                       'Utilise `/bridge/labctl shell CHEMIN.py` pour exécuter un fichier de /work dans le vrai shell Odoo '
                       'sur lab_client ; env est disponible, appelle env.cr.commit() pour conserver les écritures voulues. '
                       'Pour un module, `/bridge/labctl rpc CHEMIN.json` traverse le vrai XML-RPC sur lab_client '
                       'avec admin synthétique et un serveur neuf à chaque appel. Le JSON contient exactement '
                       '`model` (modèle du cas), `method` (publique), `args` (liste) et `kwargs` (objet). '
                       'Le résultat JSON conserve la réponse ou le Fault intégral (sortie 1) ; '
                       'vérifie le message attendu et les postconditions, un Fault quelconque ne prouve pas le critère. '
                       'Ce passage RPC ne prouve ni le rendu visuel ni les droits d’un autre utilisateur. '
                       'Les journaux complets de tes appels sont rendus par le pont ; sauvegarde tes preuves dans le projet. '
                       'Ne tente pas d’installer Docker ni de démarrer une autre stack. '
                       'La copie existante est déjà initialisée avec le module et les données synthétiques. '
                       'La base QA démarre vide ; les tests sont à écrire dans le module.\n'
                       'L’environnement autorise toutes les écritures nécessaires sur cette copie synthétique et /work. '
                       'Il ne constitue pas une confirmation de production ou de déploiement. '
                       'Réponds en français et ne masque pas les contrôles incomplets.\n')
        if lab.url:
            operational += ('\nStudio est installé. RPC local : ' + lab.url +
                            ', base lab_client, utilisateur admin, mot de passe admin (identifiants jetables du banc). '
                            'Utilise les vrais outils odoo_pack.py et XML-RPC pour ce cas. '
                            'Les champs initiaux portent des XML-ID studio_customization.lab_seed_*. '
                            'Pas de vue modifiée : aucune capture requise.\n')
        (project / 'LAB.md').write_text(operational)
        # Seules les différences de profils/outils de la révision constituent le traitement.
        server = Bridge(str(bridge / 'control.sock'), Handler); server.lab = lab
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        prompts = [case['request']]
        if case.get('followup'):
            prompts.append(case['followup'])
        for index, request in enumerate(prompts):
            if index:
                (project / 'decisions/2026-09-09.md').write_text(case['final_decision'] + '\n')
            prompt = 'Lis LAB.md puis traite la demande suivante jusqu’au résultat prévu par /odoo-new.\n\n' + request
            if index:
                prompt += '\nContexte neuf volontaire : reprends depuis les fichiers du projet et la release existante, sans réinitialiser les preuves ou l’historique.'
            (folder / f'prompt-{index}.txt').write_text(prompt)
            state['status'] = 'running'; state['active_turn'] = index
            atomic_json(folder / 'state.json', state)
            raw = folder / f'raw-{index}.jsonl'; errors = folder / f'stderr-{index}.log'
            started = time.monotonic()
            with raw.open('w') as out, errors.open('w') as err:
                process = subprocess.Popen(sandbox(home, project, pack, bridge, provider) + native_command(provider, config),
                                           stdin=subprocess.PIPE, stdout=out, stderr=err, text=True,
                                           env=provider_environment(), start_new_session=True)
                try:
                    process.communicate(prompt, timeout=timeout)
                    outcome = 'completed' if process.returncode == 0 else 'error'
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL); process.wait(); outcome = 'timeout'
            parsed = parse_output(raw, provider)
            (folder / f'answer-{index}.md').write_text(parsed['answer'])
            item = {'status': outcome, 'exit_code': process.returncode, 'seconds': round(time.monotonic() - started, 2),
                    'usage': parsed['usage'], 'actual_model': parsed['actual_model'], 'tool_calls': parsed['tool_calls'],
                    'actual_effort': parsed.get('actual_effort'),
                    'provider_completed': parsed['completed_event'], 'error': parsed['provider_error'],
                    'delegation': native_delegation_summary(raw, provider),
                    'answer_sha256': digest(parsed['answer'].encode())}
            state['turns'].append(item)
            snap = folder / f'after-{index}'; copy_project(project, snap)
            atomic_json(folder / f'after-{index}-hashes.json', source_hashes(snap))
            atomic_json(folder / 'state.json', state)
            print(json.dumps({'trial': folder.name, 'turn': index, **item}), flush=True)
            if outcome != 'completed' or not parsed['completed_event'] or parsed['provider_error']:
                break
        state['status'] = 'executed' if len(state['turns']) == len(prompts) and all(
            t['status'] == 'completed' and t['provider_completed'] and not t.get('error')
            for t in state['turns']) else 'incident'
        oracle_started = time.monotonic()
        state['oracle'] = lab.oracle()
        state['oracle_seconds'] = round(time.monotonic() - oracle_started, 3)
        state['oracle_finished_at'] = now()
        state['elapsed_to_oracle_seconds'] = round(time.monotonic() - trial_started, 3)
        state['agent_seconds'] = round(sum(t['seconds'] for t in state['turns']), 3)
        state['bridge_calls'] = len(lab.events)
        state['reception'] = runtime_reception(
            state, lab.events, source_hashes(project / case['module']) if case.get('module') else {})
        state['review'] = None
    except Exception as exc:
        state.update(status='incident', error=str(exc))
        print(json.dumps({'trial': folder.name, 'error': str(exc)}), flush=True)
    finally:
        if server:
            server.shutdown(); server.server_close()
        lab.close()
        atomic_json(folder / 'state.json', state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'status'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', default=['N01', 'N02', 'N03'])
    parser.add_argument('--providers', nargs='+', choices=['codex', 'claude'], default=['codex', 'claude'])
    parser.add_argument('--reference', default='9541bba')
    parser.add_argument('--candidate', default='5868225')
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--workers', type=int, choices=[1, 2], default=2)
    parser.add_argument('--delegate-claude', action='store_true',
                        help='mode expérimental : activer et compter les sous-agents Claude ; aucun gain de vitesse présumé')
    args = parser.parse_args(); output = args.output.resolve()
    if args.action == 'status':
        for path in sorted(output.glob('N*/state.json')):
            data = json.loads(path.read_text())
            print(path.parent.name, data['status'], len(data['turns']), data.get('oracle', {}).get('passed'))
        return
    if output.exists() or not 1 <= args.timeout <= 900:
        raise ValueError('nouveau dossier requis et timeout 1–900 s')
    if args.delegate_claude and 'claude' not in args.providers:
        raise ValueError('--delegate-claude nécessite un essai Claude dans --providers')
    catalog = {}
    for identifier in args.cases:
        if not re.fullmatch(r'N\d{2}', identifier):
            raise ValueError('identifiant invalide')
        catalog[identifier] = json.loads((ROOT / 'benchmarks/native/cases' / identifier / 'case.json').read_text())
    output.mkdir(parents=True)
    packs = {}; revisions = {}
    for label, rev in [('reference', args.reference), ('candidate', args.candidate)]:
        packs[label] = output / 'packs' / label
        revisions[label] = export_revision(rev, packs[label])
    config = {'codex': {'model': 'gpt-6-astra', 'effort': 'high'}, 'claude': {'model': 'opus', 'effort': 'medium'}}
    config['claude']['delegate'] = args.delegate_claude
    atomic_json(output / 'protocol.json', {'schema': 1, 'created_at': now(), 'revisions': revisions,
                'config': config, 'timeout': args.timeout, 'workers': args.workers,
                'cases': {k: digest(json.dumps(v, sort_keys=True).encode()) for k, v in catalog.items()},
                'runner': digest(Path(__file__).read_bytes()), 'corpus': source_hashes(ROOT / 'benchmarks/native'),
                'limitations': [('Délégation Claude activée et enfants comptés dans les événements natifs ; Codex sans délégation.'
                                 if args.delegate_claude else 'Un orchestrateur applique les rôles, délégation non mesurée.'),
                                'Le pont sérialise les commandes Odoo ; compter les enfants ne mesure pas le chevauchement ni un gain de vitesse.',
                                'Transport Odoo via pont supervisé ; accès aux profils et outils natifs.',
                                'Une répétition, comparaison du lot complet, pas effet causal de chaque correction.',
                                'Clôture et navigateur hors de ces tâches ; pas de production.']})
    # Ordre A/B pour Codex, B/A pour Claude ; au plus deux essais isolés simultanés.
    jobs = [(case, provider, label) for case in catalog.values() for provider in args.providers
            for label in (['reference', 'candidate'] if provider == 'codex' else ['candidate', 'reference'])]
    def run(job):
        case, provider, label = job
        return trial(output / f'{case["id"]}-{provider}-{label}', packs[label], case, provider, config[provider], args.timeout)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run, jobs))
    atomic_json(output / 'summary.json', results)


if __name__ == '__main__':
    main()
