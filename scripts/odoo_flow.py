#!/usr/bin/env python3
"""Valide et pilote le graphe de travail des agents Odoo.

Le script ne réalise aucune opération Odoo. Il conserve seulement l'état du
workflow, contrôle les transitions, expose les nœuds prêts et empêche les
boucles de reprise non bornées. L'orchestrateur principal est l'unique
écrivain du fichier d'état ; les agents spécialisés écrivent leurs preuves
dans les chemins distincts qu'il leur donne.

Exemples :
    odoo_flow.py validate
    odoo_flow.py analyze
    odoo_flow.py render --format mermaid
    odoo_flow.py start ~/projet --kind development --id ajout-reference
    odoo_flow.py ready ~/projet/.odoo-agents/flows/ajout-reference.json
    odoo_flow.py complete <état.json> briefing --outcome development \
        --evidence /tmp/briefing.txt
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import re
import sys
import tempfile
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent.parent
DEFAULT_GRAPH = HERE / "workflows" / "odoo-workflow.json"
KINDS = {
    "close",
    "development",
    "development_complex",
    "documentation",
    "environment",
    "express",
    "feedback",
    "functional",
    "support",
    "technical",
    "validation",
}


class FlowError(RuntimeError):
    """Erreur de définition ou d'utilisation du graphe."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FlowError(f"fichier introuvable : {path}") from exc
    except json.JSONDecodeError as exc:
        raise FlowError(f"JSON invalide dans {path}:{exc.lineno}: {exc.msg}") from exc


@contextmanager
def exclusive_lock(path: Path):
    """Sérialise les lectures-modifications-écritures entre processus."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def graph_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edges_by(graph: dict[str, Any], key: str) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in graph["edges"]:
        result[edge[key]].append(edge)
    return result


def node_outcomes(graph: dict[str, Any], node_name: str) -> list[str]:
    node = graph["nodes"][node_name]
    outcomes = set(node.get("outcomes", []))
    outcomes.update(
        edge["outcome"] for edge in graph["edges"] if edge["from"] == node_name
    )
    return sorted(outcomes)


def strongly_connected_components(graph: dict[str, Any]) -> list[list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in graph["edges"]:
        adjacency[edge["from"]].append(edge["to"])

    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in adjacency[node]:
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])

        if lowlinks[node] != indices[node]:
            return
        component: list[str] = []
        while stack:
            member = stack.pop()
            on_stack.remove(member)
            component.append(member)
            if member == node:
                break
        components.append(sorted(component))

    for node in graph["nodes"]:
        if node not in indices:
            visit(node)
    return components


def cyclic_components(graph: dict[str, Any]) -> list[list[str]]:
    self_loops = {
        edge["from"] for edge in graph["edges"] if edge["from"] == edge["to"]
    }
    return [
        component
        for component in strongly_connected_components(graph)
        if len(component) > 1 or component[0] in self_loops
    ]


def validate_graph(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if graph.get("schema_version") != 1:
        errors.append("schema_version doit valoir 1")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, dict) or not nodes:
        return errors + ["nodes doit être un objet non vide"]
    if not isinstance(edges, list):
        return errors + ["edges doit être une liste"]
    if graph.get("start") not in nodes:
        errors.append("le nœud start est absent de nodes")

    edge_ids: set[str] = set()
    malformed_edge = False
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for position, edge in enumerate(edges, start=1):
        missing = {key for key in ("id", "from", "outcome", "to") if key not in edge}
        if missing:
            errors.append(f"arête {position}: champs manquants {sorted(missing)}")
            malformed_edge = True
            continue
        if edge["id"] in edge_ids:
            errors.append(f"identifiant d'arête dupliqué : {edge['id']}")
        edge_ids.add(edge["id"])
        if edge["from"] not in nodes:
            errors.append(f"{edge['id']}: source inconnue {edge['from']}")
        if edge["to"] not in nodes:
            errors.append(f"{edge['id']}: cible inconnue {edge['to']}")
        incoming[edge["to"]].append(edge)
        outgoing[edge["from"]].append(edge)

    if malformed_edge:
        return errors

    for name, node in nodes.items():
        executor = node.get("executor")
        if executor not in {"agent", "human", "orchestrator"}:
            errors.append(f"{name}: executor invalide {executor!r}")
        if executor == "agent" and not node.get("role"):
            errors.append(f"{name}: un agent doit nommer son role")
        if node.get("join", "any") not in {"all", "any"}:
            errors.append(f"{name}: join doit valoir all ou any")
        if node.get("join") == "all" and len(incoming[name]) < 2:
            errors.append(f"{name}: une jointure all demande au moins deux entrées")
        terminal = node.get("terminal")
        if terminal and terminal not in {"blocked", "cancelled", "complete"}:
            errors.append(f"{name}: statut terminal invalide {terminal!r}")
        if terminal and outgoing[name]:
            errors.append(f"{name}: un terminal ne doit pas avoir d'arête sortante")
        if not terminal and not outgoing[name]:
            errors.append(f"{name}: nœud non terminal sans sortie")
        for lock in node.get("locks", []):
            if set(lock) != {"resource", "mode"} or lock.get("mode") not in {"read", "write"}:
                errors.append(f"{name}: verrou invalide {lock!r}")
        limits = node.get("max_outcome_uses", {})
        for outcome, limit in limits.items():
            if outcome not in node_outcomes(graph, name):
                errors.append(f"{name}: limite posée sur l'issue inconnue {outcome}")
            if not isinstance(limit, int) or limit < 1:
                errors.append(f"{name}: limite invalide pour {outcome}")

    if graph.get("start") in nodes:
        entries = set(node_outcomes(graph, graph["start"]))
        if entries != KINDS:
            errors.append(
                "les issues du nœud start diffèrent de KINDS : "
                f"graphe={sorted(entries)}, script={sorted(KINDS)}"
            )
        reached = {graph["start"]}
        changed = True
        while changed:
            changed = False
            for edge in edges:
                if edge.get("from") in reached and edge.get("to") not in reached:
                    reached.add(edge["to"])
                    changed = True
        for name in sorted(set(nodes) - reached):
            errors.append(f"nœud inaccessible depuis start : {name}")

    unbounded_edges = [
        edge
        for edge in edges
        if edge.get("outcome")
        not in nodes.get(edge.get("from"), {}).get("max_outcome_uses", {})
    ]
    residual = dict(graph)
    residual["edges"] = unbounded_edges
    for component in cyclic_components(residual):
        errors.append(f"cycle non borné : {' -> '.join(component)}")

    terminals = {name for name, node in nodes.items() if node.get("terminal")}
    can_finish = set(terminals)
    changed = True
    while changed:
        changed = False
        for edge in edges:
            if edge.get("to") in can_finish and edge.get("from") not in can_finish:
                can_finish.add(edge["from"])
                changed = True
    for name in sorted(set(nodes) - can_finish):
        errors.append(f"aucun terminal atteignable depuis : {name}")
    return errors


def analyze_graph(graph: dict[str, Any]) -> dict[str, Any]:
    outgoing: dict[tuple[str, str], list[str]] = defaultdict(list)
    incoming = edges_by(graph, "to")
    for edge in graph["edges"]:
        outgoing[(edge["from"], edge["outcome"])].append(edge["to"])
    forks = {
        f"{node}:{outcome}": targets
        for (node, outcome), targets in outgoing.items()
        if len(targets) > 1
    }
    joins = {
        name: sorted(edge["from"] for edge in incoming[name])
        for name, node in graph["nodes"].items()
        if node.get("join") == "all"
    }
    terminals = {
        name: node["terminal"]
        for name, node in graph["nodes"].items()
        if node.get("terminal")
    }
    return {
        "name": graph.get("name"),
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "agent_nodes": sum(
            node.get("executor") == "agent" for node in graph["nodes"].values()
        ),
        "human_gates": sorted(
            name
            for name, node in graph["nodes"].items()
            if node.get("executor") == "human"
        ),
        "terminals": terminals,
        "forks": forks,
        "joins": joins,
        "cycles": cyclic_components(graph),
        "max_declared_parallelism": max([len(targets) for targets in forks.values()] or [1]),
    }


def compatible(first: dict[str, Any], second: dict[str, Any]) -> bool:
    first_locks = {lock["resource"]: lock["mode"] for lock in first.get("locks", [])}
    second_locks = {lock["resource"]: lock["mode"] for lock in second.get("locks", [])}
    for resource in set(first_locks) & set(second_locks):
        if "write" in {first_locks[resource], second_locks[resource]}:
            return False
    return True


def locks_compatible(
    first: list[dict[str, str]], second: list[dict[str, str]]
) -> bool:
    return compatible({"locks": first}, {"locks": second})


def canonical_resource(value: str) -> str:
    if value.startswith('path:'):
        return 'path:' + str(Path(value[5:]).expanduser().resolve())
    if value.startswith('postgresql://'):
        uri = urlsplit(value)
        if not uri.hostname or not uri.path.strip('/') or uri.username or uri.password or uri.query or uri.fragment:
            raise FlowError('identité PostgreSQL invalide ou contenant des identifiants')
        return f"postgresql://{uri.hostname.lower()}:{uri.port or 5432}{uri.path}"
    if not value or any(c.isspace() for c in value):
        raise FlowError('identité de ressource invalide')
    return value


def resolve_locks(node: dict[str, Any], state: dict[str, Any]) -> list[dict[str, str]]:
    bindings = state.get('resource_bindings', {})
    resolved = {}
    for lock in node.get('locks', []):
        name = lock['resource'].format(run=state['run_id'])
        binding = bindings.get(name)
        if binding:
            resource = canonical_resource(binding['id'])
            parents = binding.get('parents', [])
        else:
            resource = f"project:{state['project']}:{name}" if state.get('resource_registry') else name
            parents = []
        for key, mode in [(resource, lock['mode']), *[(canonical_resource(p), 'read') for p in parents]]:
            resolved[key] = 'write' if 'write' in (resolved.get(key), mode) else 'read'
    return [{'resource': key, 'mode': mode} for key, mode in resolved.items()]


def parallel_waves(graph: dict[str, Any], ready: list[str], state=None) -> list[list[str]]:
    waves: list[list[str]] = []
    nodes = {name: dict(graph['nodes'][name], locks=resolve_locks(graph['nodes'][name], state))
             if state else graph['nodes'][name] for name in ready}
    for name in ready:
        for wave in waves:
            if all(compatible(nodes[name], nodes[other]) for other in wave):
                wave.append(name)
                break
        else:
            waves.append([name])
    return waves


def load_state(path: Path, graph_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    graph = load_json(graph_path)
    errors = validate_graph(graph)
    if errors:
        raise FlowError("graphe invalide :\n- " + "\n- ".join(errors))
    state = load_json(path)
    if state.get("graph_sha256") != graph_hash(graph_path):
        raise FlowError(
            "le graphe a changé depuis la création de cet état ; "
            "terminez ou migrez explicitement ce run"
        )
    return state, graph


def incoming_edges(graph: dict[str, Any], node_name: str) -> list[dict[str, Any]]:
    return [edge for edge in graph["edges"] if edge["to"] == node_name]


def ready_nodes(state: dict[str, Any], graph: dict[str, Any]) -> list[str]:
    if state.get("status") in {"blocked", "cancelled", "complete"}:
        return []
    ready: list[str] = []
    for name, node in graph["nodes"].items():
        if name in state.get("claims", {}):
            continue
        if name == graph["start"] and state.get("start_pending"):
            ready.append(name)
            continue
        incoming = incoming_edges(graph, name)
        if not incoming:
            continue
        counts = [state["tokens"].get(edge["id"], 0) for edge in incoming]
        if node.get("join", "any") == "all":
            is_ready = all(count > 0 for count in counts)
        else:
            is_ready = any(count > 0 for count in counts)
        if is_ready:
            ready.append(name)
    return sorted(ready)


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now()
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def ensure_local_flow_dirs(project: Path) -> None:
    """Crée les dossiers d'exécution locale sans les verser dans git."""
    for name in ("flows", "flow-artifacts"):
        directory = project / ".odoo-agents" / name
        directory.mkdir(parents=True, exist_ok=True)
        ignore = directory / ".gitignore"
        if not ignore.exists():
            ignore.write_text("*\n!.gitignore\n", encoding="utf-8")


