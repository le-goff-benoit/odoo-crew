import copy
import unittest

from scheduler import ready


def task(task_id, status='pending', proof=False, deps=(), reads=(), writes=()):
    return dict(id=task_id, status=status, proof_current=proof,
                deps=list(deps), reads=list(reads), writes=list(writes))


class ReadyTests(unittest.TestCase):
    def test_empty_and_lexical_order(self):
        self.assertEqual(ready([], {}), [])
        self.assertEqual(ready([task('z'), task('a'), task('A')], {}),
                         ['A', 'a', 'z'])

    def test_only_pending_is_proposed_regardless_of_own_proof(self):
        tasks = [task('a'), task('b', proof=True),
                 task('c', 'running', True), task('d', 'received', True)]
        self.assertEqual(ready(tasks, {}), ['a', 'b'])

    def test_transitive_dependency_status_and_proof(self):
        for status in ('pending', 'running', 'received'):
            for proof in (False, True):
                with self.subTest(status=status, proof=proof):
                    tasks = [task('leaf', deps=['middle']),
                             task('middle', 'received', True, ['root']),
                             task('root', status, proof)]
                    expected = ['leaf'] if status == 'received' and proof else []
                    if status == 'pending':
                        expected.append('root')
                    self.assertEqual(ready(tasks, {}), expected)

    def test_all_branches_must_be_current(self):
        tasks = [task('root', 'received', True),
                 task('left', 'received', True, ['root']),
                 task('right', 'received', False, ['root']),
                 task('leaf', deps=['left', 'right'])]
        self.assertEqual(ready(tasks, {}), [])
        tasks[2]['proof_current'] = True
        self.assertEqual(ready(tasks, {}), ['leaf'])

    def test_lock_modes_and_resource_overlap(self):
        for mode in (None, 'read', 'write'):
            for reads, writes in ((['r'], []), ([], ['r']), (['r'], ['r']),
                                  (['other'], ['elsewhere'])):
                with self.subTest(mode=mode, reads=reads, writes=writes):
                    locks = {} if mode is None else {'r': mode}
                    blocked = (mode is not None and 'r' in writes
                               or mode == 'write' and 'r' in reads)
                    self.assertEqual(ready([task('a', reads=reads, writes=writes)],
                                           locks), [] if blocked else ['a'])

    def test_candidates_do_not_claim_locks(self):
        tasks = [task('b', writes=['r']), task('a', writes=['r']),
                 task('c', reads=['r'])]
        self.assertEqual(ready(tasks, {}), ['a', 'b', 'c'])

    def test_inputs_are_unchanged_on_success(self):
        tasks = [task('b', deps=['a'], reads=['r']),
                 task('a', 'received', True)]
        locks = {'r': 'read'}
        before = copy.deepcopy((tasks, locks))
        self.assertEqual(ready(tasks, locks), ['b'])
        self.assertEqual((tasks, locks), before)

    def test_invalid_inputs_raise_without_mutation(self):
        cases = [
            ([task('x'), task('x', 'received', True)], {}),
            ([task('x', 'received', True, ['missing'])], {}),
            ([task('x', 'unknown')], {}),
            ([], {'unused': 'unknown'}),
            ([task('x', 'received', True, ['x'])], {}),
            ([task('candidate'), task('x', 'received', True, ['y']),
              task('y', 'running', True, ['x'])], {}),
        ]
        for tasks, locks in cases:
            with self.subTest(tasks=tasks, locks=locks):
                before = copy.deepcopy((tasks, locks))
                with self.assertRaises(ValueError):
                    ready(tasks, locks)
                self.assertEqual((tasks, locks), before)

    def test_repeated_dependency(self):
        self.assertEqual(ready([task('a', 'received', True),
                                task('b', deps=['a', 'a'])], {}), ['b'])

    def test_long_dependency_chain(self):
        tasks = [task(str(i), 'received', True, [str(i - 1)] if i else [])
                 for i in range(2000)]
        tasks.append(task('leaf', deps=['1999']))
        self.assertEqual(ready(list(reversed(tasks)), {}), ['leaf'])


if __name__ == '__main__':
    unittest.main()
