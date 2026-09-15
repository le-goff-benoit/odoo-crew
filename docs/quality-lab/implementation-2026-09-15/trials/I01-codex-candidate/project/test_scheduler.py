import unittest

from scheduler import ready


def task(task_id, status='pending', proof_current=False, deps=None,
         reads=None, writes=None):
    return {
        'id': task_id,
        'status': status,
        'proof_current': proof_current,
        'deps': [] if deps is None else deps,
        'reads': [] if reads is None else reads,
        'writes': [] if writes is None else writes,
    }


class ReadyTests(unittest.TestCase):
    def test_dependencies_must_be_current_transitively(self):
        tasks = [
            task('old', 'received', False),
            task('middle', 'received', True, ['old']),
            task('blocked', deps=['middle']),
            task('open', 'received', True),
            task('ready', deps=['open']),
        ]
        self.assertEqual(ready(tasks, {}), ['ready'])

    def test_only_received_dependencies_release_a_task(self):
        tasks = [
            task('running', 'running', True),
            task('pending-dependency', deps=[]),
            task('a', deps=['running']),
            task('b', deps=['pending-dependency']),
        ]
        self.assertEqual(ready(tasks, {}), ['pending-dependency'])

    def test_locks_and_candidate_tasks_do_not_conflict_each_other(self):
        tasks = [
            task('writer', writes=['alpha']),
            task('reader', reads=['alpha']),
            task('write-locked', writes=['beta']),
            task('read-write-locked', reads=['gamma']),
            task('read-read-locked', reads=['delta']),
        ]
        locks = {'beta': 'read', 'gamma': 'write', 'delta': 'read'}
        self.assertEqual(ready(tasks, locks), ['read-read-locked', 'reader', 'writer'])

    def test_results_are_lexically_sorted(self):
        self.assertEqual(ready([task('z'), task('A'), task('a')], {}), ['A', 'a', 'z'])

    def test_rejects_duplicate_missing_and_invalid_status(self):
        with self.assertRaises(ValueError):
            ready([task('same'), task('same')], {})
        with self.assertRaises(ValueError):
            ready([task('one', deps=['missing'])], {})
        with self.assertRaises(ValueError):
            ready([task('one', status='done')], {})

    def test_rejects_invalid_lock_mode(self):
        with self.assertRaises(ValueError):
            ready([task('one')], {'resource': 'exclusive'})

    def test_rejects_cycles_even_without_pending_tasks(self):
        tasks = [
            task('one', 'received', True, ['two']),
            task('two', 'received', True, ['one']),
        ]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_does_not_mutate_inputs(self):
        tasks = [task('done', 'received', True), task('next', deps=['done'])]
        locks = {'locked': 'read'}
        original_tasks = [dict(item, deps=list(item['deps']), reads=list(item['reads']),
                               writes=list(item['writes'])) for item in tasks]
        original_locks = dict(locks)
        ready(tasks, locks)
        self.assertEqual(tasks, original_tasks)
        self.assertEqual(locks, original_locks)
