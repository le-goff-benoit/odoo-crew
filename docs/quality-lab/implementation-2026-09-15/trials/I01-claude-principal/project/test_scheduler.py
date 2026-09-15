"""Tests de scheduler.ready : éligibilité transitive, verrous et rejets."""
import copy
import unittest

from scheduler import ready


def task(identifier, status='pending', proof_current=True, deps=(), reads=(), writes=()):
    return dict(id=identifier, status=status, proof_current=proof_current,
                deps=list(deps), reads=list(reads), writes=list(writes))


def received(identifier, proof_current=True, deps=()):
    return task(identifier, status='received', proof_current=proof_current, deps=deps)


class EligibilityTest(unittest.TestCase):
    def test_only_pending_tasks_are_proposed(self):
        tasks = [task('A'), task('B', status='running'), received('C')]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_result_is_sorted_lexicographically(self):
        tasks = [task('b'), task('B'), task('A10'), task('A9')]
        self.assertEqual(ready(tasks, {}), ['A10', 'A9', 'B', 'b'])

    def test_own_proof_current_is_irrelevant(self):
        self.assertEqual(ready([task('A', proof_current=False)], {}), ['A'])

    def test_dependency_must_be_received(self):
        tasks = [task('A', deps=['B']), task('B', status='running')]
        self.assertEqual(ready(tasks, {}), [])

    def test_received_dependency_with_stale_proof_blocks(self):
        tasks = [task('A', deps=['B']), received('B', proof_current=False)]
        self.assertEqual(ready(tasks, {}), [])

    def test_received_dependency_with_current_proof_releases(self):
        tasks = [task('A', deps=['B']), received('B')]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_stale_transitive_dependency_blocks_descendant(self):
        """Une dépendance reçue mais fondée sur une dépendance périmée ne libère pas."""
        tasks = [task('A', deps=['B']), received('B', deps=['C']), received('C', proof_current=False)]
        self.assertEqual(ready(tasks, {}), [])

    def test_running_transitive_dependency_blocks_descendant(self):
        tasks = [task('A', deps=['B']), received('B', deps=['C']), task('C', status='running')]
        self.assertEqual(ready(tasks, {}), [])

    def test_deep_received_chain_releases(self):
        tasks = [task('A', deps=['B']), received('B', deps=['C']), received('C', deps=['D']), received('D')]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_diamond_shares_memoized_verdict(self):
        tasks = [task('A', deps=['B', 'C']), received('B', deps=['D']), received('C', deps=['D']),
                 received('D', proof_current=False)]
        self.assertEqual(ready(tasks, {}), [])
        tasks[3]['proof_current'] = True
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_one_stale_branch_among_many_blocks(self):
        tasks = [task('A', deps=['B', 'C']), received('B'), received('C', proof_current=False)]
        self.assertEqual(ready(tasks, {}), [])

    def test_pending_dependency_blocks_even_when_itself_ready(self):
        """B est un candidat, mais rester pending ne libère pas A."""
        tasks = [task('A', deps=['B']), task('B')]
        self.assertEqual(ready(tasks, {}), ['B'])

    def test_wide_chain_does_not_hit_recursion_limit(self):
        depth = 5000
        tasks = [task('pending-task', deps=['n0'])]
        tasks += [received('n%d' % i, deps=['n%d' % (i + 1)]) for i in range(depth)]
        tasks.append(received('n%d' % depth))
        self.assertEqual(ready(tasks, {}), ['pending-task'])

    def test_empty_task_list(self):
        self.assertEqual(ready([], {}), [])


class LockTest(unittest.TestCase):
    def test_write_blocked_by_write_lock(self):
        self.assertEqual(ready([task('A', writes=['db'])], {'db': 'write'}), [])

    def test_write_blocked_by_read_lock(self):
        self.assertEqual(ready([task('A', writes=['db'])], {'db': 'read'}), [])

    def test_read_blocked_by_write_lock(self):
        self.assertEqual(ready([task('A', reads=['db'])], {'db': 'write'}), [])

    def test_read_allowed_under_read_lock(self):
        self.assertEqual(ready([task('A', reads=['db'])], {'db': 'read'}), ['A'])

    def test_lock_on_untouched_resource_is_ignored(self):
        self.assertEqual(ready([task('A', reads=['x'], writes=['y'])], {'z': 'write'}), ['A'])

    def test_blocked_resource_among_several_blocks_task(self):
        self.assertEqual(ready([task('A', reads=['a', 'b'], writes=['c'])], {'b': 'write'}), [])
        self.assertEqual(ready([task('A', reads=['a'], writes=['c', 'd'])], {'d': 'read'}), [])

    def test_task_reading_and_writing_same_locked_resource(self):
        self.assertEqual(ready([task('A', reads=['db'], writes=['db'])], {'db': 'read'}), [])

    def test_pending_candidates_do_not_lock_each_other(self):
        """La fonction expose les candidats, pas une vague déjà revendiquée."""
        tasks = [task('A', writes=['db']), task('B', writes=['db']), task('C', reads=['db'])]
        self.assertEqual(ready(tasks, {}), ['A', 'B', 'C'])

    def test_non_pending_tasks_do_not_create_locks(self):
        tasks = [task('A', writes=['db']), task('B', status='running', writes=['db'])]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_lock_blocks_even_when_dependencies_are_satisfied(self):
        tasks = [task('A', deps=['B'], writes=['db']), received('B')]
        self.assertEqual(ready(tasks, {}), ['A'])
        self.assertEqual(ready(tasks, {'db': 'write'}), [])


