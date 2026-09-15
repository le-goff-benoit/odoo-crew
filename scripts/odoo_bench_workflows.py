#!/usr/bin/env python3
"""Run/status du banc de parcours synthétiques ; aucun appel modèle implicite."""

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
FIXTURE = ROOT / "benchmarks/workflow_regressions"
REQUIRED = {"stock", "invoice_pdf", "browser_form"}


def assess(log, returncode, mutant=False, invoice_only=False):
    markers = set(re.findall(r"WORKFLOW_PASS (\w+)", log))
    summaries = [
        tuple(map(int, row))
        for row in re.findall(r"(\d+) failed, (\d+) error\(s\) of (\d+) tests", log)
    ]
    browser = bool(re.search(r"\.browser: WORKFLOW_BROWSER_REAL_CLICK\s*(?:\n|$)", log))
    chrome = bool(re.search(r"(?:Closing|Terminating) chrome headless with pid", log))
    skipped = bool(
        re.search(
            r"skipped Test|Chrome executable not found|Chrome headless failed to start",
            log,
        )
    )
    green = (
        returncode == 0
        and ({"invoice_pdf"} if invoice_only else REQUIRED) <= markers
        and (invoice_only or (browser and chrome))
        and not skipped
        and bool(summaries)
        and all(f == e == 0 for f, e, n in summaries)
    )
    # A crash or unrelated error cannot calibrate the business oracle.
    mutation_rejected = (
        returncode != 0
        and bool(summaries)
        and any(f >= (1 if invoice_only else 3) and e == 0 for f, e, n in summaries)
        and all(
            token in log
            for token in (
                ("WORKFLOW_INVOICE_LINE",)
                if invoice_only
                else (
                    "WORKFLOW_STOCK_REMAINDER",
                    "WORKFLOW_INVOICE_LINE",
                    "WORKFLOW_FORM_EXPLICIT_VALUE",
                )
            )
        )
        and not skipped
    )
    return {
        "pass": mutation_rejected if mutant else green,
        "expected": (
            "invoice_mutant_rejected"
            if invoice_only
            else "three_business_mutants_rejected"
        )
        if mutant
        else "all_pass",
        "returncode": returncode,
        "markers": sorted(markers),
        "summaries": summaries,
        "real_browser_click": browser,
        "chrome": chrome,
        "skipped": skipped,
    }


