#!/usr/bin/env python3
"""Laboratoire synthétique : plan, exécution isolée, progression et évaluation.

Le pilote packet-no-tools mesure des réponses sur un dossier fourni. Il ne
prétend pas exécuter le workflow Odoo ni valider du code dans une base Odoo.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "benchmarks/cases"
DIMENSIONS = ("response", "development", "qa", "client_knowledge")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as tmp:
        json.dump(value, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
    os.replace(tmp.name, path)


def cases(directory=CORPUS):
    result = {}
    for path in sorted(directory.glob("*.json")):
        case = read_json(path)
        identifier = case.get("id", "")
        if identifier != path.stem or not identifier.startswith("B") or identifier in result:
            raise ValueError(f"identifiant de cas invalide : {path.name}")
        if case.get("status") not in ("ready", "planned"):
            raise ValueError(f"statut invalide : {identifier}")
        if case["status"] == "ready":
            for field in ("prompt", "context", "role", "rubric", "mode"):
                if not case.get(field):
                    raise ValueError(f"{identifier} : champ manquant {field}")
            if case["mode"] != "packet-no-tools":
                raise ValueError(f"mode non implémenté : {identifier}")
            ids = [item["id"] for item in case["rubric"]]
            if len(ids) != len(set(ids)) or any(
                item["dimension"] not in DIMENSIONS for item in case["rubric"]
            ):
                raise ValueError(f"rubrique invalide : {identifier}")
        result[identifier] = case
    if not result:
        raise ValueError("corpus vide")
    return result


def make_packet(case, role_body):
    # Aucune rubrique de correction n'entre dans ce paquet.
    return (
        "Exercice synthétique Odoo. Mode : analyse sur dossier fourni, sans outils.\n"
        "Les consignes du rôle ci-dessous servent de référence ; les opérations réelles "
        "(fichiers, base, tests, graphe) ne sont pas disponibles dans cet exercice. "
        "Ne prétends pas les avoir exécutées. Réponds à la demande en français.\n\n"
        "## Consignes du rôle\n" + role_body + "\n\n## Dossier disponible\n"
        + case["context"] + "\n\n## Demande\n" + case["prompt"] + "\n"
    )


def create_plan(output, selected, providers, config, timeout=600):
    if not 1 <= timeout <= 600:
        raise ValueError("durée par essai : 1 à 600 secondes")
    if not selected or not providers:
        raise ValueError("au moins un cas et un fournisseur requis")
    if len(selected) != len(set(selected)) or len(providers) != len(set(providers)):
        raise ValueError("cas ou fournisseurs dupliqués")
    catalog = cases()
    for identifier in selected:
        if identifier not in catalog or catalog[identifier]["status"] != "ready":
            raise ValueError(f"cas non exécutable : {identifier}")
    for provider in providers:
        if provider not in ("codex", "claude") or not config.get(provider, {}).get("model"):
            raise ValueError(f"configuration manquante : {provider}")
        if not config[provider].get("effort"):
            raise ValueError(f"effort explicite requis : {provider}")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    run = output / (dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
    run.mkdir(mode=0o700)
    trials = []
    for identifier in selected:
        case = catalog[identifier]
        role = ROOT / "roles" / (case["role"] + ".md")
        if role.resolve().parent != (ROOT / "roles").resolve():
            raise ValueError("rôle hors du référentiel")
        packet = make_packet(case, role.read_text(encoding="utf-8"))
        for provider in providers:
            trial_id = f"{identifier}-{provider}"
            folder = run / trial_id
            folder.mkdir()
            (folder / "packet.txt").write_text(packet, encoding="utf-8")
            atomic_json(folder / "case.json", case)
            trials.append({
                "id": trial_id, "case": identifier, "provider": provider,
                "config": config[provider], "status": "pending", "mode": case["mode"],
                "packet_sha256": digest(packet.encode()),
                "packet_bytes": len(packet.encode()), "packet_words": len(packet.split()),
                "case_sha256": digest((folder / "case.json").read_bytes()),
                "role_sha256": digest(role.read_bytes()), "review": None,
            })
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    state = {
        "schema": 1, "id": run.name, "created_at": now(), "updated_at": now(),
        "revision": revision.stdout.strip() if revision.returncode == 0 else None,
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "timeout_seconds": timeout, "max_executions": len(trials),
        "status": "planned", "trials": trials,
        "limitations": ["Pilote sans outils : aucune exécution Odoo ni validation du développement.",
                        "Consignes du rôle injectées explicitement : routage natif non évalué.",
                        "Une seule répétition et efforts différents : aucun classement causal des modèles.",
                        "Effort effectif inconnu si le fournisseur ne le retourne pas."],
    }
    atomic_json(run / "state.json", state)
    report(run, state)
    return run


def provider_command(provider, config):
    if provider == "codex":
        command = ["/opt/node/bin/codex", "exec", "--ignore-user-config", "--ignore-rules",
                   "--ephemeral", "--json", "--skip-git-repo-check", "--sandbox", "read-only",
                   "--model", config["model"], "-c", "model_reasoning_effort=" + json.dumps(config["effort"]),
                   "-c", 'web_search="disabled"']
        for feature in ("shell_tool", "unified_exec", "apps", "plugins", "multi_agent", "memories",
                        "hooks", "browser_use", "computer_use", "image_generation", "view_image"):
            command.extend(["--disable", feature])
        return command + ["-"]
    return ["/opt/claude", "--print", "--safe-mode", "--restricted", "--tools", "",
            "--strict-mcp-config", "--no-session-persistence", "--output-format", "stream-json",
            "--verbose", "--model", config["model"], "--effort", config["effort"]]


def isolated_command(provider, config, workspace):
    if not shutil.which("bwrap"):
        raise ValueError("bubblewrap absent : lancement non isolé refusé")
    home = Path.home()
    auth = home / (".codex/auth.json" if provider == "codex" else ".claude/.credentials.json")
    binary = shutil.which(provider)
    if not binary or not auth.is_file():
        raise ValueError(f"{provider} : CLI ou authentification locale absente")
    command = ["bwrap", "--die-with-parent", "--unshare-pid", "--unshare-ipc", "--unshare-uts",
               "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
               "--ro-bind", "/lib64", "/lib64", "--symlink", "usr/bin", "/bin",
               "--ro-bind", "/etc", "/etc", "--proc", "/proc", "--dev", "/dev",
               "--tmpfs", "/tmp", "--tmpfs", "/run", "--dir", str(home),
               "--dir", str(auth.parent), "--ro-bind", str(auth), str(auth),
               "--ro-bind", str(workspace), "/work", "--chdir", "/work", "--dir", "/opt"]
    resolver = Path("/etc/resolv.conf").resolve()
    if str(resolver).startswith("/run/"):
        command.extend(["--ro-bind", str(resolver), str(resolver)])
    if provider == "codex":
        # L'installation npm associe CLI et node ; les autres répertoires personnels ne sont pas montés.
        node_root = Path(binary).parent.parent
        if not (node_root / "bin/node").is_file():
            raise ValueError("installation Codex non npm : adaptateur à configurer explicitement")
        command.extend(["--ro-bind", str(node_root), "/opt/node"])
    else:
        command.extend(["--ro-bind", str(Path(binary).resolve()), "/opt/claude"])
    # Le réseau est nécessaire au fournisseur ; /home, le dépôt et les corrigés ne sont pas montés.
    return command + provider_command(provider, config)


def parse_output(path, provider):
    answer = ""
    usage = None
    model = None
    provider_error = None
    completed = False
    tool_calls = 0
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if provider == "codex":
            if event.get("type") == "item.completed":
                item = event.get("item", {})
                if item.get("type") == "agent_message":
                    answer = item.get("text", "")
                elif item.get("type") in ("command_execution", "mcp_tool_call", "web_search"):
                    tool_calls += 1
            if event.get("type") == "turn.completed":
                completed = True
                usage = event.get("usage")
            if event.get("type") in ("error", "turn.failed"):
                provider_error = event.get("message") or event.get("error")
        else:
            if event.get("type") == "system" and event.get("subtype") == "init":
                model = event.get("model")
            if event.get("type") == "assistant":
                message = event.get("message", {})
                model = message.get("model") or model
                tool_calls += sum(part.get("type") == "tool_use" for part in message.get("content", []))
            if event.get("type") == "result":
                completed = event.get("subtype") == "success" and not event.get("is_error", False)
                answer = event.get("result", "")
                usage = {"tokens": event.get("usage"), "cost_usd": event.get("total_cost_usd")}
                if not completed:
                    provider_error = event.get("errors") or event.get("subtype")
    return {"answer": answer, "usage": usage, "actual_model": model,
            "actual_effort": None, "provider_error": provider_error,
            "completed_event": completed, "tool_calls": tool_calls}


def report(run, state):
    lines = [f"# Banc Odoo — {state['id']}", "", f"État : **{state['status']}**", "",
             "Exécution et qualité sont distinctes. Une grille satisfaite ne vaut pas validation générale ; une revue indépendante reste nécessaire.", "",
             "| Cas | Outil | Exécution | Secondes | Conformité à la grille |", "|---|---|---|---:|---|"]
    for trial in state["trials"]:
        review = trial.get("review")
        quality = review["verdict"] if review else "non évaluée"
        lines.append(f"| {trial['case']} | {trial['provider']} | {trial['status']} | {trial.get('seconds', '—')} | {quality} |")
    lines.extend(["", "## Configurations et mesure", "",
                  "| Essai | Modèle demandé | Effort demandé | Modèle observé |", "|---|---|---|---|"])
    for trial in state["trials"]:
        lines.append(f"| {trial['id']} | {trial['config']['model']} | {trial['config']['effort']} | {trial.get('actual_model') or 'non retourné'} |")
    lines.extend(["", "## Évaluation par dimension", "",
                  "Les fractions comptent les critères satisfaits ; elles ne constituent pas une moyenne de qualité.", "",
                  "| Essai | Réponse | Développement | QA | Connaissance client |", "|---|---|---|---|---|"])
    for trial in state["trials"]:
        dimensions = (trial.get("review") or {}).get("dimensions", {})
        values = [f"{dimensions[d]['passed']}/{dimensions[d]['total']}" if dimensions.get(d) else "non mesuré" for d in DIMENSIONS]
        lines.append("| " + trial["id"] + " | " + " | ".join(values) + " |")
    lines.extend(["", "## Réserves hors grille", ""])
    for trial in state["trials"]:
        for observation in (trial.get("review") or {}).get("observations_outside_rubric", []):
            lines.append(f"- **{trial['id']}** : {observation}")
    lines.extend(["", "## Limites", "", *[f"- {value}" for value in state["limitations"]], ""])
    (run / "report.md").write_text("\n".join(lines), encoding="utf-8")


def review_trial(run, trial_id, review):
    """Jugement externe, exhaustif et lié à la réponse effectivement observée."""
    run = Path(run)
    with (run / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("campagne en cours ; attendre avant l’évaluation") from exc
        state = read_json(run / "state.json")
        trial = next((t for t in state["trials"] if t["id"] == trial_id), None)
        if trial is None or trial["status"] != "completed":
            raise ValueError("seule une réponse terminée peut être évaluée")
        folder = run / trial_id
        answer = (folder / "answer.md").read_bytes()
        if digest(answer) != trial["answer_sha256"] or review.get("answer_sha256") != trial["answer_sha256"]:
            raise ValueError("évaluation d’une autre réponse ou réponse altérée")
        if digest((folder / "case.json").read_bytes()) != trial["case_sha256"]:
            raise ValueError("rubrique altérée")
        rubric = read_json(folder / "case.json")["rubric"]
        grades = review.get("criteria", {})
        if set(grades) != {r["id"] for r in rubric} or not review.get("reviewer"):
            raise ValueError("évaluateur et critères exhaustifs requis")
        for grade in grades.values():
            if grade.get("grade") not in ("pass", "fail", "uncertain") or not grade.get("evidence", "").strip():
                raise ValueError("chaque critère exige un jugement et une preuve")
        critical_failure = any(r.get("critical") and grades[r["id"]]["grade"] == "fail" for r in rubric)
        verdict = "rejected" if critical_failure else "accepted" if all(g["grade"] == "pass" for g in grades.values()) else "needs_review"
        dimensions = {}
        for dimension in DIMENSIONS:
            values = [grades[r["id"]]["grade"] for r in rubric if r["dimension"] == dimension]
            dimensions[dimension] = {"passed": values.count("pass"), "total": len(values)} if values else None
        trial["review"] = dict(review, verdict=verdict, dimensions=dimensions, reviewed_at=now())
        atomic_json(folder / "review.json", trial["review"])
        state["updated_at"] = now()
        atomic_json(run / "state.json", state)
        report(run, state)


def display(state):
    total = len(state["trials"])
    done = sum(t["status"] in ("completed", "error", "timeout") for t in state["trials"])
    print(f"ODOO BENCH {state['id']} · {state['status']} · {done}/{total} exécutés", flush=True)
    for trial in state["trials"]:
        config = trial["config"]
        print(f"  {trial['id']:<16} {trial['status']:<12} {config['model']} / {config['effort']}"
              f" · {trial.get('seconds', 0)} s · qualité "
              + (trial["review"]["verdict"] if trial.get("review") else "non évaluée"), flush=True)


def run_plan(run):
    run = Path(run).resolve()
    with (run / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("campagne déjà exécutée par un autre processus") from exc
        state = read_json(run / "state.json")
        # Une exécution interrompue peut avoir consommé des tokens : pas de relance automatique.
        for trial in state["trials"]:
            if trial["status"] == "running":
                trial["status"] = "interrupted"
        state["status"] = "running"
        stopping = False

        def stop(_signum, _frame):
            nonlocal stopping
            stopping = True

        previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGTERM, signal.SIGINT)}
        try:
            for trial in state["trials"]:
                if stopping or (run / "STOP").exists():
                    break
                if trial["status"] != "pending":
                    continue
                folder = run / trial["id"]
                packet = (folder / "packet.txt").read_bytes()
                if digest(packet) != trial["packet_sha256"] or digest((folder / "case.json").read_bytes()) != trial["case_sha256"]:
                    raise ValueError("paquet ou cas modifié depuis la préparation")
                trial.update(status="running", started_at=now(), seconds=0)
                atomic_json(run / "state.json", state)
                report(run, state)
                display(state)
                started = time.monotonic()
                process = None
                try:
                    with tempfile.TemporaryDirectory(prefix="odoo-bench-packet-") as work:
                        workspace = Path(work)
                        command = isolated_command(trial["provider"], trial["config"], workspace)
                        binary = shutil.which(trial["provider"])
                        version = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=10)
                        trial["cli_version"] = version.stdout.strip()
                        env = {key: value for key, value in os.environ.items() if key in
                               ("HOME", "USER", "LANG", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY",
                                "https_proxy", "http_proxy", "no_proxy")}
                        env["PATH"] = "/opt/node/bin:/usr/bin:/bin"
                        with (folder / "events.jsonl").open("wb") as out, (folder / "stderr.log").open("wb") as err:
                            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                                       env=env, start_new_session=True)
                            process.stdin.write(packet)
                            process.stdin.close()
                            heartbeat = 0
                            while process.poll() is None:
                                elapsed = time.monotonic() - started
                                if stopping or (run / "STOP").exists() or elapsed >= state["timeout_seconds"]:
                                    os.killpg(process.pid, signal.SIGTERM)
                                    try:
                                        process.wait(timeout=5)
                                    except subprocess.TimeoutExpired:
                                        os.killpg(process.pid, signal.SIGKILL)
                                        process.wait()
                                    trial["status"] = "interrupted" if stopping or (run / "STOP").exists() else "timeout"
                                    break
                                if elapsed - heartbeat >= 5:
                                    trial["seconds"] = round(elapsed, 1)
                                    state["updated_at"] = now()
                                    atomic_json(run / "state.json", state)
                                    print(f"  {trial['id']} · en cours · {elapsed:.0f} s", flush=True)
                                    heartbeat = elapsed
                                time.sleep(0.2)
                            trial["exit_code"] = process.returncode
                        result = parse_output(folder / "events.jsonl", trial["provider"])
                        answer = result.pop("answer")
                        (folder / "answer.md").write_text(answer, encoding="utf-8")
                        trial.update(result)
                        trial["answer_sha256"] = digest(answer.encode())
                        if trial["status"] == "running":
                            trial["status"] = "completed" if process.returncode == 0 and result["completed_event"] and answer.strip() and not result["tool_calls"] else "error"
                except (OSError, ValueError, subprocess.SubprocessError) as exc:
                    trial.update(status="error", error=str(exc))
                finally:
                    if process is not None and process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    trial.update(seconds=round(time.monotonic() - started, 1), ended_at=now())
                    atomic_json(run / "state.json", state)
                    report(run, state)
            if any(t["status"] in ("pending", "interrupted") for t in state["trials"]):
                state["status"] = "interrupted"
            elif any(t["status"] != "completed" for t in state["trials"]):
                state["status"] = "executed_with_errors"
            else:
                state["status"] = "executed"
            state["updated_at"] = now()
            atomic_json(run / "state.json", state)
            report(run, state)
            display(state)
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    commands.add_parser("validate")
    plan = commands.add_parser("plan")
    plan.add_argument("--cases", nargs="+", default=["B03", "B06", "B10"])
    plan.add_argument("--providers", nargs="+", choices=["codex", "claude"], default=["codex", "claude"])
    plan.add_argument("--config", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument("--timeout", type=int, default=600)
    review = commands.add_parser("review")
    review.add_argument("run", type=Path)
    review.add_argument("trial")
    review.add_argument("file", type=Path)
    for command in ("run", "status", "stop", "resume"):
        sub = commands.add_parser(command)
        sub.add_argument("run", type=Path)
    args = parser.parse_args()
    try:
        if args.command in ("list", "validate"):
            for case in cases().values():
                print(f"{case['id']} · {case['status']} · {case['title']}")
        elif args.command == "plan":
            print(create_plan(args.output, args.cases, args.providers, read_json(args.config), args.timeout))
        elif args.command == "status":
            display(read_json(args.run / "state.json"))
        elif args.command == "review":
            review_trial(args.run, args.trial, read_json(args.file))
        elif args.command == "stop":
            (args.run / "STOP").touch()
        else:
            if args.command == "resume":
                (args.run / "STOP").unlink(missing_ok=True)
            run_plan(args.run)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Erreur : {exc}\n")


if __name__ == "__main__":
    main()
