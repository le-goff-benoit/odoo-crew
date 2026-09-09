#!/usr/bin/env python3
"""Qualification synthétique 18/19 et vrai navigateur 19, trois exécutions isolées."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "benchmarks/qualification/versions"
ORM_MARKERS = {"zero", "negative_create", "negative_write", "confirmation"}


def assess(log: str, returncode: int, browser: bool, mutant: bool = False) -> dict:
    """Ne confondre ni serveur HTTP ni test skippé avec un navigateur réussi."""
    markers = set(re.findall(r"QUALIFICATION_PASS (\w+)", log))
    summaries = re.findall(r"(\d+) failed, (\d+) error\(s\) of (\d+) tests", log)
    failures = [tuple(map(int, summary)) for summary in summaries]
    required = ORM_MARKERS | ({"browser_server"} if browser else set())
    clicked = "QUALIFICATION_BROWSER_CLICK_OK" in log
    chrome = bool(re.search(r"(?:Closing|Terminating) chrome headless with pid", log))
    clean_summary = bool(failures) and all(f == e == 0 for f, e, _ in failures)
    enough_tests = any(n >= (5 if browser else 4) for _, _, n in failures)
    skip_reasons = re.findall(r"skipped Test\S+\s*:\s*(.+)", log)
    skipped = bool(skip_reasons or re.search(
        r"(?:Chrome executable not found|Chrome headless failed to start|websocket-client.*not|skipped [1-9])", log
    ))
    positive = (
        returncode == 0 and clean_summary and enough_tests and required <= markers
        and not skipped and (not browser or (clicked and chrome))
    )
    rejected_mutant = (
        returncode != 0 and any(f > 0 for f, _, _ in failures)
        and ORM_MARKERS <= markers and clicked and chrome
        and "QUALIFICATION_SERVER_STATE" in log and "browser_server" not in markers
    )
    return {
        "pass": rejected_mutant if mutant else positive,
        "expected_outcome": "reject_false_server_assertion" if mutant else "pass",
        "returncode": returncode,
        "markers": sorted(markers),
        "odoo_summaries": failures,
        "chrome_process_observed": chrome,
        "browser_click_observed": clicked,
        "server_state_confirmed": "browser_server" in markers,
        "skip_observed": skipped,
        "skip_reasons": skip_reasons,
    }


def prepare(folder: Path, series: str, mutant: bool = False) -> Path:
    if series not in {"18.0", "19.0"} or (mutant and series != "19.0"):
        raise ValueError("Série ou mutation hors du protocole")
    project = folder / "project"
    project.mkdir(parents=True)
    (project / ".odoo-agents").mkdir()
    (project / ".odoo-agents/config").write_text(f"ODOO_SERIES={series}\n")
    # Avant la première copie/écriture de code Odoo dans ce projet.
    briefing = subprocess.run(
        ["python3", str(ROOT / "scripts/odoo_briefing.py"), str(project),
         "--series", series, "--offline"], capture_output=True, text=True, check=True,
    )
    (folder / "briefing.md").write_text(briefing.stdout)
    module = project / "lab_qualification"
    shutil.copytree(FIXTURE / "common/lab_qualification", module)
    manifest = module / "__manifest__.py"
    manifest.write_text(manifest.read_text().replace("SERIES", series))
    template = module / "models.py.template"
    constraint = (
        '_sql_constraints = [("quantity_nonnegative", "CHECK(quantity >= 0)", '
        '"Quantity must be nonnegative.")]'
        if series == "18.0" else
        '_quantity_nonnegative = models.Constraint("CHECK(quantity >= 0)", '
        '"Quantity must be nonnegative.")'
    )
    (module / "models.py").write_text(template.read_text().replace("CONSTRAINT_PLACEHOLDER", constraint))
    template.unlink()
    if series == "19.0":
        browser = (FIXTURE / "test_browser.py").read_text()
        if mutant:
            browser = browser.replace(
                'self.assertEqual(record.state, "confirmed", "QUALIFICATION_SERVER_STATE")',
                'self.assertEqual(record.state, "draft", "QUALIFICATION_SERVER_STATE")',
            )
        (module / "tests/test_browser.py").write_text(browser)
        with (module / "tests/__init__.py").open("a") as stream:
            stream.write("from . import test_browser\n")
    return project


def execute(output: Path, browser_only: bool = False) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(FIXTURE / "protocol.json", output / "protocol.json")
    prefix = "qualification-versions-" + uuid.uuid4().hex[:10]
    network, postgres = prefix, prefix + "-pg"
    scenarios = (("19.0", False), ("19.0", True)) if browser_only else (("18.0", False), ("19.0", False), ("19.0", True))
    report = {"prefix": prefix, "runs": [], "images": {}, "cleanup": {}, "browser_only": browser_only}
    containers = [postgres]

    def command(args, timeout=45, check=True):
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=check)

    try:
        for tag in ("odoo-qa:18.0", "odoo-qa:19.0", "postgres:16"):
            info = json.loads(command(["docker", "image", "inspect", tag]).stdout)[0]
            report["images"][tag] = {"id": info["Id"], "digests": info.get("RepoDigests", [])}
        command(["docker", "network", "create", "--internal", network])
        command(["docker", "run", "-d", "--name", postgres, "--network", network,
                 "--tmpfs", "/var/lib/postgresql/data", "-e", "POSTGRES_USER=odoo",
                 "-e", "POSTGRES_PASSWORD=synthetic-lab-only", "postgres:16"])
        for _ in range(30):
            if command(["docker", "exec", postgres, "pg_isready", "-U", "odoo"], check=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("PostgreSQL synthétique indisponible")
        for series, mutant in scenarios:
            label = series + ("-mutant" if mutant else "-positive")
            folder = output / label
            project = prepare(folder, series, mutant)
            name = prefix + "-" + label
            containers.append(name)
            cmd = [
                "docker", "run", "--name", name, "--network", network,
                "--tmpfs", "/var/lib/odoo:mode=1777", "--shm-size", "256m",
                "--mount", f"type=bind,src={project},dst=/mnt/extra-addons,readonly",
                "--entrypoint", "odoo", f"odoo-qa:{series}",
                "--db_host", postgres, "--db_user", "odoo", "--db_password", "synthetic-lab-only",
                "-d", "qualification_" + label.replace(".", "_").replace("-", "_"),
                "--addons-path", "/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons",
                "--data-dir", "/tmp/odoo-data",
                "--without-demo=all" if series == "18.0" else "--without-demo",
                "--http-interface", "127.0.0.1", "-i", "lab_qualification",
                "--test-enable", "--test-tags", "/lab_qualification", "--stop-after-init",
                "--max-cron-threads", "0", "--workers", "0", "--log-level", "test",
            ]
            start = time.monotonic()
            timed_out = False
            with (folder / "odoo.log").open("w") as logfile:
                process = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT)
                try:
                    returncode = process.wait(timeout=360)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    command(["docker", "rm", "-f", name], check=False)
                    process.wait(timeout=30)
                    returncode = 124
            log = (folder / "odoo.log").read_text()
            result = assess(log, returncode, series == "19.0", mutant)
            result.update({"scenario": label, "seconds": round(time.monotonic() - start, 3), "timeout": timed_out})
            (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
            report["runs"].append(result)
            print(json.dumps(result), flush=True)
    finally:
        for name in reversed(containers):
            command(["docker", "rm", "-f", name], check=False)
        command(["docker", "network", "rm", network], check=False)
        remaining = command(["docker", "ps", "-a", "--filter", f"name={prefix}", "--format", "{{.Names}}"], check=False)
        networks = command(["docker", "network", "ls", "--filter", f"name={network}", "--format", "{{.Name}}"], check=False)
        report["cleanup"] = {"containers": remaining.stdout.splitlines(), "networks": networks.stdout.splitlines(), "verified": remaining.returncode == networks.returncode == 0 and not remaining.stdout.strip() and not networks.stdout.strip()}
        report["pass"] = len(report["runs"]) == len(scenarios) and all(item["pass"] for item in report["runs"]) and report["cleanup"]["verified"]
        (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
        hashes = {str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(output.rglob("*")) if path.is_file() and path.name != "SHA256.json"}
        (output / "SHA256.json").write_text(json.dumps(hashes, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Nouveau dossier de preuves")
    parser.add_argument("--browser-only", action="store_true", help="Rejouer seulement positif19 et mutant19 après un incident du banc")
    args = parser.parse_args()
    raise SystemExit(0 if execute(args.output.resolve(), args.browser_only)["pass"] else 1)
