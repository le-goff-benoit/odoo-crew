from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "odoo_flow", ROOT / "scripts" / "odoo_flow.py"
)
assert SPEC and SPEC.loader
FLOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FLOW)
GRAPH_PATH = ROOT / "workflows" / "odoo-workflow.json"


def finish(state, graph, node, outcome):
    FLOW.complete_node(state, graph, node, outcome, [f"preuve:{node}"])


class GraphDefinitionTest(unittest.TestCase):
    def test_physical_resource_conflicts_across_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            graph = json.loads(GRAPH_PATH.read_text())
            graph['nodes']['briefing']['locks'] = [{'resource': 'qa_db_module', 'mode': 'write'}]
            graph_file = root / 'graph.json'
            graph_file.write_text(json.dumps(graph))
            states = []
            for name in ('one', 'two'):
                project = root / name
                (project / '.odoo-agents').mkdir(parents=True)
                config = {'schema': 1, 'registry': str(root / 'shared.json'), 'bindings': {
                    'qa_db_module': {'id': 'postgresql://LOCALHOST/synthetic', 'parents': ['stack:synthetic']}}}
                (project / '.odoo-agents/resources.json').write_text(json.dumps(config))
                state = FLOW.new_state(project, 'development', name, graph_file)
                path = project / 'state.json'
                FLOW.write_state(path, state)
                states.append(path)
            FLOW.claim_node(states[0], graph_file, 'briefing', 'codex-one')
            with self.assertRaises(FLOW.FlowError):
                FLOW.claim_node(states[1], graph_file, 'briefing', 'claude-two')
            FLOW.release_claim(states[0], graph_file, 'briefing', 'codex-one', 'finished isolated work')
            FLOW.claim_node(states[1], graph_file, 'briefing', 'claude-two')

    def test_stack_write_conflicts_with_child_database_but_siblings_can_run(self):
        state = {'run_id': 'test', 'project': '/synthetic', 'resource_bindings': {
            'db1': {'id': 'postgresql://localhost/one', 'parents': ['stack:synthetic']},
            'db2': {'id': 'postgresql://localhost/two', 'parents': ['stack:synthetic']},
            'stack': {'id': 'stack:synthetic'}}}
        def locks(name):
            return FLOW.resolve_locks({'locks': [{'resource': name, 'mode': 'write'}]}, state)
        self.assertTrue(FLOW.locks_compatible(locks('db1'), locks('db2')))
        self.assertFalse(FLOW.locks_compatible(locks('stack'), locks('db1')))

    def test_empty_file_or_directory_is_not_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / 'empty.md'
            empty.touch()
            for path in (Path(tmp), empty):
                with self.assertRaises(FLOW.FlowError):
                    FLOW.evidence_files([str(path)])
            empty.write_text('Test exécuté : 3 critères satisfaits.')
            self.assertEqual(FLOW.evidence_files([str(empty)]), [str(empty)])

    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))

    def test_graph_is_valid(self):
        self.assertEqual(FLOW.validate_graph(self.graph), [])

    def test_graph_exposes_parallelism_and_bounded_cycles(self):
        analysis = FLOW.analyze_graph(self.graph)
        self.assertGreaterEqual(analysis["max_declared_parallelism"], 3)
        self.assertGreaterEqual(len(analysis["joins"]), 4)
        self.assertGreaterEqual(len(analysis["cycles"]), 3)
        self.assertEqual(
            set(analysis["human_gates"]),
            {
                "human_high_risk_scope_gate",
                "human_implementation_gate",
                "human_production_gate",
                "human_scope_gate",
            },
        )

    def test_unbounded_cycle_is_rejected(self):
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        graph["nodes"]["module_task_gate"]["max_outcome_uses"].pop("retry")
        errors = FLOW.validate_graph(graph)
        self.assertTrue(any("cycle non borné" in error for error in errors))

    def test_malformed_edge_is_reported_without_crashing(self):
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        graph["edges"].append({"id": "broken"})
        errors = FLOW.validate_graph(graph)
        self.assertTrue(any("champs manquants" in error for error in errors))