def registry_path(state: dict[str, Any]) -> Path:
    return Path(state["resource_registry"]) if state.get("resource_registry") else Path(state["project"]) / ".odoo-agents" / "flows" / "resource-locks.json"


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "claims": []}
    registry = load_json(path)
    if registry.get("schema_version") != 1 or not isinstance(registry.get("claims"), list):
        raise FlowError(f"registre de verrous invalide : {path}")
    return registry


def write_registry(path: Path, registry: dict[str, Any]) -> None:
    write_state(path, registry)


def evidence_files(values: list[str]) -> list[str]:
    resolved: list[str] = []
    for value in values:
        path = Path(value).expanduser().resolve()
        if not path.exists():
            raise FlowError(f"preuve introuvable : {value}")
        if not path.is_file() or not path.stat().st_size:
            raise FlowError(f"preuve attendue : fichier non vide : {value}")
        resolved.append(str(path))
    return resolved


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:80] or "odoo-flow"


def new_state(project: Path, kind: str, run_id: str, graph_path: Path) -> dict[str, Any]:
    state = {
        "schema_version": 1,
        "run_id": run_id,
        "project": str(project.resolve()),
        "kind": kind,
        "graph": str(graph_path.resolve()),
        "graph_sha256": graph_hash(graph_path),
        "graph_snapshot": load_json(graph_path),
        "created_at": now(),
        "updated_at": now(),
        "status": "active",
        "start_pending": True,
        "tokens": {},
        "node_counts": {},
        "outcome_counts": {},
        "claims": {},
        "events": [],
    }

    resources = project / '.odoo-agents/resources.json'
    if resources.is_file():
        config = load_json(resources)
        if config.get('schema') != 1 or not isinstance(config.get('bindings'), dict):
            raise FlowError('configuration de ressources invalide')
        old = load_registry(project / '.odoo-agents/flows/resource-locks.json')
        prune_registry(old)
        if old['claims']:
            raise FlowError('libérer les anciennes revendications locales avant activation du registre partagé')
        state['resource_registry'] = str(Path(config.get('registry', str(Path.home() / '.cache/odoo-agents/resource-locks.json'))).expanduser().resolve())
        state['resource_bindings'] = config['bindings']
        for binding in config['bindings'].values():
            canonical_resource(binding['id'])
            for parent in binding.get('parents', []):
                canonical_resource(parent)
    return state


