#!/usr/bin/env python3
"""Vérifie toutes les sorties déclarées par build.sh, sans les modifier."""
from __future__ import annotations

import re
import shlex
import json
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from odoo_loaded_instructions import check as check_loaded
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def expected_outputs(root: Path, destination: Path) -> dict[Path, str]:
    build = (root / "build.sh").read_text(encoding="utf-8")
    outputs = {}
    declarations = [shlex.split(line) for line in build.replace("\\\n", "").splitlines()
                    if re.match(r"^emit(?:_command|_skill)? ", line)]
    for declaration in declarations:
        kind, slug, role, *args = declaration
        body = (root / "roles" / f"{role}.md").read_text(encoding="utf-8")
        body += "\n" + (root / "roles/communication.md").read_text(encoding="utf-8")
        marker = (
            "<!-- Généré par ~/.odoo19-agents/build.sh — ne pas éditer ici.\n"
            f"     Source : ~/.odoo19-agents/roles/{role}.md -->\n\n"
        )
        if kind == "emit_command":
            hint, intro, short, desc = args
            header = f"description: {json.dumps(desc, ensure_ascii=False)}\n"
            if hint:
                header += f"argument-hint: {json.dumps(hint, ensure_ascii=False)}\n"
            target = destination / ".claude/commands" / f"{slug}.md"
            outputs[target] = "---\n" + header + "---\n\n" + marker + (intro + "\n\n" if intro else "") + body
        elif kind == "emit":
            tools, short, desc, *color = args
            header = f"name: {slug}\ndescription: {json.dumps(desc, ensure_ascii=False)}\n"
            if tools:
                header += f"tools: {tools}\n"
            header += "model: inherit\n"
            if color:
                header += f"color: {color[0]}\n"
            outputs[destination / ".claude/agents" / f"{slug}.md"] = "---\n" + header + "---\n\n" + marker + body
        else:
            short, desc = args
        header = f"name: {slug}\ndescription: {json.dumps(desc, ensure_ascii=False)}\nmetadata:\n  short-description: {json.dumps(short, ensure_ascii=False)}\n"
        content = "---\n" + header + "---\n\n" + marker + body
        outputs[destination / ".codex/skills" / slug / "SKILL.md"] = content
        if kind == "emit_skill":
            outputs[destination / ".claude/skills" / slug / "SKILL.md"] = content
    if not declarations:
        raise ValueError("aucune déclaration de génération")
    return outputs


def check(root: Path, destination: Path) -> list[str]:
    errors = []
    for path, expected in expected_outputs(root, destination).items():
        if not path.is_file():
            errors.append(f"manquant : {path}")
            continue
        text = path.read_text(encoding="utf-8")
        if text != expected:
            errors.append(f"contenu différent de la source : {path}")
    start = "<!-- odoo19-agents:début — généré par ~/.odoo19-agents/build.sh -->"
    end = "<!-- odoo19-agents:fin -->"
    routing = (root / "roles/routing.md").read_text(encoding="utf-8")
    expected = (
        start + "\n# Développement Odoo\n\n" + routing
        + "\nPour une demande de développement, la chaîne complète est outillée par\n"
        + "la commande `/odoo-new`.\n" + end
    )
    for relative in (".claude/CLAUDE.md", ".codex/AGENTS.md"):
        path = destination / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        blocks = re.findall(re.escape(start) + r".*?" + re.escape(end), text, re.S)
        if blocks != [expected]:
            errors.append(f"bloc d’aiguillage manquant ou divergent : {path}")
    errors.extend(check_loaded(destination))
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: odoo_generated.py <racine des sorties>")
    problems = check(ROOT, Path(sys.argv[1]).resolve())
    for problem in problems:
        print(f"≠ {problem}", file=sys.stderr)
    if problems:
        sys.exit(1)
    print(f"Génération conforme : {len(expected_outputs(ROOT, Path(sys.argv[1])))} fichiers + 2 blocs d’aiguillage et pointeur personnel.")