class FlowExecutionTest(unittest.TestCase):
    def setUp(self):
        self.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def state(self, kind):
        return FLOW.new_state(self.project, kind, "test", GRAPH_PATH)

    def test_completion_rejects_stale_structured_evidence(self):
        from odoo_evidence import execute
        code = self.project / 'code.py'
        code.write_text('value = 1')
        proof = self.project / 'proof.json'
        execute(self.project, ['code.py'], proof, [sys.executable, '-c', 'print("checked")'])
        state = self.state('development')
        path = self.project / 'state.json'
        FLOW.write_state(path, state)
        FLOW.claim_node(path, GRAPH_PATH, 'briefing', 'codex-test')
        code.write_text('value = 2')
        with self.assertRaisesRegex(FLOW.FlowError, 'code changé'):
            FLOW.complete_claimed_node(path, GRAPH_PATH, 'briefing', 'development', [str(proof)], None, 'codex-test', False)
        self.assertIn('briefing', json.loads(path.read_text())['claims'])

    def test_normal_module_path_forks_and_joins(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "module")
        finish(state, self.graph, "module_implementation", "done")
        self.assertEqual(
            FLOW.ready_nodes(state, self.graph),
            ["module_runtime_qa", "module_static_qa"],
        )
        waves = FLOW.parallel_waves(self.graph, FLOW.ready_nodes(state, self.graph))
        self.assertEqual(len(waves), 1)
        finish(state, self.graph, "module_static_qa", "done")
        self.assertEqual(FLOW.ready_nodes(state, self.graph), ["module_runtime_qa"])
        finish(state, self.graph, "module_runtime_qa", "done")
        self.assertEqual(FLOW.ready_nodes(state, self.graph), ["module_task_gate"])
        finish(state, self.graph, "module_task_gate", "pass")
        finish(state, self.graph, "journal_task", "done")
        finish(state, self.graph, "task_done", "done")
        self.assertEqual(state["status"], "complete")

    def test_terminal_dashboard_shows_agents_and_graph_position(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "module")
        finish(state, self.graph, "module_implementation", "done")
        dashboard = FLOW.format_dashboard(state, self.graph, show_history=True)
        self.assertIn("ODOO FLOW · test", dashboard)
        self.assertIn("POSITION DANS LE GRAPHE", dashboard)
        self.assertIn("VAGUE 1 · PARALLÈLE · 2 nœuds", dashboard)
        self.assertIn("AGENT · odoo-tester · graph-lane-runtime", dashboard)
        self.assertIn("AGENT · odoo-tester · graph-lane-static", dashboard)
        self.assertIn("Agents délégués 0 actif(s) · 2 prêt(s)", dashboard)
        self.assertIn("HISTORIQUE RÉCENT", dashboard)

    def test_terminal_dashboard_distinguishes_running_and_human_wait(self):
        running = self.state("development")
        finish(running, self.graph, "briefing", "development")
        finish(running, self.graph, "functional_review", "module")
        running["claims"]["module_implementation"] = {
            "at": "2026-09-07T10:00:00+00:00",
            "locks": [],
            "node": "module_implementation",
            "owner": "agent-dev",
            "state": "/tmp/state.json",
        }
        dashboard = FLOW.format_dashboard(running, self.graph)
        self.assertIn("État       EN COURS", dashboard)
        self.assertIn("AGENT · odoo-developer · propriétaire: agent-dev", dashboard)

        waiting = self.state("development")
        finish(waiting, self.graph, "briefing", "development")
        finish(waiting, self.graph, "functional_review", "blocked")
        dashboard = FLOW.format_dashboard(waiting, self.graph)
        self.assertIn("État       ATTENTE HUMAINE", dashboard)
        self.assertIn("◆ human_scope_gate", dashboard)
        self.assertIn("HUMAIN", dashboard)

    def test_running_status_wins_while_another_parallel_node_is_ready(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "module")
        finish(state, self.graph, "module_implementation", "done")
        state["claims"]["module_runtime_qa"] = {
            "at": "2026-09-07T10:00:00+00:00",
            "locks": [],
            "node": "module_runtime_qa",
            "owner": "codex-odoo-tester-runtime",
            "state": "/tmp/state.json",
        }
        summary = FLOW.state_summary(state, self.graph)
        self.assertEqual(summary["status"], "running")
        self.assertEqual(summary["running"], ["module_runtime_qa"])
        self.assertEqual(summary["ready"], ["module_static_qa"])
        dashboard = FLOW.format_dashboard(state, self.graph)
        self.assertIn("État       EN COURS", dashboard)
        self.assertIn("Agents délégués 1 actif(s) · 1 prêt(s)", dashboard)

    def test_cli_claim_and_json_status_keep_human_and_machine_outputs(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "module")
        state_path = self.project / "dashboard.json"
        FLOW.write_state(state_path, state)
        script = str(ROOT / "scripts" / "odoo_flow.py")

        claimed = subprocess.run(
            [
                sys.executable,
                script,
                "claim",
                str(state_path),
                "module_implementation",
                "--owner",
                "codex-odoo-developer",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(claimed.returncode, 0, claimed.stderr)
        self.assertIn(
            "▶ module_implementation · AGENT · odoo-developer", claimed.stdout
        )
        self.assertIn("Démarré par codex-odoo-developer", claimed.stdout)

        status = subprocess.run(
            [sys.executable, script, "status", str(state_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("État       EN COURS", status.stdout)
        self.assertIn("propriétaire: codex-odoo-developer", status.stdout)

        machine = subprocess.run(
            [sys.executable, script, "status", str(state_path), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(machine.returncode, 0, machine.stderr)
        payload = json.loads(machine.stdout)
        self.assertEqual(payload["running"], ["module_implementation"])
        self.assertEqual(
            payload["running_nodes"]["module_implementation"]["owner"],
            "codex-odoo-developer",
        )
        self.assertEqual(
            payload["running_nodes"]["module_implementation"]["role"],
            "odoo-developer",
        )

    def test_complex_analysis_has_three_parallel_lanes(self):
        state = self.state("development_complex")
        finish(state, self.graph, "briefing", "development_complex")
        ready = FLOW.ready_nodes(state, self.graph)
        self.assertEqual(
            ready,
            ["analyst_data_lane", "analyst_project_lane", "analyst_standard_lane"],
        )
        self.assertEqual(len(FLOW.parallel_waves(self.graph, ready)), 1)
        for node in ready:
            finish(state, self.graph, node, "done")
        self.assertEqual(FLOW.ready_nodes(state, self.graph), ["functional_synthesis"])

    def test_high_risk_path_requires_client_copy_lane(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "module_high_risk")
        finish(state, self.graph, "module_implementation_high_risk", "done")
        ready = FLOW.ready_nodes(state, self.graph)
        self.assertEqual(len(ready), 3)
        finish(state, self.graph, "module_high_static_qa", "done")
        finish(state, self.graph, "module_high_runtime_qa", "done")
        self.assertNotIn("module_high_gate", FLOW.ready_nodes(state, self.graph))
        finish(state, self.graph, "module_client_copy_qa", "done")
        self.assertEqual(FLOW.ready_nodes(state, self.graph), ["module_high_gate"])

    def test_retry_is_limited_to_two(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "module")
        for retry in range(2):
            finish(state, self.graph, "module_implementation", "done")
            finish(state, self.graph, "module_static_qa", "done")
            finish(state, self.graph, "module_runtime_qa", "done")
            finish(state, self.graph, "module_task_gate", "retry")
            self.assertEqual(retry + 1, state["outcome_counts"]["module_task_gate:retry"])
        finish(state, self.graph, "module_implementation", "done")
        finish(state, self.graph, "module_static_qa", "done")
        finish(state, self.graph, "module_runtime_qa", "done")
        with self.assertRaisesRegex(FLOW.FlowError, "atteint sa limite"):
            finish(state, self.graph, "module_task_gate", "retry")
        finish(state, self.graph, "module_task_gate", "blocked")
        finish(state, self.graph, "journal_task_blocked", "done")
        finish(state, self.graph, "task_blocked", "done")
        self.assertEqual(state["status"], "blocked")

    def test_human_gate_is_visible_as_waiting(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "blocked")
        summary = FLOW.state_summary(state, self.graph)
        self.assertEqual(summary["status"], "waiting_human")
        self.assertEqual(summary["ready"], ["human_scope_gate"])

    def test_release_red_path_never_reaches_docs(self):
        state = self.state("close")
        finish(state, self.graph, "briefing", "close")
        finish(state, self.graph, "close_precheck", "green")
        finish(state, self.graph, "release_technical_qa", "exhausted")
        self.assertEqual(
            FLOW.ready_nodes(state, self.graph), ["release_blocked_journal"]
        )
        finish(state, self.graph, "release_blocked_journal", "done")
        finish(state, self.graph, "release_blocked", "done")
        self.assertEqual(state["status"], "blocked")
        completed = {event["node"] for event in state["events"]}
        self.assertNotIn("client_docs", completed)

    def test_studio_lanes_are_serialized_by_client_copy_lock(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "studio")
        finish(state, self.graph, "studio_implementation", "done")
        ready = FLOW.ready_nodes(state, self.graph)
        self.assertEqual(ready, ["studio_diff_qa", "studio_scenario_qa"])
        self.assertEqual(len(FLOW.parallel_waves(self.graph, ready)), 2)

    def test_sensitive_support_bug_returns_to_analysis(self):
        state = self.state("support")
        finish(state, self.graph, "briefing", "support")
        finish(state, self.graph, "support_diagnosis", "bug_sensitive")
        self.assertEqual(
            FLOW.ready_nodes(state, self.graph), ["bug_sensitive_handoff_gate"]
        )
        with self.assertRaisesRegex(FLOW.FlowError, "issue invalide"):
            finish(state, self.graph, "bug_sensitive_handoff_gate", "module")
        finish(state, self.graph, "bug_sensitive_handoff_gate", "review_high_risk")
        self.assertEqual(
            FLOW.ready_nodes(state, self.graph), ["functional_review_high_risk"]
        )
        finish(state, self.graph, "functional_review_high_risk", "module")
        finish(state, self.graph, "module_implementation_high_risk", "done")
        self.assertEqual(
            FLOW.ready_nodes(state, self.graph),
            ["module_client_copy_qa", "module_high_runtime_qa", "module_high_static_qa"],
        )

    def test_sensitive_support_studio_detour_cannot_downgrade_module_qa(self):
        state = self.state("support")
        finish(state, self.graph, "briefing", "support")
        finish(state, self.graph, "support_diagnosis", "bug_sensitive")
        finish(state, self.graph, "bug_sensitive_handoff_gate", "review_high_risk")
        finish(state, self.graph, "functional_review_high_risk", "studio")
        finish(state, self.graph, "studio_implementation", "blocked")
        self.assertEqual(
            FLOW.ready_nodes(state, self.graph), ["human_high_risk_scope_gate"]
        )
        finish(state, self.graph, "human_high_risk_scope_gate", "module")
        self.assertEqual(
            FLOW.ready_nodes(state, self.graph), ["module_implementation_high_risk"]
        )

    def test_graph_hash_prevents_silent_resume_after_change(self):
        state = self.state("development")
        state_path = self.project / "state.json"
        FLOW.write_state(state_path, state)
        graph_copy = self.project / "graph.json"
        graph_copy.write_text(GRAPH_PATH.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(FLOW.FlowError, "graphe a changé"):
            FLOW.load_state(state_path, graph_copy)

    def test_claim_can_be_released_even_after_graph_disappears(self):
        state = self.state('development')
        state_path = self.project / 'state.json'
        FLOW.write_state(state_path, state)
        FLOW.claim_node(state_path, GRAPH_PATH, 'briefing', 'codex-test')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/odoo_flow.py'),
                                 '--graph', str(self.project / 'missing.json'), 'release',
                                 str(state_path), 'briefing', '--owner', 'codex-test', '--reason', 'interruption'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = FLOW.load_json(state_path)
        self.assertFalse(saved['claims'])
        self.assertTrue(saved['start_pending'])

    def test_migration_rejects_changed_meaning_of_active_edge(self):
        state = self.state('development')
        finish(state, self.graph, 'briefing', 'development')
        altered = json.loads(json.dumps(self.graph))
        active = next(edge for edge in altered['edges'] if state['tokens'].get(edge['id']))
        active['to'] = 'task_done'
        with self.assertRaises(FLOW.FlowError):
            FLOW.validate_migration(state, altered)

    def test_start_directories_are_local_git_ignored(self):
        FLOW.ensure_local_flow_dirs(self.project)
        for name in ("flows", "flow-artifacts"):
            ignore = self.project / ".odoo-agents" / name / ".gitignore"
            self.assertEqual(ignore.read_text(encoding="utf-8"), "*\n!.gitignore\n")

    def test_cli_migrates_a_compatible_state_explicitly(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        state_path = self.project / "state.json"
        FLOW.write_state(state_path, state)
        graph_copy = self.project / "graph.json"
        graph_copy.write_text(GRAPH_PATH.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "odoo_flow.py"),
                "--graph",
                str(graph_copy),
                "migrate",
                str(state_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        migrated = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(migrated["graph_sha256"], FLOW.graph_hash(graph_copy))

    def test_claims_enforce_cross_run_resource_locks(self):
        paths = []
        for run_id in ("first", "second"):
            state = FLOW.new_state(self.project, "development", run_id, GRAPH_PATH)
            finish(state, self.graph, "briefing", "development")
            finish(state, self.graph, "functional_review", "module")
            path = self.project / f"{run_id}.json"
            FLOW.write_state(path, state)
            paths.append(path)
        first = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "odoo_flow.py"), "claim", str(paths[0]), "module_implementation", "--owner", "one"],
            check=False,
            capture_output=True,
            text=True,
        )
        second = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "odoo_flow.py"), "claim", str(paths[1]), "module_implementation", "--owner", "two"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 2)
        self.assertIn("verrou incompatible", second.stderr)

    def test_concurrent_completions_do_not_lose_events(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "module")
        finish(state, self.graph, "module_implementation", "done")
        state_path = self.project / "parallel.json"
        FLOW.write_state(state_path, state)
        evidence = self.project / "evidence.md"
        evidence.write_text("preuve", encoding="utf-8")
        script = str(ROOT / "scripts" / "odoo_flow.py")
        for node in ("module_static_qa", "module_runtime_qa"):
            claimed = subprocess.run(
                [sys.executable, script, "claim", str(state_path), node, "--owner", node],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(claimed.returncode, 0, claimed.stderr)
        processes = [
            subprocess.Popen(
                [
                    sys.executable,
                    script,
                    "complete",
                    str(state_path),
                    node,
                    "--outcome",
                    "done",
                    "--evidence",
                    str(evidence),
                    "--owner",
                    node,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for node in ("module_static_qa", "module_runtime_qa")
        ]
        results = [process.communicate(timeout=10) for process in processes]
        for process, (_stdout, stderr) in zip(processes, results):
            self.assertEqual(process.returncode, 0, stderr)
        persisted = json.loads(state_path.read_text(encoding="utf-8"))
        completed = [event["node"] for event in persisted["events"]]
        self.assertIn("module_static_qa", completed)
        self.assertIn("module_runtime_qa", completed)
        self.assertEqual(FLOW.ready_nodes(persisted, self.graph), ["module_task_gate"])

    def test_human_gate_requires_explicit_confirmation_and_file(self):
        state = self.state("development")
        finish(state, self.graph, "briefing", "development")
        finish(state, self.graph, "functional_review", "blocked")
        state_path = self.project / "human.json"
        FLOW.write_state(state_path, state)
        evidence = self.project / "decision.md"
        evidence.write_text("Décision de l'humain", encoding="utf-8")
        command = [
            sys.executable,
            str(ROOT / "scripts" / "odoo_flow.py"),
            "complete",
            str(state_path),
            "human_scope_gate",
            "--outcome",
            "cancel",
            "--evidence",
            str(evidence),
        ]
        refused = subprocess.run(command, check=False, capture_output=True, text=True)
        accepted = subprocess.run(
            command + ["--human-confirmed"], check=False, capture_output=True, text=True
        )
        self.assertEqual(refused.returncode, 2)
        self.assertIn("--human-confirmed", refused.stderr)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)


if __name__ == "__main__":
    unittest.main()