def consume_ready_token(state: dict[str, Any], graph: dict[str, Any], node_name: str) -> None:
    if node_name == graph["start"] and state.get("start_pending"):
        state["start_pending"] = False
        return
    incoming = incoming_edges(graph, node_name)
    if graph["nodes"][node_name].get("join", "any") == "all":
        for edge in incoming:
            state["tokens"][edge["id"]] -= 1
        return
    for edge in sorted(incoming, key=lambda item: item["id"]):
        if state["tokens"].get(edge["id"], 0) > 0:
            state["tokens"][edge["id"]] -= 1
            return
    raise FlowError(f"aucun jeton consommable pour {node_name}")


def complete_node(
    state: dict[str, Any],
    graph: dict[str, Any],
    node_name: str,
    outcome: str,
    evidence: list[str],
    note: str | None = None,
) -> None:
    if node_name not in graph["nodes"]:
        raise FlowError(f"nœud inconnu : {node_name}")
    if node_name not in ready_nodes(state, graph):
        raise FlowError(f"nœud non prêt : {node_name}")
    node = graph["nodes"][node_name]
    if state.get('plan_task', {}).get('risk') == 'high' and outcome == 'module':
        raise FlowError('risque élevé du plan : transition module_high_risk obligatoire')
    outcomes = node_outcomes(graph, node_name)
    if outcome not in outcomes:
        raise FlowError(
            f"issue invalide pour {node_name}: {outcome}; attendue parmi {', '.join(outcomes)}"
        )
    if node_name == graph["start"] and outcome != state["kind"]:
        raise FlowError(
            f"le run a été ouvert pour {state['kind']}; le briefing ne peut pas émettre {outcome}"
        )
    if node.get("evidence") and not evidence:
        raise FlowError(f"{node_name}: au moins une preuve --evidence est requise")
    outcome_key = f"{node_name}:{outcome}"
    outcome_count = state["outcome_counts"].get(outcome_key, 0)
    maximum = node.get("max_outcome_uses", {}).get(outcome)
    if maximum is not None and outcome_count >= maximum:
        raise FlowError(
            f"{node_name}:{outcome} a atteint sa limite de {maximum}; "
            "choisissez une issue d'arrêt réelle"
        )

    consume_ready_token(state, graph, node_name)
    state["node_counts"][node_name] = state["node_counts"].get(node_name, 0) + 1
    state["outcome_counts"][outcome_key] = outcome_count + 1
    emitted: list[str] = []
    for edge in graph["edges"]:
        if edge["from"] == node_name and edge["outcome"] == outcome:
            state["tokens"][edge["id"]] = state["tokens"].get(edge["id"], 0) + 1
            emitted.append(edge["to"])
    state["events"].append(
        {
            "at": now(),
            "node": node_name,
            "outcome": outcome,
            "evidence": evidence,
            "note": note or "",
            "emitted": emitted,
        }
    )
    terminal = node.get("terminal")
    if terminal:
        state["status"] = terminal