def prepare(folder, mutant=False, series="19.0"):
    project = folder / "project"
    project.mkdir(parents=True)
    (project / ".odoo-agents").mkdir()
    (project / ".odoo-agents/config").write_text(f"series = {series}\n")
    briefing = subprocess.run(
        ["python3", str(ROOT / "scripts/odoo_briefing.py"), str(project), "--offline"],
        capture_output=True,
        text=True,
        check=True,
    )
    (folder / "briefing.md").write_text(briefing.stdout)
    for module in ("workflow_case", "workflow_oracle"):
        shutil.copytree(
            FIXTURE / "addons" / module,
            project / module,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
    for manifest in project.glob("*/__manifest__.py"):
        manifest.write_text(
            manifest.read_text().replace("19.0.1.0.0", series + ".1.0.0")
        )
    if mutant:
        path = project / "workflow_case/models.py"
        original = path.read_text()
        for needle in ("move.quantity = move.product_uom_qty", "if not self.quantity:"):
            if original.count(needle) != 1:
                raise ValueError("Mutation target changed: " + needle)
        text = original.replace(
            "move.quantity = move.product_uom_qty", "move.quantity = 5"
        ).replace("if not self.quantity:", "if True:")
        path.write_text(text)
        path = project / "workflow_case/views.xml"
        text = path.read_text().replace(
            "</odoo>",
            """<template id="drop_zero_lines" inherit_id="account.report_invoice_document"><xpath expr="//t[@t-foreach='lines_to_report']" position="attributes"><attribute name="t-foreach">lines_to_report.filtered(lambda line: line.price_subtotal != 0)</attribute></xpath></template></odoo>""",
        )
        if series == "18.0":
            text = text.replace("lines_to_report", "lines")
        path.write_text(text)
    return project


def execute(output, invoice18=False):
    series = "18.0" if invoice18 else "19.0"
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, output / "runner.py")
    shutil.copy2(FIXTURE / "protocol.json", output / "protocol.json")
    prefix = "workflow-lab-" + uuid.uuid4().hex[:10]
    pg = prefix + "-pg"
    report = {
        "schema": 1,
        "status": "running",
        "scope": (
            "synthetic Odoo 18.0 rendered invoice PDF"
            if invoice18
            else "synthetic Odoo 19.0 ORM, ordinary-user stock rights, real Chromium and rendered PDF"
        ),
        "model_calls": 0,
        "trials": [],
        "tools": {"runner_command_calls": 0},
        "limitations": [
            "No customer database",
            "No model capability inferred from oracle calibration",
            "Only the selected series and selected paths are qualified",
        ],
    }
    names = [pg]
    start = time.monotonic()

    def command(args, check=True, timeout=60):
        report["tools"]["runner_command_calls"] += 1
        return subprocess.run(
            args, capture_output=True, text=True, check=check, timeout=timeout
        )

    def save():
        (output / "result.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        )

    try:
        report["images"] = {
            tag: json.loads(command(["docker", "image", "inspect", tag]).stdout)[0][
                "Id"
            ]
            for tag in ("odoo-qa:" + series, "postgres:16")
        }
        command(["docker", "network", "create", "--internal", prefix])
        command(
            [
                "docker",
                "run",
                "-d",
                "--name",
                pg,
                "--network",
                prefix,
                "--tmpfs",
                "/var/lib/postgresql/data",
                "-e",
                "POSTGRES_USER=odoo",
                "-e",
                "POSTGRES_PASSWORD=synthetic-lab-only",
                "postgres:16",
            ]
        )
        for _ in range(30):
            if (
                command(
                    ["docker", "exec", pg, "pg_isready", "-U", "odoo"], check=False
                ).returncode
                == 0
            ):
                break
            time.sleep(1)
        else:
            raise RuntimeError("Synthetic postgres unavailable")
        for label, mutant in [("witness", False), ("mutants", True)]:
            folder = output / label
            project = prepare(folder, mutant, series)
            name = prefix + "-" + label
            names.append(name)
            args = [
                "docker",
                "run",
                "--name",
                name,
                "--network",
                prefix,
                "--tmpfs",
                "/var/lib/odoo:mode=1777",
                "--shm-size",
                "256m",
                "--mount",
                f"type=bind,src={project},dst=/mnt/extra-addons,readonly",
                "--entrypoint",
                "odoo",
                "odoo-qa:" + series,
                "--db_host",
                pg,
                "--db_user",
                "odoo",
                "--db_password",
                "synthetic-lab-only",
                "-d",
                "workflow_" + label,
                "--addons-path",
                "/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons",
                "--data-dir",
                "/tmp/odoo-data",
                ("--without-demo=all" if invoice18 else "--without-demo"),
                "--load-language",
                "fr_FR",
                "--http-interface",
                "127.0.0.1",
                "-i",
                "workflow_oracle",
                "--test-enable",
                "--test-tags",
                (
                    "/workflow_oracle:TestInvoiceWorkflow"
                    if invoice18
                    else "/workflow_oracle"
                ),
                "--stop-after-init",
                "--max-cron-threads",
                "0",
                "--workers",
                "0",
                "--log-level",
                "test",
            ]
            trial_start = time.monotonic()
            report["active"] = label
            save()
            with (folder / "odoo.log").open("w") as stream:
                process = subprocess.Popen(
                    args, stdout=stream, stderr=subprocess.STDOUT
                )
                try:
                    rc = process.wait(timeout=700)
                except subprocess.TimeoutExpired:
                    command(["docker", "rm", "-f", name], check=False)
                    process.wait(timeout=30)
                    rc = 124
            result = assess((folder / "odoo.log").read_text(), rc, mutant, invoice18)
            result.update(label=label, seconds=round(time.monotonic() - trial_start, 3))
            evidence = folder / "rendered"
            evidence.mkdir()
            command(
                ["docker", "cp", name + ":/tmp/workflow-evidence/.", str(evidence)],
                check=False,
            )
            report["trials"].append(result)
            save()
            print(json.dumps(result), flush=True)
            if not mutant and not result["pass"]:
                raise RuntimeError("Witness failed; do not infer mutation sensitivity")
        report["status"] = (
            "completed" if all(item["pass"] for item in report["trials"]) else "failed"
        )
    except Exception as exc:
        report["status"] = "error"
        report["error"] = str(exc)
    finally:
        for name in reversed(names):
            command(["docker", "rm", "-f", name], check=False)
        command(["docker", "network", "rm", prefix], check=False)
        remaining = command(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"name={prefix}",
                "--format",
                "{{.Names}}",
            ],
            check=False,
        )
        networks = command(
            [
                "docker",
                "network",
                "ls",
                "--filter",
                f"name={prefix}",
                "--format",
                "{{.Name}}",
            ],
            check=False,
        )
        report["cleanup_verified"] = (
            remaining.returncode == networks.returncode == 0
            and not remaining.stdout.strip()
            and not networks.stdout.strip()
        )
        if not report["cleanup_verified"]:
            report["status"] = "error"
        report["seconds"] = round(time.monotonic() - start, 3)
        report.pop("active", None)
        save()
        (output / "SHA256.json").write_text(
            json.dumps(
                {
                    str(path.relative_to(output)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in sorted(output.rglob("*"))
                    if path.is_file() and path.name != "SHA256.json"
                },
                indent=2,
            )
            + "\n"
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["run", "status"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--mini-release",
        action="store_true",
        help="W05 real plan/flow integration without Docker",
    )
    parser.add_argument(
        "--invoice18",
        action="store_true",
        help="Qualify invoice PDF witness/mutant on Odoo 18.0 only",
    )
    args = parser.parse_args()
    if args.action == "status":
        print((args.output / "result.json").read_text())
        return 0
    if args.mini_release:
        if args.invoice18:
            parser.error("--mini-release et --invoice18 sont incompatibles")
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "workflow_mini_release", FIXTURE / "mini_release.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.execute(args.output.resolve())
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    return (
        0
        if execute(args.output.resolve(), args.invoice18)["status"] == "completed"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
