#!/usr/bin/env python3
"""Estimer et mesurer l'exécution des agents par tâche d'une release, sans barème client."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import fcntl
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import uuid

TOKEN_KEYS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens', 'output_tokens', 'total_tokens')
REPORT_FILES = ('estimation.md', 'bilan-effort.md', 'bilan-effort.json', 'bilan-effort.csv')


def now():
    return datetime.now(timezone.utc).isoformat()


def instant(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('horodatage avec fuseau obligatoire')
    return result.timestamp()


def number(value):
    if isinstance(value, bool):
        raise ValueError('nombre positif ou nul requis')
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('nombre invalide') from exc
    if not result.is_finite() or result < 0:
        raise ValueError('nombre fini positif ou nul requis')
    return result


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def location(release):
    release = Path(release).resolve()
    if release.parent.name != 'changelog' or not (release / 'README.md').is_file():
        raise ValueError('release changelog/<dossier> avec README.md requise')
    return release, release.parent.parent


@contextmanager
def locked(release):
    release, project = location(release)
    folder = project / '.odoo-agents'
    folder.mkdir(exist_ok=True)
    with (folder / 'effort.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield release, project


def state(release):
    value = read(Path(release) / 'effort.json')
    if value.get('schema') != 1:
        raise ValueError('format effort inconnu')
    return value


def save(release, value):
    value['updated_at'] = now()
    write(Path(release) / 'effort.json', value)


def contracts(release):
    path = Path(release) / 'plan.json'
    if not path.exists():
        saved = Path(release) / 'effort.json'
        tasks = read(saved)['tasks'] if saved.exists() else {}
        return {task: {'title': title, 'sha256': manual_contract(release, task, title)} for task, title in tasks.items()}
    from odoo_plan import contract_hash
    project = Path(release).parent.parent
    return {t['id']: {'title': t['title'], 'sha256': contract_hash(t, project)} for t in read(path)['tasks']}


def manual_contract(release, task, title):
    request = Path(release) / 'demande.md'
    return digest({'task': task, 'title': title,
                   'request_sha256': hashlib.sha256(request.read_bytes()).hexdigest() if request.exists() else None})


def init(release):
    with locked(release) as (release, _):
        if (release / 'effort.json').exists():
            return state(release)
        stamp = now()
        value = {'schema': 1, 'release': release.name, 'created_at': stamp, 'updated_at': stamp,
                 'tasks': {k: v['title'] for k, v in contracts(release).items()},
                 'estimates': [], 'entries': [], 'rate_cards': []}
        save(release, value)
        return value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', value):
        raise ValueError('identifiant stable alphanumérique requis')
    return value


def add_task(release, task, title):
    """Déclarer un travail passé sans fabriquer une prévision rétroactive."""
    identifier(task)
    if not isinstance(title, str) or not title.strip():
        raise ValueError('titre du lot de travail requis')
    with locked(release) as (release, _):
        data = state(release)
        known = contracts(release)
        has_plan = (release / 'plan.json').exists()
        if has_plan and task not in known and task != 'RELEASE':
            raise ValueError('tâche absente du plan')
        if has_plan:
            title = known.get(task, {}).get('title') or title
        if task in data['tasks'] and data['tasks'][task] != title:
            raise ValueError('tâche déjà déclarée avec un autre titre')
        data['tasks'][task] = title
        save(release, data)
        return data


def estimate(release, definition, reason=None):
    with locked(release) as (release, _):
        data = state(release)
        if data['estimates'] and not (reason and reason.strip()):
            raise ValueError('une révision exige --reason ; estimation initiale conservée')
        rows, seen = [], set()
        known = contracts(release)
        has_plan = (release / 'plan.json').exists()
        for line in definition.get('lines', []):
            task, agent = identifier(line['task']), identifier(line['agent'])
            if has_plan and task not in known and task != 'RELEASE':
                raise ValueError('tâche absente du plan ; RELEASE réservé aux travaux communs')
            if (task, agent) in seen:
                raise ValueError('une seule ligne par tâche et agent dans une révision')
            seen.add((task, agent))
            low, middle, high = [number(line[k]) for k in ('optimistic_minutes', 'likely_minutes', 'pessimistic_minutes')]
            if not low <= middle <= high:
                raise ValueError('fourchette attendue : optimiste <= probable <= pessimiste')
            assumptions = line.get('assumptions')
            if not isinstance(assumptions, list) or not assumptions or any(not isinstance(a, str) or not a.strip() for a in assumptions):
                raise ValueError('hypothèses explicites requises')
            if not isinstance(line.get('basis'), str) or not line['basis'].strip() or line.get('confidence') not in ('low', 'medium', 'high'):
                raise ValueError('base de jugement et confiance low/medium/high requises')
            title = known.get(task, {}).get('title') or line.get('title') or data['tasks'].get(task)
            if not isinstance(title, str) or not title.strip():
                raise ValueError('titre du lot de travail requis')
            data['tasks'][task] = title
            rows.append({'task': task, 'title': title, 'agent': agent,
                         'optimistic_minutes': float(low), 'likely_minutes': float(middle),
                         'pessimistic_minutes': float(high), 'expected_minutes': float((low + 4 * middle + high) / 6),
                         'assumptions': assumptions, 'basis': line['basis'], 'confidence': line['confidence'],
                         'contract_sha256': known.get(task, {}).get('sha256') if has_plan else manual_contract(release, task, title)})
        if not rows:
            raise ValueError('au moins une ligne d’estimation requise')
        if data['estimates']:
            merged = {(x['task'], x['agent']): x for x in data['estimates'][-1]['lines']}
            merged.update({(x['task'], x['agent']): x for x in rows})
            rows = list(merged.values())
        data['estimates'].append({'revision': len(data['estimates']) + 1, 'at': now(),
                                  'reason': reason or 'estimation initiale', 'lines': rows})
        save(release, data)
        return data['estimates'][-1]


def normalized_usage(path, provider, since=None, until=None):
    from odoo_usage import read_usage
    usage = read_usage(Path(path), provider, since=since, until=until)
    if not usage.get('thread_id'):
        raise ValueError('identité de session introuvable ; attribution refusée')
    for key in ('started_at', 'ended_at'):
        if usage.get(key):
            instant(usage[key])
    return usage


def interval(entry):
    start = entry.get('since') or entry.get('started_at')
    end = entry.get('until') or entry.get('ended_at')
    if entry.get('status') in ('running', 'incomplete') and not entry.get('until'):
        end = None
    return (instant(start) if start else float('-inf'), instant(end) if end else float('inf'))


def check_allocation(release, data, candidate, replacing=None):
    """One project lock serializes overlap checks across its releases."""
    project = Path(release).parent.parent
    for folder in (project / 'changelog').iterdir():
        path = folder / 'effort.json'
        if not path.exists():
            continue
        other = data if folder.resolve() == Path(release).resolve() else read(path)
        for old in other['entries']:
            if folder.resolve() == Path(release).resolve() and old['id'] == replacing:
                continue
            if old['provider'] != candidate['provider']:
                continue
            if old['thread_id'] == candidate['thread_id']:
                a, b = interval(old), interval(candidate)
                if max(a[0], b[0]) < min(a[1], b[1]) or a == b:
                    raise ValueError('session/fenêtre déjà attribuée : ' + old['task'] + ' / ' + old['agent'])
            elif set(old.get('identities', [])) & set(candidate.get('identities', [])):
                raise ValueError('réponses déjà comptées dans une autre attribution')


def ensure_task(data, task, agent):
    identifier(task); identifier(agent)
    if task not in data['tasks']:
        raise ValueError('lot inconnu : initialiser le plan, utiliser add-task ou ajouter sa ligne d’estimation')


def forecast_revision(data, task, agent, at):
    eligible = [r['revision'] for r in data['estimates'] if instant(r['at']) <= instant(at)
                and any((x['task'], x['agent']) == (task, agent) for x in r['lines'])]
    return eligible[-1] if eligible else None


def start(release, task, agent, provider, source):
    usage = normalized_usage(source, provider)
    with locked(release) as (release, _):
        data = state(release); ensure_task(data, task, agent)
        entry = {'id': uuid.uuid4().hex[:12], 'task': task, 'agent': agent, 'provider': provider,
                 'thread_id': usage['thread_id'], 'model': usage.get('model'), 'started_at': now(),
                 'ended_at': None, 'status': 'running', 'basis': 'timer', 'baseline': usage,
                 'tokens': None, 'seconds': None, 'identities': [], 'warnings': []}
        entry['estimate_revision'] = forecast_revision(data, task, agent, entry['started_at'])
        check_allocation(release, data, entry)
        data['entries'].append(entry); save(release, data)
        return entry


def counter_delta(before, after):
    if before is None or after is None or any(before.get(k) is None or after.get(k) is None for k in TOKEN_KEYS):
        return None
    delta = {k: after[k] - before[k] for k in TOKEN_KEYS}
    if any(v < 0 for v in delta.values()):
        raise ValueError('compteur cumulatif régressif')
    return delta


def stop(release, entry_id, source):
    with locked(release) as (release, _):
        data = state(release)
        entry = next((e for e in data['entries'] if e['id'] == entry_id), None)
        if not entry or entry['status'] != 'running' or entry['basis'] != 'timer':
            raise ValueError('chronomètre actif inconnu')
        usage = normalized_usage(source, entry['provider'])
        if usage['thread_id'] != entry['thread_id']:
            raise ValueError('la session de fin diffère de celle du départ')
        entry['ended_at'] = now(); entry['status'] = 'complete'
        entry['seconds'] = instant(entry['ended_at']) - instant(entry['started_at'])
        number(entry['seconds'])
        entry['tokens'] = counter_delta(entry['baseline'].get('tokens'), usage.get('tokens'))
        baseline_model = entry['baseline'].get('model')
        entry['model'] = usage.get('model') if baseline_model in (None, usage.get('model')) and 'mixed_models' not in entry['baseline'].get('warnings', []) else None
        entry['source_sha256'] = usage['source_sha256']
        entry['warnings'] = list(usage.get('warnings', [])) + ['Chronomètre de périmètre : outils et attentes internes inclus ; bornes des jetons aux réponses déjà enregistrées.']
        if entry['tokens'] is None:
            entry['warnings'].append('Jetons non mesurés : compteur initial ou final absent/incomplet.')
        entry['provider_cost'] = None
        before_cost, after_cost = entry['baseline'].get('provider_cost'), usage.get('provider_cost')
        if before_cost and after_cost and (before_cost['currency'], before_cost.get('basis')) == (after_cost['currency'], after_cost.get('basis')):
            difference = number(after_cost['amount']) - number(before_cost['amount'])
            entry['provider_cost'] = {**after_cost, 'amount': float(number(difference))}
        entry['identities'] = usage.get('identities', [])
        entry['observed_at'] = now()
        check_allocation(release, data, entry, entry['id'])
        save(release, data)
        return entry


def import_usage(release, task, agent, provider, source, since=None, until=None):
    if bool(since) != bool(until):
        raise ValueError('une fenêtre exige --since et --until')
    if since and instant(since) >= instant(until):
        raise ValueError('fenêtre non positive')
    if since:
        since, until = [datetime.fromtimestamp(instant(x), timezone.utc).isoformat() for x in (since, until)]
    usage = normalized_usage(source, provider, since, until)
    with locked(release) as (release, _):
        data = state(release); ensure_task(data, task, agent)
        same = next((e for e in data['entries'] if e['basis'] == 'native'
                     and (e['provider'], e['thread_id'], e.get('since'), e.get('until')) == (provider, usage['thread_id'], since, until)), None)
        if same and (same['task'], same['agent']) != (task, agent):
            raise ValueError('session déjà attribuée à un autre lot/agent')
        if same and same.get('source_sha256') == usage['source_sha256']:
            return same
        entry = {**usage, 'id': same['id'] if same else uuid.uuid4().hex[:12], 'task': task, 'agent': agent,
                 'provider': provider, 'basis': 'native', 'since': since, 'until': until,
                 'status': 'complete' if usage.get('complete') else 'incomplete',
                 'seconds': usage.get('active_seconds'), 'observed_at': now()}
        start_at = since or usage.get('started_at')
        entry['estimate_revision'] = forecast_revision(data, task, agent, start_at) if start_at else None
        if entry['seconds'] is None:
            entry.setdefault('warnings', []).append('Temps mobilisé non mesuré ; enveloppe disponible séparément, pas substituée au temps actif.')
        check_allocation(release, data, entry, same['id'] if same else None)
        if same:
            if same.get('tokens') is not None and entry.get('tokens') is not None:
                counter_delta(same['tokens'], entry['tokens'])
            entry['history'] = same.get('history', []) + [{k: v for k, v in same.items() if k != 'history'}]
            data['entries'][data['entries'].index(same)] = entry
        else:
            data['entries'].append(entry)
        save(release, data)
        return entry


def rates(release, definition):
    cards = deepcopy(definition.get('cards', []))
    if not cards:
        raise ValueError('cards non vide requis')
    for card in cards:
        for key in ('provider', 'model', 'source', 'scope'):
            if not isinstance(card.get(key), str) or not card[key].strip():
                raise ValueError('tarif : ' + key + ' requis')
        if card.get('basis') not in ('api_equivalent', 'contract') or not re.fullmatch('[A-Z]{3}', card.get('currency', '')):
            raise ValueError('tarif : basis api_equivalent/contract et devise ISO requises')
        card['effective_at'] = datetime.fromtimestamp(instant(card['effective_at']), timezone.utc).isoformat()
        for key in ('input_per_million', 'cached_input_per_million', 'cache_write_input_per_million', 'output_per_million'):
            card[key] = str(number(card[key]))
    with locked(release) as (release, _):
        data = state(release)
        for card in cards:
            key = (card['provider'], card['model'], card['effective_at'])
            old = next((c for c in data['rate_cards'] if (c['provider'], c['model'], c['effective_at']) == key), None)
            if old and old != card:
                raise ValueError('tarif historique immuable : choisir une nouvelle date d’effet')
            if not old:
                data['rate_cards'].append(card)
        save(release, data)
        return cards


def cost(entry, cards):
    native = entry.get('provider_cost')
    if native is not None:
        amount = number(native['amount'])
        currency = native['currency']
        if not re.fullmatch('[A-Z]{3}', currency):
            raise ValueError('devise de coût natif invalide')
        return {'amount': float(amount), 'currency': currency, 'kind': 'declared', 'basis': native.get('basis', 'native')}
    tokens = entry.get('tokens')
    if not tokens or any(tokens.get(k) is None for k in TOKEN_KEYS) or not entry.get('model') or not entry.get('started_at'):
        return None
    start_at = instant(entry.get('since') or entry['started_at'])
    end_at = instant(entry.get('until') or entry.get('ended_at') or entry['started_at'])
    candidates = [c for c in cards if c['provider'] == entry['provider'] and c['model'] == entry['model']]
    if any(start_at < instant(c['effective_at']) < end_at for c in candidates):
        return None  # Aggregate usage cannot be split between tariff periods.
    eligible = [c for c in candidates if instant(c['effective_at']) <= start_at]
    if not eligible:
        return None
    card = max(eligible, key=lambda c: instant(c['effective_at']))
    ordinary = tokens['input_tokens'] - tokens['cached_input_tokens'] - tokens['cache_write_input_tokens']
    if ordinary < 0:
        raise ValueError('cache supérieur aux entrées normalisées')
    charge = sum(number(n) * number(card[k]) for n, k in [
        (ordinary, 'input_per_million'), (tokens['cached_input_tokens'], 'cached_input_per_million'),
        (tokens['cache_write_input_tokens'], 'cache_write_input_per_million'), (tokens['output_tokens'], 'output_per_million')]) / Decimal(1000000)
    return {'amount': float(charge), 'currency': card['currency'], 'kind': 'calculated',
            'basis': card['basis'], 'rate_card': card, 'note': 'Valorisation au tarif déclaré ; ne constitue pas une facture.'}


def union_seconds(intervals):
    result = 0.0; end = None
    for a, b in sorted(intervals):
        if end is None or a >= end:
            result += b - a
        elif b > end:
            result += b - end
        end = b if end is None else max(end, b)
    return result


def report_data(release, data):
    current = contracts(release)
    original = data['estimates'][0] if data['estimates'] else None
    revised = data['estimates'][-1] if data['estimates'] else None
    initial = {(x['task'], x['agent']): x for x in original['lines']} if original else {}
    latest = {(x['task'], x['agent']): x for x in revised['lines']} if revised else {}
    pairs = set(initial) | set(latest) | {(x['task'], x['agent']) for x in data['entries']}
    rows = []
    for task, agent in sorted(pairs):
        entries = [x for x in data['entries'] if (x['task'], x['agent']) == (task, agent)]
        old, new = initial.get((task, agent)), latest.get((task, agent))
        measured = bool(entries) and all(x.get('seconds') is not None and x['status'] == 'complete' for x in entries)
        actual = sum(x['seconds'] for x in entries) / 60 if measured else None
        subtotal = sum(x['seconds'] for x in entries if x.get('seconds') is not None) / 60
        token_complete = bool(entries) and all(x.get('tokens') is not None and x['status'] == 'complete' for x in entries)
        tokens = {k: sum(x['tokens'][k] for x in entries) for k in TOKEN_KEYS} if token_complete else None
        known_tokens = sum((x.get('tokens') or {}).get('total_tokens', 0) or 0 for x in entries)
        warnings = [w for x in entries for w in x.get('warnings', [])]
        changed = any(line and line.get('contract_sha256') and current.get(task, {}).get('sha256') != line['contract_sha256'] for line in (old, new))
        retrospective = bool(old and any(x.get('started_at') and instant(x.get('since') or x['started_at']) < instant(original['at']) for x in entries))
        if changed:
            warnings.append('Périmètre changé depuis l’estimation ; comparaison non homogène.')
        if retrospective:
            warnings.append('Estimation initiale postérieure au démarrage observé : reconstitution, pas prévision.')
        if not entries:
            warnings.append('Aucune mesure importée pour cette ligne.')
        costs = [{'entry': x['id'], 'cost': cost(x, data['rate_cards'])} for x in entries]
        variance = actual - old['expected_minutes'] if actual is not None and old and not retrospective and not changed else None
        rows.append({'task': task, 'title': data['tasks'][task], 'agent': agent, 'initial': old, 'revised': new,
                     'actual_minutes': actual, 'known_minutes': subtotal, 'time_complete': measured,
                     'tokens': tokens, 'known_tokens': known_tokens, 'token_complete': token_complete,
                     'delta_minutes': variance, 'delta_percent': 100 * variance / old['expected_minutes'] if variance is not None and old['expected_minutes'] else None,
                     'retrospective': retrospective, 'scope_changed': changed, 'entries': [e['id'] for e in entries],
                     'costs': costs, 'warnings': list(dict.fromkeys(warnings))})
    intervals = [interval(e) for e in data['entries'] if e.get('started_at') and e.get('ended_at') and e['status'] == 'complete']
    intervals = [(a, b) for a, b in intervals if b >= a]
    cost_totals = {}
    for row in rows:
        for item in row['costs']:
            c = item['cost']
            if c:
                key = c['kind'] + ':' + c['basis'] + ':' + c['currency']
                cost_totals[key] = cost_totals.get(key, Decimal(0)) + number(c['amount'])
    missing_tasks = sorted(set(data['tasks']) - {r['task'] for r in rows})
    if current:
        missing_tasks = sorted(set(missing_tasks) | (set(current) - {r['task'] for r in rows}))
    return {'schema': 1, 'release': data['release'], 'generated_at': now(), 'state_sha256': digest(data),
            'contracts_sha256': digest(current), 'initial_revision': original['revision'] if original else None,
            'latest_revision': revised['revision'] if revised else None, 'rows': rows, 'missing_tasks': missing_tasks,
            'totals': {'planned_initial_minutes': sum(x['expected_minutes'] for x in initial.values()) if initial else None,
                       'planned_revised_minutes': sum(x['expected_minutes'] for x in latest.values()) if latest else None,
                       'actual_minutes': sum(r['actual_minutes'] for r in rows) if rows and not missing_tasks and all(r['time_complete'] for r in rows) else None,
                       'known_minutes': sum(r['known_minutes'] for r in rows),
                       'tokens': sum(r['tokens']['total_tokens'] for r in rows) if rows and not missing_tasks and all(r['token_complete'] for r in rows) else None,
                       'known_tokens': sum(r['known_tokens'] for r in rows),
                       'envelope_minutes': (max(b for _, b in intervals) - min(a for a, _ in intervals)) / 60 if intervals else None,
                       'covered_interval_minutes': union_seconds(intervals) / 60 if intervals else None,
                       'known_costs': {k: float(v) for k, v in cost_totals.items()},
                       'unpriced_entries': sum(item['cost'] is None for row in rows for item in row['costs'])},
            'limitations': ['Estimation de minutes d’exécution des agents, aucun temps humain ni barème client.',
                           'Temps des outils et attentes internes inclus ; les attentes humaines ne sont pas isolées automatiquement.',
                           'Somme des temps par agent distincte de l’enveloppe calendaire ; les intervalles peuvent se chevaucher.',
                           'Compteurs absents et lignes non mesurées restent inconnus. Les sous-totaux connus ne sont pas des totaux complets.',
                           'L’attribution tâche/agent est déclarée explicitement ; le contenu métier des conversations n’est pas inspecté.']}


def fmt(value, digits=2):
    return 'non mesuré' if value is None else f'{value:.{digits}f}'


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def render(report):
    estimate_lines = ['# Estimation du temps des agents', '', 'Minutes d’exécution, outils inclus. Aucun barème commercial appliqué.',
                      'Valeur centrale = (optimiste + 4 × probable + pessimiste) / 6 ; fourchette de jugement, pas intervalle statistique.', '',
                      '| Lot de travail | Agent | Optimiste | Probable | Pessimiste | Central | Confiance |', '|---|---|---:|---:|---:|---:|---|']
    lines = ['# Bilan prévu / réalisé', '', 'Le temps cumulé des agents ne représente ni des heures humaines ni la durée totale de la release.', '',
             '| Lot de travail | Agent | Prévu initial (min) | Prévu révisé (min) | Réel (min) | Écart (min) | Jetons |',
             '|---|---|---:|---:|---:|---:|---:|']
    stream = io.StringIO(); writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['lot', 'libelle', 'agent', 'prevu_initial_minutes', 'prevu_revise_minutes', 'reel_minutes', 'ecart_minutes', 'jetons', 'temps_complet', 'jetons_complets', 'couts_ia', 'reserves'])
    def safe(value):
        text = '' if value is None else str(value)
        return "'" + text if text.startswith(('=', '+', '-', '@', '\t', '\r')) else text
    for row in report['rows']:
        a, b = row['initial'], row['revised']
        old, new = a['expected_minutes'] if a else None, b['expected_minutes'] if b else None
        token = row['tokens']['total_tokens'] if row['tokens'] else None
        label = row['task'] + ' — ' + row['title']
        lines.append('| ' + ' | '.join(map(cell, [label, row['agent'], fmt(old), fmt(new), fmt(row['actual_minutes']), fmt(row['delta_minutes']), fmt(token, 0)])) + ' |')
        if b:
            confidence = {'low': 'faible', 'medium': 'moyenne', 'high': 'élevée'}[b['confidence']]
            estimate_lines.append('| ' + ' | '.join(map(cell, [label, row['agent'], fmt(b['optimistic_minutes']), fmt(b['likely_minutes']), fmt(b['pessimistic_minutes']), fmt(new), confidence])) + ' |')
        writer.writerow([safe(x) for x in [row['task'], row['title'], row['agent'], old, new, row['actual_minutes'], row['delta_minutes'], token,
                                          row['time_complete'], row['token_complete'], json.dumps(row['costs'], ensure_ascii=False), '; '.join(row['warnings'])]])
    for row in report['rows']:
        b = row['revised']
        if b:
            estimate_lines += ['', '## ' + row['task'] + ' / ' + row['agent'], '', 'Base : ' + b['basis'], '', *['- ' + x for x in b['assumptions']]]
    totals = report['totals']
    lines += ['', 'Temps cumulé mesuré : **' + fmt(totals['actual_minutes']) + ' min** ; sous-total connu : ' + fmt(totals['known_minutes']) + ' min.',
              'Jetons totaux : **' + fmt(totals['tokens'], 0) + '** ; sous-total connu : ' + fmt(totals['known_tokens'], 0) + '.',
              'Enveloppe des périodes enregistrées : ' + fmt(totals['envelope_minutes']) + ' min ; union de ces périodes : ' + fmt(totals['covered_interval_minutes']) + ' min.',
              '', '## Coûts IA', '', 'Coûts déclarés et valorisations calculées sont séparés ; aucun prix d’offre n’est calculé.', '',
              '| Lot / agent | Mesure | Nature | Montant | Devise |', '|---|---|---|---:|---|']
    for row in report['rows']:
        for item in row['costs']:
            c = item['cost']
            lines.append('| ' + ' | '.join(map(cell, [row['task'] + ' / ' + row['agent'], item['entry'], (c['kind'] + ' / ' + c['basis']) if c else 'non chiffré', fmt(c['amount'], 6) if c else 'non mesuré', c['currency'] if c else '—'])) + ' |')
    lines += ['', 'Sous-totaux chiffrés : ' + (json.dumps(totals['known_costs'], ensure_ascii=False) if totals['known_costs'] else 'aucun'),
              'Mesures sans coût disponible : ' + str(totals['unpriced_entries']) + '.', '', '## Réserves', '',
              *['- ' + x for x in report['limitations']], *['- Lot sans ligne : ' + t for t in report['missing_tasks']]]
    for row in report['rows']:
        lines += ['- ' + row['task'] + ' / ' + row['agent'] + ' : ' + w for w in row['warnings']]
    return {'estimation.md': '\n'.join(estimate_lines) + '\n', 'bilan-effort.md': '\n'.join(lines) + '\n',
            'bilan-effort.csv': stream.getvalue()}


def report(release):
    with locked(release) as (release, _):
        data = state(release); result = report_data(release, data)
        for name, text in render(result).items():
            (release / name).write_text(text)
        write(release / 'bilan-effort.json', result)
        return result


def check_report(release):
    release = Path(release)
    data = state(release); actual = read(release / 'bilan-effort.json')
    if actual.get('state_sha256') != digest(data) or actual.get('contracts_sha256') != digest(contracts(release)):
        raise ValueError('bilan d’effort périmé : relancer report')
    expected = report_data(release, data)
    expected['generated_at'] = actual.get('generated_at')
    if expected != actual:
        raise ValueError('bilan d’effort incohérent avec les mesures')
    for name, text in render(actual).items():
        if (release / name).read_text() != text:
            raise ValueError('export d’effort modifié : ' + name)
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ('init', 'add-task', 'estimate', 'start', 'stop', 'import-usage', 'rates', 'report', 'check'):
        p = sub.add_parser(action); p.add_argument('release', type=Path)
        if action == 'add-task':
            p.add_argument('--task', required=True); p.add_argument('--title', required=True)
        if action in ('estimate', 'rates'):
            p.add_argument('--file', type=Path, required=True)
        if action == 'estimate':
            p.add_argument('--reason')
        if action in ('start', 'import-usage'):
            p.add_argument('--task', required=True); p.add_argument('--agent', required=True)
            p.add_argument('--provider', choices=('codex', 'claude'), required=True)
        if action in ('start', 'stop', 'import-usage'):
            p.add_argument('--source', type=Path, required=True)
        if action == 'stop':
            p.add_argument('--entry', required=True)
        if action == 'import-usage':
            p.add_argument('--since'); p.add_argument('--until')
    args = parser.parse_args()
    try:
        if args.action == 'init':
            result = init(args.release)
        elif args.action == 'add-task':
            result = add_task(args.release, args.task, args.title)
        elif args.action == 'estimate':
            result = estimate(args.release, read(args.file), args.reason)
        elif args.action == 'rates':
            result = rates(args.release, read(args.file))
        elif args.action == 'start':
            result = start(args.release, args.task, args.agent, args.provider, args.source)
        elif args.action == 'stop':
            result = stop(args.release, args.entry, args.source)
        elif args.action == 'import-usage':
            result = import_usage(args.release, args.task, args.agent, args.provider, args.source, args.since, args.until)
        elif args.action == 'report':
            result = report(args.release)
        else:
            result = check_report(args.release)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('Suivi des agents : ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