def state_summary(state: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    ready = ready_nodes(state, graph)
    running = sorted(state.get("claims", {}))
    if state["status"] == "active" and running:
        status = "running"
    elif state["status"] == "active" and ready:
        executors = {graph["nodes"][name]["executor"] for name in ready}
        status = "waiting_human" if executors == {"human"} else "active"
    elif state["status"] == "active":
        status = "deadlocked"
    else:
        status = state["status"]
    return {
        "run_id": state["run_id"],
        "project": state["project"],
        "kind": state["kind"],
        "status": status,
        "ready": ready,
        "parallel_waves": parallel_waves(graph, ready, state),
        "running": running,
        "completed_events": len(state["events"]),
    }


def render_mermaid(graph: dict[str, Any]) -> str:
    lines = ["flowchart TD"]
    for name, node in graph["nodes"].items():
        label = node["description"].replace('"', "'")
        if node.get("terminal"):
            lines.append(f'    {name}(["{label}"])')
        elif node.get("executor") == "human":
            lines.append(f'    {name}{{"{label}"}}')
        else:
            lines.append(f'    {name}["{label}"]')
    for edge in graph["edges"]:
        lines.append(
            f"    {edge['from']} -->|{edge['outcome']}| {edge['to']}"
        )
    return "\n".join(lines)


def prune_registry(registry: dict[str, Any]) -> None:
    """Retire les revendications dont l'état ne confirme plus l'exécution."""
    kept = []
    for claim in registry["claims"]:
        state_path = Path(claim.get("state", ""))
        try:
            other_state = load_json(state_path)
        except FlowError:
            continue
        current = other_state.get("claims", {}).get(claim.get("node"))
        if current and current.get("owner") == claim.get("owner"):
            kept.append(claim)
    registry["claims"] = kept


def claim_node(state_path: Path, graph_path: Path, node_name: str, owner: str) -> None:
    with exclusive_lock(state_path):
        state, graph = load_state(state_path, graph_path)
        if node_name not in graph["nodes"]:
            raise FlowError(f"nœud inconnu : {node_name}")
        if graph["nodes"][node_name]["executor"] == "human":
            raise FlowError(f"une porte humaine ne se revendique pas : {node_name}")
        if node_name not in ready_nodes(state, graph):
            raise FlowError(f"nœud non prêt ou déjà revendiqué : {node_name}")
        claim = {
            "at": now(),
            "locks": resolve_locks(graph["nodes"][node_name], state),
            "node": node_name,
            "owner": owner,
            "state": str(state_path),
        }
        lock_registry = registry_path(state)
        with exclusive_lock(lock_registry):
            registry = load_registry(lock_registry)
            prune_registry(registry)
            for existing in registry["claims"]:
                if not locks_compatible(claim["locks"], existing.get("locks", [])):
                    raise FlowError(
                        f"verrou incompatible avec {existing.get('node')} "
                        f"du run {Path(existing.get('state', '')).stem}"
                    )
            registry["claims"].append(claim)
            write_registry(lock_registry, registry)
            state.setdefault("claims", {})[node_name] = claim
            write_state(state_path, state)


def validate_migration(state: dict[str, Any], new_graph: dict[str, Any]) -> None:
    old = state.get("graph_snapshot")
    if not old:
        raise FlowError("ancien graphe absent : fournir --from-graph correspondant à l'empreinte du run")
    active = {edge_id for edge_id, count in state.get("tokens", {}).items() if count}
    executed = {event["node"] for event in state.get("events", [])}
    old_edges = {edge['id']: edge for edge in old['edges']}
    new_edges = {edge['id']: edge for edge in new_graph['edges']}
    pending = {old_edges[e]['to'] for e in active if e in old_edges}
    if state.get('start_pending'):
        pending.add(old['start'])
        if old['start'] != new_graph['start']:
            raise FlowError('point de départ modifié pendant un run')
    for node in executed | pending:
        if old['nodes'].get(node) != new_graph['nodes'].get(node):
            raise FlowError('sémantique de nœud active ou historique modifiée : ' + node)
    relevant_old = {k: e for k, e in old_edges.items() if k in active or e['from'] in executed or e['to'] in pending}
    relevant_new = {k: e for k, e in new_edges.items() if k in active or e['from'] in executed or e['to'] in pending}
    if relevant_old != relevant_new:
        raise FlowError('transitions actives ou historiques modifiées : migration refusée')


def release_claim(
    state_path: Path, graph_path: Path, node_name: str, owner: str, reason: str
) -> None:
    with exclusive_lock(state_path):
        state = load_json(state_path)  # libérer ne consomme aucun jeton du graphe
        claim = state.get("claims", {}).get(node_name)
        if not claim or claim.get("owner") != owner:
            raise FlowError(f"revendication absente pour {node_name} et {owner}")
        lock_registry = registry_path(state)
        with exclusive_lock(lock_registry):
            registry = load_registry(lock_registry)
            state["claims"].pop(node_name)
            state.setdefault("claim_events", []).append(
                {"at": now(), "action": "release", "node": node_name, "owner": owner, "reason": reason}
            )
            write_state(state_path, state)
            registry["claims"] = [
                item
                for item in registry["claims"]
                if not (
                    item.get("state") == str(state_path)
                    and item.get("node") == node_name
                    and item.get("owner") == owner
                )
            ]
            write_registry(lock_registry, registry)


def bind_criteria(state_path, graph_path, source, output, owner):
    from odoo_coverage import contract, draft, GATES
    with exclusive_lock(state_path):
        state, graph = load_state(state_path, graph_path)
        # À la jointure, son propriétaire lie le contrat ; avant les voies,
        # l'orchestrateur le fait sans revendication concurrente.
        claims = state.get('claims', {})
        if state['status'] != 'active' or any(c['owner'] != owner for c in claims.values()):
            raise FlowError('liaison impossible : flow terminé ou revendications d’un autre propriétaire')
        if any(e['node'] in GATES and e['outcome'] == 'pass' for e in state['events']):
            raise FlowError('liaison impossible après réception QA')
        try:
            pinned = contract(state['project'], str(source))
            if state.get('qa_contract') and state['qa_contract'] != pinned:
                raise ValueError('contrat déjà lié : aucun remplacement implicite ; ouvrir un nouveau flow pour un contrat révisé')
            root = Path(state['project']).resolve()
            target = output.resolve()
            if not target.is_relative_to(root) or target.exists() or target.is_symlink():
                raise ValueError('nouveau fichier de couverture requis dans le projet')
            # Ne pas écraser la spec, le flow ou une preuve existante.
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('x') as stream:
                json.dump(draft(pinned), stream, ensure_ascii=False, indent=2)
                stream.write('\n')
            state['qa_contract'] = pinned
            state.setdefault('qa_contract_binding', {'owner': owner, 'at': now()})
            write_state(state_path, state)
        except (ValueError, TypeError, OSError) as exc:
            raise FlowError(str(exc)) from exc
    return pinned


RECOVERY_GATE = 'reception_recovery_gate'
RECOVERY_NODES = {'reception_recovery_gate', 'memory_task_blocked'}
RECOVERY_EDGES = {'journal-memory-retry', 'journal-memory-blocked',
                  'reception-memory-pass', 'reception-memory-blocked'}


RECOVERY_EXTENSION = {'nodes': {'reception_recovery_gate': {'description': 'Recevoir à nouveau les propositions mémoire depuis '
                                                      'les bases actuelles, à contrat et preuves inchangés.',
                                       'executor': 'orchestrator',
                                       'join': 'any',
                                       'evidence': ['réception indépendante renouvelée ou motif de blocage '
                                                    'mémoire'],
                                       'max_outcome_uses': {'pass': 2},
                                       'locks': [{'resource': 'project_memory', 'mode': 'write'}]},
           'memory_task_blocked': {'description': 'Intervention arrêtée sur la réception ou la publication '
                                                  'mémoire ; la QA passée reste conservée.',
                                   'executor': 'orchestrator',
                                   'join': 'any',
                                   'terminal': 'blocked',
                                   'outcomes': ['done'],
                                   'evidence': ['motif de blocage mémoire et état de publication réel'],
                                   'locks': []}},
 'edges': [{'id': 'journal-memory-retry',
            'from': 'journal_task',
            'outcome': 'retry',
            'to': 'reception_recovery_gate'},
           {'id': 'journal-memory-blocked',
            'from': 'journal_task',
            'outcome': 'blocked',
            'to': 'memory_task_blocked'},
           {'id': 'reception-memory-pass',
            'from': 'reception_recovery_gate',
            'outcome': 'pass',
            'to': 'journal_task'},
           {'id': 'reception-memory-blocked',
            'from': 'reception_recovery_gate',
            'outcome': 'blocked',
            'to': 'memory_task_blocked'}]}


def recovery_available(graph):
    return (all(graph['nodes'].get(name) == node for name, node in RECOVERY_EXTENSION['nodes'].items())
            and [edge for edge in graph['edges'] if edge['id'] in RECOVERY_EDGES] == RECOVERY_EXTENSION['edges'])


def accepted_bundle(state, memory_policy='ignore'):
    from odoo_coverage import GATES
    from odoo_reception import check_ref, verify_bundle, verify_contract
    accepted = state.get('accepted_reception')
    if state.get('status') != 'active' or not accepted or not any(
            event['node'] in GATES and event['outcome'] == 'pass' for event in state['events']):
        raise ValueError('réception QA acceptée préalable requise')
    pins = [state.get('task_reception', {})] + state.get('task_reception_history', [])
    pinned = next((pin for pin in pins if pin.get('sha256') == accepted['bundle_sha256']), None)
    if not pinned:
        raise ValueError('dossier de réception accepté introuvable')
    root = Path(state['project']).resolve()
    check_ref(root, accepted)
    bundle = verify_bundle(root, pinned, memory_policy=memory_policy)
    verify_contract(bundle, state.get('qa_contract'))
    return pinned, bundle


def upgrade_recovery(state_path, graph_path, owner, from_graph=None):
    """Ajout connu seulement ; aucune relaxation de validate_migration."""
    import copy
    with exclusive_lock(state_path):
        state = load_json(state_path)
        graph = load_json(graph_path)
        old = state.get('graph_snapshot')
        if not owner.strip() or state.get('status') != 'active' or state.get('claims'):
            raise FlowError('migration de reprise : flow actif sans revendication requis')
        if not old or any(e['node'] == 'journal_task' for e in state['events']):
            raise FlowError('migration de reprise : snapshot requis et journal jamais exécuté')
        # L’empreinte d’origine reste vérifiable sur le fichier déclaré du run.
        original = Path(from_graph) if from_graph else Path(state.get('graph', ''))
        if (not original.is_file() or graph_hash(original) != state.get('graph_sha256')
                or load_json(original) != old):
            raise FlowError('migration de reprise : fournir le graphe original intact au chemin déclaré')
        if validate_graph(graph) or not recovery_available(graph):
            raise FlowError('sous-graphe de reprise absent ou invalide')
        stripped = copy.deepcopy(graph)
        for name in RECOVERY_NODES:
            stripped['nodes'].pop(name)
        stripped['edges'] = [edge for edge in stripped['edges'] if edge['id'] not in RECOVERY_EDGES]
        if old != stripped:
            raise FlowError('migration de reprise limitée aux seuls ajouts mémoire prévus')
        previous = state['graph_sha256']
        state.update(graph=str(graph_path), graph_sha256=graph_hash(graph_path), graph_snapshot=graph)
        state.setdefault('migrations', []).append({'at': now(), 'from': previous,
            'to': state['graph_sha256'], 'kind': 'memory-recovery', 'owner': owner})
        write_state(state_path, state)
        return state


def publish_memory(state_path, graph_path, owner):
    from odoo_reception import check_ref, publish
    with exclusive_lock(state_path):
        state, graph = load_state(state_path, graph_path)
        claim = state.get('claims', {}).get('journal_task')
        if not claim or claim.get('owner') != owner:
            raise FlowError('publication : revendication journal_task du propriétaire requise')
        lock_registry = registry_path(state)
        with exclusive_lock(lock_registry):
            registry = load_registry(lock_registry)
            if not any(item == claim for item in registry['claims']):
                raise FlowError('publication : verrou mémoire du registre absent')
            if any(item != claim and not locks_compatible(claim['locks'], item.get('locks', []))
                   for item in registry['claims']):
                raise FlowError('publication : verrou mémoire concurrent')
            try:
                pinned, _ = accepted_bundle(state)
                if pinned != state.get('task_reception'):
                    raise ValueError('nouveau dossier non encore accepté')
                review = json.loads(check_ref(Path(state['project']).resolve(), state['accepted_reception']).read_bytes())
                if review['reviewer'].strip() == owner.strip():
                    raise ValueError('relecteur identique au propriétaire de publication')
                return publish(state['project'], pinned, review)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                raise FlowError(f'publication mémoire refusée : {exc}') from exc


def prepare_reception(state_path, graph_path, sources, spec, evidence, memories, scopes, output, owner):
    from odoo_coverage import GATES, digest
    from odoo_reception import prepare, verify_contract
    with exclusive_lock(state_path):
        state, graph = load_state(state_path, graph_path)
        if state.get('plan_task') and not recovery_available(graph):
            raise FlowError('tâches planifiées : graphe avec reprise mémoire requis')
        if state['status'] != 'active' or any(c['owner'] != owner for c in state.get('claims', {}).values()):
            raise FlowError('réception impossible : flow terminé ou revendications d’un autre propriétaire')
        recovering = any(e['node'] in GATES and e['outcome'] == 'pass' for e in state['events'])
        if recovering and (not recovery_available(graph) or
                           state.get('claims', {}).get(RECOVERY_GATE, {}).get('owner') != owner):
            raise FlowError('préparation après QA : revendiquez reception_recovery_gate')
        try:
            root = Path(state['project']).resolve()
            bundle = prepare(root, sources, spec, evidence, memories, scopes, owner)
            verify_contract(bundle, state.get('qa_contract'))
            if recovering:
                _, previous = accepted_bundle(state)
                if any(bundle[key] != previous[key] for key in ('groups', 'scopes', 'code')):
                    raise ValueError('reprise mémoire : sources, spécification, preuves et code doivent rester identiques')
            target = (root / output).resolve()
            if not target.is_relative_to(root) or target.exists() or target.is_symlink():
                raise ValueError('nouveau fichier de dossier requis dans le projet')
            if str(target.relative_to(root)) in {row['target'] for row in bundle['memory']}:
                raise ValueError('sortie distincte des cibles mémoire requise')
            if any(target == (root / scope).resolve() or target.is_relative_to((root / scope).resolve()) for scope in scopes):
                raise ValueError('dossier hors périmètre de code requis')
            bases = []
            for row in bundle['memory']:
                if row['before_sha256'] is not None:
                    base = target.with_name(target.name + '.' + Path(row['target']).name + '.base')
                    if base.exists() or base.is_symlink():
                        raise ValueError('nouveau fichier de base mémoire requis : ' + str(base))
                    content = (root / row['target']).read_bytes()
                    if digest(content) != row['before_sha256']:
                        raise ValueError('mémoire changée pendant préparation : ' + row['target'])
                    bases.append((row, base, content))
            target.parent.mkdir(parents=True, exist_ok=True)
            for row, base, content in bases:
                with base.open('xb') as stream:
                    stream.write(content)
                row['base'] = {'path': str(base.relative_to(root)), 'sha256': digest(content)}
            with target.open('x', encoding='utf-8') as stream:
                json.dump(bundle, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
            receipt = {'path': str(target.relative_to(root)), 'sha256': digest(target.read_bytes()),
                       'owner': owner, 'at': now()}
            if state.get('task_reception'):
                state.setdefault('task_reception_history', []).append(state['task_reception'])
            state['task_reception'] = receipt
            write_state(state_path, state)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            raise FlowError(f'préparation de réception refusée : {exc}') from exc
    return receipt


def verify_task_reception(state, checked_evidence, node_name, outcome, owner):
    from odoo_coverage import GATES, digest, project_file
    from odoo_reception import FORMAT, check_ref, verify, verify_contract
    pinned = state.get('task_reception')
    recovery_exit = node_name == 'journal_task' and outcome in {'retry', 'blocked'}
    if not pinned and (recovery_exit or node_name == RECOVERY_GATE):
        raise FlowError('reprise mémoire réservée aux tâches avec réception liée')
    if not pinned:
        return None
    try:
        if recovery_exit and outcome == 'retry' and state['outcome_counts'].get('journal_task:retry', 0) >= 2:
            raise ValueError('deux reprises mémoire déjà ouvertes ; choisir blocked')
        if recovery_exit or node_name == RECOVERY_GATE:
            if outcome == 'blocked':
                # Une preuve devenue périmée doit encore permettre l’arrêt réel.
                if not state.get('accepted_reception'):
                    raise ValueError('réception QA acceptée préalable requise')
            else:
                accepted_bundle(state)
        if node_name in GATES | {RECOVERY_GATE} and outcome == 'pass':
            if node_name == RECOVERY_GATE and pinned['sha256'] == state['accepted_reception']['bundle_sha256']:
                raise ValueError('nouveau dossier de réception requis pour la reprise')
            reviews = []
            for value in checked_evidence:
                try:
                    data = json.loads(Path(value).read_bytes())
                except (ValueError, UnicodeError):
                    continue
                if isinstance(data, dict) and data.get('format') == FORMAT:
                    reviews.append((value, data))
            if len(reviews) != 1:
                raise ValueError('une réception odoo-task-reception/1 est requise pour pass')
            value, review = reviews[0]
            path = project_file(state['project'], value)
            bundle = verify(review, pinned, state['project'])
            verify_contract(bundle, state.get('qa_contract'))
            if review['reviewer'].strip() == owner.strip():
                raise ValueError('réception indépendante requise : reviewer identique au propriétaire actuel de complétion')
            return {'path': str(path.relative_to(Path(state['project']).resolve())),
                    'sha256': digest(path.read_bytes()), 'bundle_sha256': pinned['sha256'],
                    'node': node_name, 'at': now()}
        if node_name == 'journal_task' and outcome == 'done':
            accepted = state.get('accepted_reception')
            # Les chemins sans jointure QA restent compatibles (réponse fonctionnelle, etc.).
            passed = any(e['node'] in GATES and e['outcome'] == 'pass' for e in state['events'])
            if not passed:
                return None
            if not accepted or accepted['bundle_sha256'] != pinned['sha256']:
                raise ValueError('réception QA acceptée absente')
            path = check_ref(Path(state['project']).resolve(), accepted)
            bundle = verify(json.loads(path.read_bytes()), pinned, state['project'], published=True)
            verify_contract(bundle, state.get('qa_contract'))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise FlowError(f'réception de tâche refusée : {exc}') from exc
    return None


def qa_report(state_path, graph_path, node_name, coverage_path, output, outcome, owner):
    from odoo_coverage import GATES, digest, project_file, render_report
    with exclusive_lock(state_path):
        state, graph = load_state(state_path, graph_path)
        claim = state.get('claims', {}).get(node_name)
        if node_name not in GATES or not claim or claim.get('owner') != owner:
            raise FlowError('rapport QA : revendiquez la jointure avec ce propriétaire')
        if not state.get('qa_contract') or outcome not in node_outcomes(graph, node_name):
            raise FlowError('rapport QA : contrat lié et issue de jointure requis')
        try:
            root = Path(state['project']).resolve()
            source = project_file(root, coverage_path)
            proof = json.loads(source.read_bytes())
            rendered = render_report(proof, state['qa_contract'], root, outcome)
            target = output.resolve()
            if not target.is_relative_to(root) or target.exists() or target.is_symlink():
                raise ValueError('nouveau fichier de rapport requis dans le projet')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('x', encoding='utf-8') as stream:
                stream.write(rendered)
            receipt = {'path': str(target), 'sha256': digest(target.read_bytes()),
                       'coverage_path': str(source), 'coverage_sha256': digest(source.read_bytes()),
                       'contract_sha256': state['qa_contract']['sha256'],
                       'node': node_name, 'outcome': outcome, 'owner': owner, 'at': now()}
            state.setdefault('qa_reports', []).append(receipt)
            write_state(state_path, state)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            raise FlowError(f'rapport QA refusé : {exc}') from exc
    return receipt


def verify_used_qa_reports(state, checked_evidence, node_name, outcome, owner):
    from odoo_coverage import digest, project_file, render_report
    for receipt in state.get('qa_reports', []):
        if receipt['path'] not in checked_evidence:
            continue
        try:
            if (receipt['node'], receipt['outcome'], receipt['owner']) != (node_name, outcome, owner):
                raise ValueError('rapport lié à une autre jointure, issue ou propriétaire')
            report = project_file(state['project'], receipt['path'])
            coverage_path = project_file(state['project'], receipt['coverage_path'])
            if digest(report.read_bytes()) != receipt['sha256'] or digest(coverage_path.read_bytes()) != receipt['coverage_sha256']:
                raise ValueError('rapport ou couverture modifié depuis le rendu')
            if receipt['contract_sha256'] != state['qa_contract']['sha256']:
                raise ValueError('contrat différent de celui du rapport')
            expected = render_report(json.loads(coverage_path.read_bytes()), state['qa_contract'], state['project'], outcome)
            if report.read_text() != expected:
                raise ValueError('rapport différent du rendu de la couverture')
        except (ValueError, KeyError, TypeError, OSError) as exc:
            raise FlowError(f'rapport QA refusé : {exc}') from exc


def complete_claimed_node(
    state_path: Path,
    graph_path: Path,
    node_name: str,
    outcome: str,
    evidence: list[str],
    note: str | None,
    owner: str,
    human_confirmed: bool,
) -> dict[str, Any]:
    with exclusive_lock(state_path):
        state, graph = load_state(state_path, graph_path)
        if node_name not in graph["nodes"]:
            raise FlowError(f"nœud inconnu : {node_name}")
        node = graph["nodes"][node_name]
        checked_evidence = evidence_files(evidence)
        verify_used_qa_reports(state, checked_evidence, node_name, outcome, owner)
        from odoo_coverage import FORMAT, GATES, verify as verify_coverage
        if state.get('qa_contract') and node_name in GATES and outcome == 'pass':
            try:
                coverages = []
                for value in checked_evidence:
                    if Path(value).suffix == '.json':
                        proof = json.loads(Path(value).read_text())
                        if isinstance(proof, dict) and proof.get('format') == FORMAT:
                            coverages.append(proof)
                if len(coverages) != 1:
                    raise ValueError('une preuve odoo-qa-coverage/1 est requise pour pass')
                verify_coverage(coverages[0], state['qa_contract'], state['project'])
            except (ValueError, KeyError, TypeError, OSError) as exc:
                raise FlowError(f'couverture QA refusée : {exc}') from exc
        accepted_reception = verify_task_reception(state, checked_evidence, node_name, outcome, owner)
        from odoo_evidence import verify as verify_evidence
        for value in checked_evidence:
            if Path(value).suffix == '.json':
                try:
                    proof = json.loads(Path(value).read_text())
                    if isinstance(proof, dict) and proof.get('format') == 'odoo-evidence/1':
                        verify_evidence(proof, state['project'], require_success=outcome not in
                                        {'fail', 'failed', 'red', 'retry', 'blocked', 'exhausted'})
                except (ValueError, KeyError, OSError) as exc:
                    raise FlowError(f"preuve JSON invalide : {value} : {exc}") from exc
        evidence_digests = {value: graph_hash(Path(value)) for value in checked_evidence}
        is_human = node["executor"] == "human"
        if is_human and not human_confirmed:
            raise FlowError(
                f"{node_name}: --human-confirmed est requis avec une décision écrite"
            )
        if not is_human:
            claim = state.get("claims", {}).get(node_name)
            if not claim or claim.get("owner") != owner:
                raise FlowError(
                    f"{node_name}: revendiquez d'abord le nœud avec --owner {owner}"
                )
            state["claims"].pop(node_name)
        try:
            complete_node(state, graph, node_name, outcome, checked_evidence, note)
            state["events"][-1]["evidence_sha256"] = evidence_digests
            if accepted_reception:
                if state.get("accepted_reception"):
                    state.setdefault("accepted_reception_history", []).append(state["accepted_reception"])
                state["accepted_reception"] = accepted_reception
        except Exception:
            if not is_human:
                state["claims"][node_name] = claim
            raise
        if is_human:
            write_state(state_path, state)
            return state

        lock_registry = registry_path(state)
        with exclusive_lock(lock_registry):
            registry = load_registry(lock_registry)
            write_state(state_path, state)
            registry["claims"] = [
                item
                for item in registry["claims"]
                if not (
                    item.get("state") == str(state_path)
                    and item.get("node") == node_name
                    and item.get("owner") == owner
                )
            ]
            write_registry(lock_registry, registry)
        return state


STATUS_LABELS = {
    "active": "PRÊT",
    "running": "EN COURS",
    "waiting_human": "ATTENTE HUMAINE",
    "deadlocked": "BLOQUÉ — AUCUN NŒUD PRÊT",
    "complete": "TERMINÉ",
    "blocked": "ARRÊTÉ",
    "cancelled": "ANNULÉ",
}

EXECUTOR_LABELS = {
    "agent": "AGENT",
    "human": "HUMAIN",
    "orchestrator": "ORCHESTRATEUR",
}


def actor_label(node: dict[str, Any]) -> str:
    label = EXECUTOR_LABELS.get(node["executor"], node["executor"].upper())
    if node.get("role"):
        label += f" · {node['role']}"
    if node.get("mode"):
        label += f" · {node['mode']}"
    return label


def format_dashboard(
    state: dict[str, Any], graph: dict[str, Any], show_history: bool = False
) -> str:
    """Rend un état lisible dans les terminaux Claude Code et Codex."""
    summary = state_summary(state, graph)
    events = state.get("events", [])
    claims = state.get("claims", {})
    ready_agents = sum(
        graph["nodes"][name]["executor"] == "agent" for name in summary["ready"]
    )
    claimed_agent_nodes = sum(
        graph["nodes"][name]["executor"] == "agent" for name in summary["running"]
    )
    lines = [
        f"ODOO FLOW · {summary['run_id']}",
        "─" * 72,
        f"État       {STATUS_LABELS.get(summary['status'], summary['status'].upper())}",
        f"Flux       {summary['kind']}",
        f"Projet     {summary['project']}",
        f"Progression {summary['completed_events']} étape(s) franchie(s)",
        f"Nœuds agent {claimed_agent_nodes} revendiqué(s) · {ready_agents} prêt(s)",
    ]
    if state.get('qa_contract'):
        lines.append(f"Contrat QA {len(state['qa_contract']['criteria'])} critères liés · couverture exigée pour pass")
    if events:
        last = events[-1]
        lines.append(f"Dernière   ✓ {last['node']} → {last['outcome']}")

    lines.extend(["", "POSITION DANS LE GRAPHE"])
    if summary["running"]:
        lines.append("  EN COURS")
        for name in summary["running"]:
            node = graph["nodes"][name]
            claim = claims[name]
            lines.extend(
                [
                    f"  ▶ {name}",
                    f"    {actor_label(node)} · propriétaire: {claim['owner']}",
                    f"    {node['description']}",
                ]
            )

    for index, wave in enumerate(summary["parallel_waves"], start=1):
        parallel = len(wave) > 1
        if parallel:
            lines.append(f"  VAGUE {index} · PARALLÈLE · {len(wave)} nœuds")
        elif len(summary["parallel_waves"]) > 1:
            lines.append(f"  VAGUE {index} · SÉQUENTIELLE")
        else:
            lines.append("  PROCHAINE ÉTAPE")
        for name in wave:
            node = graph["nodes"][name]
            evidence = ", ".join(node.get("evidence", [])) or "aucune"
            outcomes = ", ".join(node_outcomes(graph, name)) or "fin"
            availability = claimability(state, graph, name)
            if availability['blockers']:
                lines.append('    ATTENTE RESSOURCE : ' + ', '.join(str(b['owner']) + ' / ' + str(b['node']) for b in availability['blockers']))
            marker = "◆" if node["executor"] == "human" else "○"
            lines.extend(
                [
                    f"  {marker} {name}",
                    f"    {actor_label(node)}",
                    f"    {node['description']}",
                    f"    Sorties: {outcomes} · Preuve: {evidence}",
                ]
            )

    if not summary["running"] and not summary["ready"]:
        lines.append("  Aucun nœud actif.")

    if show_history and events:
        lines.extend(["", "HISTORIQUE RÉCENT"])
        for event in events[-5:]:
            lines.append(f"  ✓ {event['node']} → {event['outcome']}")
    return "\n".join(lines)


def claimability(state, graph, node_name):
    """Disponibilité observée ; claim reste l'opération atomique qui fait foi."""
    node = graph['nodes'][node_name]
    if node['executor'] == 'human':
        return {'claimable': False, 'reason': 'attente humaine', 'blockers': []}
    registry = load_registry(registry_path(state))
    prune_registry(registry)
    wanted = resolve_locks(node, state)
    blockers = [{'node': c.get('node'), 'owner': c.get('owner'), 'state': c.get('state'), 'locks': c.get('locks', [])}
                for c in registry['claims'] if not locks_compatible(wanted, c.get('locks', []))]
    return {'claimable': not blockers, 'reason': 'ressource occupée' if blockers else 'revendicable', 'blockers': blockers}


def print_ready(
    state: dict[str, Any],
    graph: dict[str, Any],
    as_json: bool,
    show_history: bool = False,
) -> None:
    summary = state_summary(state, graph)
    if as_json:
        payload = dict(summary)
        payload["nodes"] = {
            name: {
                "description": graph["nodes"][name]["description"],
                "executor": graph["nodes"][name]["executor"],
                "role": graph["nodes"][name].get("role"),
                "mode": graph["nodes"][name].get("mode"),
                "outcomes": node_outcomes(graph, name),
                "evidence": graph["nodes"][name].get("evidence", []),
                "locks": graph["nodes"][name].get("locks", []),
                **claimability(state, graph, name),
            }
            for name in summary["ready"]
        }
        payload["running_nodes"] = {
            name: {
                "description": graph["nodes"][name]["description"],
                "executor": graph["nodes"][name]["executor"],
                "role": graph["nodes"][name].get("role"),
                "mode": graph["nodes"][name].get("mode"),
                "owner": state["claims"][name]["owner"],
                "claimed_at": state["claims"][name]["at"],
                "locks": state["claims"][name].get("locks", []),
            }
            for name in summary["running"]
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(format_dashboard(state, graph, show_history))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="valider la définition")
    validate.add_argument("--json", action="store_true")

    analyze = subparsers.add_parser("analyze", help="mesurer la structure")
    analyze.add_argument("--json", action="store_true")

    render = subparsers.add_parser("render", help="rendre le graphe")
    render.add_argument("--format", choices=["mermaid"], default="mermaid")

    start = subparsers.add_parser("start", help="ouvrir un état persistant")
    start.add_argument("project", type=Path)
    start.add_argument("--kind", choices=sorted(KINDS), required=True)
    start.add_argument("--id")

    for command in ("ready", "status"):
        action = subparsers.add_parser(command, help=f"afficher {command}")
        action.add_argument("state", type=Path)
        action.add_argument("--json", action="store_true")

    complete = subparsers.add_parser("complete", help="terminer un nœud prêt")
    complete.add_argument("state", type=Path)
    complete.add_argument("node")
    complete.add_argument("--outcome", required=True)
    complete.add_argument("--evidence", action="append", default=[])
    complete.add_argument("--note")
    complete.add_argument("--owner", default="orchestrator")
    complete.add_argument("--human-confirmed", action="store_true")

    binding = subparsers.add_parser('bind-criteria', help='lier un contrat QA et générer sa couverture manquante')
    binding.add_argument('state', type=Path)
    binding.add_argument('--source', type=Path, required=True)
    binding.add_argument('--output', type=Path, required=True)
    binding.add_argument('--owner', required=True)

    for name, help_text in [('publish-memory', 'publier les deux drafts approuvés de façon reprenable'),
                            ('upgrade-recovery', 'ajouter explicitement la reprise mémoire à un ancien run')]:
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument('state', type=Path)
        command.add_argument('--owner', required=True)
        if name == 'upgrade-recovery':
            command.add_argument('--from-graph', type=Path)
    reception = subparsers.add_parser('prepare-reception', help='figer le dossier de réception et la mémoire proposée')
    reception.add_argument('state', type=Path)
    reception.add_argument('--source', action='append', required=True)
    reception.add_argument('--spec', required=True)
    reception.add_argument('--evidence', action='append', required=True)
    reception.add_argument('--memory', action='append', required=True)
    reception.add_argument('--scope', action='append', default=[])
    reception.add_argument('--output', type=Path, required=True)
    reception.add_argument('--owner', required=True)

    report = subparsers.add_parser('qa-report', help='rendre un rapport QA lié à sa couverture et à son issue')
    report.add_argument('state', type=Path)
    report.add_argument('node')
    report.add_argument('--coverage', type=Path, required=True)
    report.add_argument('--output', type=Path, required=True)
    report.add_argument('--outcome', choices=['pass', 'retry', 'blocked'], required=True)
    report.add_argument('--owner', required=True)

    claim = subparsers.add_parser("claim", help="revendiquer un nœud et ses verrous")
    claim.add_argument("state", type=Path)
    claim.add_argument("node")
    claim.add_argument("--owner", default="orchestrator")

    release = subparsers.add_parser("release", help="libérer un nœud sans le terminer")
    release.add_argument("state", type=Path)
    release.add_argument("node")
    release.add_argument("--owner", default="orchestrator")
    release.add_argument("--reason", required=True)

    migrate = subparsers.add_parser(
        "migrate", help="rattacher explicitement un run à une nouvelle version compatible du graphe"
    )
    migrate.add_argument("state", type=Path)
    migrate.add_argument("--from-graph", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    graph_path = args.graph.resolve()
    try:
        if args.command == "release":
            release_claim(args.state.resolve(), graph_path, args.node, args.owner, args.reason)
            print(f"■ {args.node} · verrou libéré par {args.owner}")
            return 0
        graph = load_json(graph_path)
        errors = validate_graph(graph)
        if args.command == "validate":
            if args.json:
                print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
            elif errors:
                print("Graphe invalide :", file=sys.stderr)
                for error in errors:
                    print(f"- {error}", file=sys.stderr)
            else:
                analysis = analyze_graph(graph)
                print(
                    f"Graphe valide : {analysis['nodes']} nœuds, {analysis['edges']} arêtes, "
                    f"{len(analysis['forks'])} forks, {len(analysis['joins'])} jointures, "
                    f"{len(analysis['cycles'])} cycles bornés."
                )
            return 1 if errors else 0
        if errors:
            raise FlowError("graphe invalide :\n- " + "\n- ".join(errors))
        if args.command == "analyze":
            analysis = analyze_graph(graph)
            if args.json:
                print(json.dumps(analysis, ensure_ascii=False, indent=2))
            else:
                print(f"{analysis['name']} : {analysis['nodes']} nœuds, {analysis['edges']} arêtes")
                print(f"nœuds agents : {analysis['agent_nodes']}")
                print(f"portes humaines : {', '.join(analysis['human_gates'])}")
                print(f"forks : {len(analysis['forks'])} · jointures : {len(analysis['joins'])}")
                print(f"cycles bornés : {len(analysis['cycles'])}")
                print(f"parallélisme déclaré maximal : {analysis['max_declared_parallelism']}")
                print(f"terminaux : {', '.join(analysis['terminals'])}")
            return 0
        if args.command == "render":
            print(render_mermaid(graph))
            return 0
        if args.command == "start":
            project = args.project.resolve()
            if not project.is_dir():
                raise FlowError(f"projet introuvable : {project}")
            run_id = slugify(args.id or f"{datetime.now():%Y%m%d-%H%M%S}-{args.kind}")
            ensure_local_flow_dirs(project)
            path = project / ".odoo-agents" / "flows" / f"{run_id}.json"
            with exclusive_lock(path):
                if path.exists():
                    raise FlowError(f"un run existe déjà : {path}")
                state = new_state(project, args.kind, run_id, graph_path)
                write_state(path, state)
            print(path)
            return 0

        if args.command == "migrate":
            state_path = args.state.resolve()
            with exclusive_lock(state_path):
                state = load_json(state_path)
                if state.get("claims"):
                    raise FlowError("libérez les nœuds en cours avant de migrer ce run")
                if args.from_graph:
                    if graph_hash(args.from_graph) != state.get('graph_sha256'):
                        raise FlowError('ancien graphe différent de celui du run')
                    state['graph_snapshot'] = load_json(args.from_graph)
                validate_migration(state, graph)
                known_nodes = set(graph["nodes"])
                known_edges = {edge["id"] for edge in graph["edges"]}
                for event in state.get("events", []):
                    node = event.get("node")
                    outcome = event.get("outcome")
                    if node not in known_nodes or outcome not in node_outcomes(graph, node):
                        raise FlowError(
                            f"historique incompatible au nœud {node!r}, issue {outcome!r}"
                        )
                active_unknown = [
                    edge_id
                    for edge_id, count in state.get("tokens", {}).items()
                    if count and edge_id not in known_edges
                ]
                if active_unknown:
                    raise FlowError(
                        "jetons actifs sur des arêtes supprimées : "
                        + ", ".join(active_unknown)
                    )
                previous = state.get("graph_sha256", "")
                state["graph"] = str(graph_path)
                state["graph_sha256"] = graph_hash(graph_path)
                state["graph_snapshot"] = graph
                state.setdefault("migrations", []).append(
                    {"at": now(), "from": previous, "to": state["graph_sha256"]}
                )
                write_state(state_path, state)
            print(f"Run migré vers {state['graph_sha256'][:12]} : {state_path}")
            return 0

        state_path = args.state.resolve()
        if args.command == 'upgrade-recovery':
            state = upgrade_recovery(state_path, graph_path, args.owner, args.from_graph)
            print(f"Reprise mémoire ajoutée : {state['graph_sha256'][:12]} ; historique conservé.")
            return 0
        if args.command == 'publish-memory':
            for row in publish_memory(state_path, graph_path, args.owner):
                print(f"Mémoire {row['action']} : {row['target']}")
            print('Publication vérifiée ; journal_task reste revendiqué et doit être complété.')
            return 0
        if args.command == 'prepare-reception':
            receipt = prepare_reception(state_path, graph_path, args.source, args.spec, args.evidence,
                                        args.memory, args.scope, args.output, args.owner)
            print(f"Dossier de réception : {receipt['path']} · {receipt['sha256'][:12]}")
            print('Réception indépendante positive requise avant pass ; publier ensuite les drafts exacts.')
            return 0
        if args.command == 'qa-report':
            receipt = qa_report(state_path, graph_path, args.node, args.coverage,
                                args.output, args.outcome, args.owner)
            print(f"Rapport QA : {receipt['path']} · issue {receipt['outcome']} · {receipt['sha256'][:12]}")
            return 0
        if args.command == 'bind-criteria':
            pinned = bind_criteria(state_path, graph_path, args.source, args.output, args.owner)
            print(f"Contrat QA lié : {len(pinned['criteria'])} critères · {pinned['sha256'][:12]}")
            print(f'Couverture à renseigner : {args.output}')
            return 0
        if args.command == "claim":
            claim_node(state_path, graph_path, args.node, args.owner)
            node = graph["nodes"][args.node]
            print(f"▶ {args.node} · {actor_label(node)}")
            print(f"  Démarré par {args.owner}")
            print(f"  {node['description']}")
            return 0
        if args.command == "release":
            release_claim(
                state_path, graph_path, args.node, args.owner, args.reason
            )
            print(f"■ {args.node} · verrou libéré par {args.owner}")
            return 0
        if args.command in {"ready", "status"}:
            with exclusive_lock(state_path):
                state, graph = load_state(state_path, graph_path)
                print_ready(
                    state,
                    graph,
                    args.json,
                    show_history=args.command == "status",
                )
            return 0
        if args.command == "complete":
            state = complete_claimed_node(
                state_path,
                graph_path,
                args.node,
                args.outcome,
                args.evidence,
                args.note,
                args.owner,
                args.human_confirmed,
            )
            graph = load_json(graph_path)
            print_ready(state, graph, False)
            return 0
    except FlowError as exc:
        print(f"ERREUR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