class RejectionTest(unittest.TestCase):
    def test_duplicate_identifier(self):
        with self.assertRaises(ValueError):
            ready([task('A'), task('A')], {})

    def test_duplicate_identifier_among_non_pending(self):
        with self.assertRaises(ValueError):
            ready([task('A'), received('B'), received('B')], {})

    def test_missing_dependency(self):
        with self.assertRaises(ValueError):
            ready([task('A', deps=['ghost'])], {})

    def test_missing_dependency_of_non_pending_task(self):
        with self.assertRaises(ValueError):
            ready([task('A'), received('B', deps=['ghost'])], {})

    def test_unknown_status(self):
        with self.assertRaises(ValueError):
            ready([task('A', status='done')], {})

    def test_unknown_lock_mode(self):
        with self.assertRaises(ValueError):
            ready([task('A')], {'db': 'exclusive'})

    def test_unknown_lock_mode_on_untouched_resource(self):
        with self.assertRaises(ValueError):
            ready([task('A', reads=['x'])], {'other': 'append'})

    def test_self_dependency_is_a_cycle(self):
        with self.assertRaises(ValueError):
            ready([task('A', deps=['A'])], {})

    def test_cycle_between_pending_tasks(self):
        with self.assertRaises(ValueError):
            ready([task('A', deps=['B']), task('B', deps=['A'])], {})

    def test_cycle_in_a_component_that_is_not_pending(self):
        """Même hors du chemin des candidats, un cycle est rejeté."""
        tasks = [task('A'), received('B', deps=['C']), received('C', deps=['B'])]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_cycle_unreachable_from_any_pending_task(self):
        tasks = [task('A', deps=['Z']), received('Z'),
                 task('X', status='running', deps=['Y']), task('Y', status='running', deps=['X'])]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_longer_cycle(self):
        tasks = [received('A', deps=['B']), received('B', deps=['C']), received('C', deps=['A'])]
        with self.assertRaises(ValueError):
            ready(tasks, {})

    def test_diamond_is_not_a_cycle(self):
        tasks = [task('A', deps=['B', 'C']), received('B', deps=['D']), received('C', deps=['D']), received('D')]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_repeated_dependency_is_not_a_cycle(self):
        tasks = [task('A', deps=['B', 'B']), received('B')]
        self.assertEqual(ready(tasks, {}), ['A'])

    def test_long_chain_cycle_detection_is_iterative(self):
        depth = 5000
        tasks = [received('n%d' % i, deps=['n%d' % (i + 1)]) for i in range(depth)]
        tasks.append(received('n%d' % depth, deps=['n0']))
        with self.assertRaises(ValueError):
            ready(tasks, {})


class PurityTest(unittest.TestCase):
    def test_inputs_are_left_untouched(self):
        tasks = [task('A', deps=['B'], reads=['r'], writes=['w']),
                 received('B', deps=['C']), received('C', proof_current=False),
                 task('D', status='running', writes=['w'])]
        locks = {'w': 'read', 'other': 'write'}
        snapshot_tasks, snapshot_locks = copy.deepcopy(tasks), copy.deepcopy(locks)
        ready(tasks, locks)
        self.assertEqual(tasks, snapshot_tasks)
        self.assertEqual(locks, snapshot_locks)

    def test_result_is_a_plain_sorted_list_of_ids(self):
        result = ready([task('B'), task('A')], {})
        self.assertIsInstance(result, list)
        self.assertEqual(result, ['A', 'B'])

    def test_repeated_calls_agree(self):
        tasks = [task('A', deps=['B']), received('B')]
        self.assertEqual(ready(tasks, {}), ready(tasks, {}))


if __name__ == '__main__':
    unittest.main()
