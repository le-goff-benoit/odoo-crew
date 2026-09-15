import unittest
from scheduler import ready


def task(id, status='pending', proof_current=False, deps=None, reads=None, writes=None):
    return dict(
        id=id, status=status, proof_current=proof_current,
        deps=deps or [], reads=reads or [], writes=writes or [],
    )


class ReadyTest(unittest.TestCase):
    def test_no_deps_ready_regardless_of_own_proof_current(self):
        self.assertEqual(ready([task('A')], {}), ['A'])

    def test_sorted_lexically(self):
        tasks = [task('B'), task('A'), task('C')]
        self.assertEqual(ready(tasks, {}), ['A', 'B', 'C'])

    def test_ignores_non_pending(self):
        tasks = [task('A', status='running'), task('B', status='received', proof_current=True)]
        self.assertEqual(ready(tasks, {}), [])

    def test_dep_received_and_proof_current_unlocks(self):
        tasks = [
            task('A', deps=['D']),
            task('D', status='received', proof_current=True),
        ]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_dep_received_but_not_proof_current_blocks(self):
        tasks = [
            task('A', deps=['D']),
            task('D', status='received', proof_current=False),
        ]
        self.assertEqual(ready(tasks, {}), [])

    def test_dep_not_received_blocks(self):
        tasks = [
            task('A', deps=['D']),
            task('D', status='pending', proof_current=True),
        ]
        self.assertEqual(ready(tasks, {}), ['D'])

    def test_transitive_dep_stale_blocks_descendant(self):
        # A -> D (received, proof_current) -> E (received, NOT proof_current)
        tasks = [
            task('A', deps=['D']),
            task('D', status='received', proof_current=True, deps=['E']),
            task('E', status='received', proof_current=False),
        ]
        self.assertEqual(ready(tasks, {}), [])

    def test_transitive_dep_all_current_unlocks(self):
        tasks = [
            task('A', deps=['D']),
            task('D', status='received', proof_current=True, deps=['E']),
            task('E', status='received', proof_current=True),
        ]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_write_blocked_by_existing_read_lock(self):
        tasks = [task('A', writes=['r1'])]
        self.assertEqual(ready(tasks, {'r1': 'read'}), [])

    def test_write_blocked_by_existing_write_lock(self):
        tasks = [task('A', writes=['r1'])]
        self.assertEqual(ready(tasks, {'r1': 'write'}), [])

    def test_read_blocked_only_by_write_lock(self):
        tasks = [task('A', reads=['r1'])]
        self.assertEqual(ready(tasks, {'r1': 'write'}), [])

    def test_read_not_blocked_by_read_lock(self):
        tasks = [task('A', reads=['r1'])]
        self.assertEqual(ready(tasks, {'r1': 'read'}), ['A'])

    def test_pending_tasks_do_not_lock_each_other(self):
        tasks = [task('A', writes=['r1']), task('B', writes=['r1'])]
        self.assertEqual(ready(tasks, {}), ['A', 'B'])

    def test_duplicate_id_raises(self):
        tasks = [task('A'), task('A')]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_missing_dependency_raises(self):
        tasks = [task('A', deps=['ghost'])]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_unknown_status_raises(self):
        tasks = [task('A', status='cancelled')]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_unknown_lock_mode_raises(self):
        tasks = [task('A')]
        with self.assertRaises(ValueError):
            ready(tasks, {'r1': 'exclusive'})

    def test_self_cycle_raises(self):
        tasks = [task('A', deps=['A'])]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_cycle_between_two_tasks_raises(self):
        tasks = [task('A', deps=['B']), task('B', deps=['A'])]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_cycle_in_non_pending_component_raises(self):
        tasks = [
            task('A'),
            task('X', status='received', proof_current=True, deps=['Y']),
            task('Y', status='received', proof_current=True, deps=['X']),
        ]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_inputs_not_mutated(self):
        tasks = [task('A', deps=['D']), task('D', status='received', proof_current=True)]
        locks = {'r1': 'read'}
        snapshot_tasks = [dict(t) for t in tasks]
        snapshot_locks = dict(locks)
        ready(tasks, locks)
        self.assertEqual(tasks, snapshot_tasks)
        self.assertEqual(locks, snapshot_locks)


if __name__ == '__main__':
    unittest.main()
