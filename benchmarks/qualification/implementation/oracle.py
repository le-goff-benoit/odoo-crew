"""Held outside candidate mounts. Independent behavioral and mutation oracle."""
import copy
import importlib.util
import math
from pathlib import Path
import sys


def load(project, case):
    name = 'scheduler' if case == 'I01' else 'quotas'
    spec = importlib.util.spec_from_file_location('candidate', Path(project) / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ready if case == 'I01' else module.snapshot


def judge(function, case):
    if case == 'I01':
        def task(name, status='pending', deps=(), reads=(), writes=(), current=True):
            return dict(id=name, status=status, proof_current=current, deps=list(deps), reads=list(reads), writes=list(writes))
        tasks = [task('Z'), task('A', writes=['code']), task('B', reads=['code'])]
        before = copy.deepcopy(tasks)
        assert function(tasks, {}) == ['A', 'B', 'Z']
        assert function(tasks, {'code': 'read'}) == ['B', 'Z']
        assert function(tasks, {'code': 'write'}) == ['Z']
        assert tasks == before
        assert function([task('A', 'received', current=False), task('B', 'received', ['A']), task('C', deps=['B'])], {}) == []
        assert function([task('A', 'received'), task('B', 'received', ['A']), task('C', deps=['B'])], {}) == ['C']
        assert function([task('A', 'running'), task('B', deps=['A'])], {}) == []
        invalid = [([task('A'), task('A')], {}), ([task('A', deps=['missing'])], {}),
                   ([task('A', 'received', ['B']), task('B', 'received', ['A']), task('Z')], {}),
                   ([task('A', 'done')], {}), ([task('A')], {'code': 'unknown'})]
        for tasks, locks in invalid:
            try:
                function(tasks, locks)
            except ValueError:
                pass
            else:
                raise AssertionError('invalid graph/lock accepted')
    else:
        def event(**kw):
            return dict(dict(provider='openai', window='5h', observed_at=700, used_percent=40, reset_at=1500), **kw)
        missing = {'openai': {'5h': None, 'week': None}, 'anthropic': {'5h': None, 'week': None}}
        assert function([], 1000) == missing
        data = [event(), event(provider='anthropic', used_percent=80), event(window='week', used_percent=0)]
        before = copy.deepcopy(data)
        result = function(data, 1000)
        assert data == before
        assert result['openai']['5h'] == dict(used_percent=40, reset_at=1500, observed_at=700, stale=False)
        assert result['anthropic']['5h']['used_percent'] == 80
        assert result['openai']['week']['used_percent'] == 0
        assert function([event()], 1001)['openai']['5h']['stale'] is True
        assert function([event(), event(used_percent=44)], 1000)['openai']['5h']['used_percent'] == 44
        assert function([event(observed_at=800), event(observed_at=700, used_percent=99)], 1000)['openai']['5h']['used_percent'] == 40
        for change in [dict(observed_at=None), dict(observed_at=True), dict(observed_at=1001), dict(observed_at=-1),
                       dict(observed_at=float('nan')), dict(observed_at=float('inf')), dict(used_percent=True),
                       dict(used_percent=-1), dict(used_percent=101), dict(used_percent='20'), dict(used_percent=float('nan')),
                       dict(reset_at=True), dict(reset_at=-1), dict(reset_at=699), dict(reset_at=float('inf')),
                       dict(provider='other'), dict(window='month')]:
            assert function([event(), event(**change)], 1000)['openai']['5h']['used_percent'] == 40, change
        assert function([event(reset_at=None, used_percent=100)], 1000)['openai']['5h']['reset_at'] is None
    return True


if __name__ == '__main__':
    judge(load(sys.argv[1], sys.argv[2]), sys.argv[2])
    print('independent oracle passed')
