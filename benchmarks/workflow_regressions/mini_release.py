"""W05 : vrais outils plan/flow sur graphe minimal explicite, sans simuler Odoo."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import odoo_evidence as evidence  # noqa: E402 - repository-local tools
import odoo_flow as flow  # noqa: E402
import odoo_intentions as intentions  # noqa: E402
import odoo_orchestrate as orchestration  # noqa: E402
import odoo_plan as plan  # noqa: E402


def execute(output: Path):
    started = time.monotonic()
    output.mkdir(parents=True, exist_ok=False)
    project = output / "project"
    release = project / "changelog/release"
    release.mkdir(parents=True)
    (release / "README.md").write_text(
        "<!-- release ouverte -->\n# Synthetic mini-release\n"
    )
    (project / "request.md").write_text(
        "Initial requirement: preserve explicit totals.\n"
    )
    (project / ".odoo-agents").mkdir()
    (project / ".odoo-agents/config").write_text("series = 19.0\n")
    for scope in ("totals", "pdf"):
        (project / scope).mkdir()
        (project / scope / "check.py").write_text(
            'assert round(1.235, 2) == 1.24\nprint("synthetic assertion passed")\n'
        )
    graph = {
        "schema_version": 1,
        "name": "workflow-probe-only",
        "start": "prepare",
        "nodes": {
            "prepare": {
                "executor": "orchestrator",
                "evidence": ["real check output"],
                "locks": [{"resource": "probe", "mode": "write"}],
            },
            "received": {
                "executor": "orchestrator",
                "terminal": "complete",
                "outcomes": ["done"],
                "evidence": ["real check output"],
            },
        },
        "edges": [
            {
                "id": "checked-" + kind,
                "from": "prepare",
                "outcome": kind,
                "to": "received",
            }
            for kind in sorted(flow.KINDS)
        ],
    }
    tools = output / "tooling"
    (tools / "workflows").mkdir(parents=True)
    graphpath = tools / "workflows/odoo-workflow.json"
    graphpath.write_text(json.dumps(graph))
    assert not flow.validate_graph(graph)

    def task(identifier, scope, depends=None):
        return {
            "id": identifier,
            "title": identifier,
            "request": "request.md",
            "request_excerpt": "Initial requirement: preserve explicit totals.",
            "route": "module",
            "risk": "normal",
            "acceptance": ["synthetic assertion passes"],
            "scopes": [scope],
            "depends_on": depends or [],
            "technical_reason": "Isolated workflow engine calibration",
            "reads": [],
            "writes": [scope],
            "checks": [
                {
                    "id": "assertion",
                    "command": [sys.executable, scope + "/check.py"],
                    "environment": "synthetic-local-v1",
                    "cases": ["explicit value"],
                }
            ],
            "execution": {"provider": "codex", "model": "principal", "effort": "high"},
        }

    definition = {
        "schema": 2,
        "author": {"role": "orchestrator", "provider": "codex", "model": "principal"},
        "decisions": [],
        "intentions_file": "changelog/release/intentions.json",
        "tasks": [task("T01", "totals"), task("T02", "pdf", ["T01"])],
    }
    intentions.update(release, {"items": []})
    plan.initialise(release, definition)
    proof_paths = []

    def start(identifier):
        with patch.object(plan, "ROOT", tools):
            path = Path(plan.mutate(release, "start", identifier))
        flow.claim_node(path, graphpath, "prepare", "codex-orchestrator-probe")
        return path

    def finish(identifier, path):
        data, _ = plan.read(release)
        current = next(t for t in data["tasks"] if t["id"] == identifier)
        proof = project / "proofs" / f"{identifier}.json"
        evidence.execute(
            project,
            current["scopes"],
            proof,
            current["checks"][0]["command"],
            environment="synthetic-local-v1",
        )
        for node, outcome in [("prepare", "development"), ("received", "done")]:
            if node == "received":
                flow.claim_node(path, graphpath, node, "codex-orchestrator-probe")
            flow.complete_claimed_node(
                path,
                graphpath,
                node,
                outcome,
                [str(proof)],
                "real assertion on synthetic fixture",
                "codex-orchestrator-probe",
                False,
            )
        acceptance = project / f"{identifier}-acceptance.md"
        acceptance.write_text(
            "Synthetic assertion independently executed and received.\n"
        )
        memory = project / f"{identifier}-memory.md"
        memory.write_text("No customer decision inferred from synthetic calibration.\n")
        plan.mutate(
            release,
            "finish",
            identifier,
            proof=str(proof.relative_to(project)),
            acceptance=acceptance.name,
            memory=memory.name,
        )
        proof_paths.append(proof)

    finish("T01", start("T01"))
    before, _ = plan.read(release)
    received = before["tasks"][0]
    proof_hash = hashlib.sha256(proof_paths[0].read_bytes()).hexdigest()
    state = orchestration.update(
        project,
        "activate",
        owner="codex-orchestrator-probe",
        provider="codex",
        model="principal",
        session_id="before",
        release=release,
        tasks=["T01", "T02"],
    )
    pending = start("T02")
    orchestration.update(
        project,
        "interrupt",
        owner="codex-orchestrator-probe",
        reason="Synthetic user interruption",
    )
    (project / "late.md").write_text(
        "Add French invoice label without revisiting accepted totals.\n"
    )
    intentions.update(
        release,
        {
            "items": [
                {
                    "id": "I03",
                    "text": "French invoice label",
                    "purpose": "French label present",
                    "source": {"path": "late.md"},
                }
            ]
        },
    )
    late = task("T03", "pdf", ["T01"])
    late["intentions"] = ["I03"]
    late.pop("technical_reason")
    plan.append_tasks(release, {"schema": 2, "tasks": [late]})
    after, _ = plan.read(release)
    assert after["tasks"][0] == received
    assert hashlib.sha256(proof_paths[0].read_bytes()).hexdigest() == proof_hash
    assert not plan.available(after, project, "T03")[0], (
        "Concurrent PDF writers must conflict"
    )
    resumed = orchestration.update(
        project,
        "resume",
        owner="codex-orchestrator-probe",
        session_id="after",
        tasks=["T01", "T02", "T03"],
    )
    assert resumed["id"] == state["id"]
    finish("T02", pending)
    finish("T03", start("T03"))
    current, _ = plan.read(release)
    assert all(
        status[0] == "validated" for status in plan.statuses(current, project).values()
    )
    assert intentions.reconcile(release)["items"][0]["tasks"] == ["T03"]
    orchestration.update(project, "complete", owner="codex-orchestrator-probe")
    # Negative oracle: replacing a proof invalidates only its consumers; preserve original bytes after observation.
    original = proof_paths[0].read_bytes()
    proof_paths[0].write_text("{}")
    rejected = plan.statuses(current, project)["T01"][0] == "stale"
    proof_paths[0].write_bytes(original)
    assert rejected
    result = {
        "schema": 1,
        "status": "completed",
        "seconds": round(time.monotonic() - started, 3),
        "pass": True,
        "actual_tool_commands": 3,
        "received_tasks": ["T01", "T02", "T03"],
        "late_intention": "I03",
        "scope_conflict_rejected": True,
        "same_orchestration_id": True,
        "received_proof_sha256": proof_hash,
        "changed_proof_rejected": rejected,
        "scope": "Real plan, intentions, orchestration, flow claim/complete and evidence APIs; minimal two-node synthetic graph, not an Odoo QA run",
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
