#!/usr/bin/env python3
"""Éliminer les anciennes copies générées chargées depuis le dossier personnel."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil

START = '<!-- odoo19-agents:début — généré par ~/.odoo19-agents/build.sh -->'
END = '<!-- odoo19-agents:fin -->'
POINTER = START + '\nLes règles Odoo partagées sont dans `~/.odoo19-agents/roles/routing.md`.\nLes profils et commandes sont générés depuis le même référentiel pour Claude et Codex.\n' + END


def backup(path, destination):
    raw = path.read_bytes()
    name = path.name + '-' + hashlib.sha256(raw).hexdigest()[:12]
    folder = destination / '.odoo-agents-backups/loaded-instructions'
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    if not target.exists():
        target.write_bytes(raw)


def migrate(destination):
    path = destination / 'AGENTS.md'
    text = path.read_text() if path.exists() else ''
    pattern = re.escape(START) + r'.*?' + re.escape(END)
    if START in text and END not in text:
        raise ValueError('bloc généré incomplet : correction manuelle nécessaire')
    without = re.sub(pattern, '', text, flags=re.S).strip()
    updated = (without + '\n\n' if without else '') + POINTER + '\n'
    if text != updated:
        if path.exists():
            backup(path, destination)
        path.write_text(updated)
    legacy = destination / '.agents/skills/camptocamp-docs'
    skill = legacy / 'SKILL.md'
    if skill.is_file():
        if 'Source : ~/.odoo19-agents/roles/docs.md' not in skill.read_text():
            raise ValueError('skill documentaire non généré : conserver et arbitrer explicitement')
        backup(skill, destination)
        # Sauvegarder tout le dossier avant retrait du catalogue automatique.
        target = destination / '.odoo-agents-backups/loaded-instructions' / ('camptocamp-docs-' + hashlib.sha256(skill.read_bytes()).hexdigest()[:12])
        if not target.exists():
            shutil.copytree(legacy, target)
        shutil.rmtree(legacy)


def check(destination):
    errors = []
    path = destination / 'AGENTS.md'
    text = path.read_text() if path.exists() else ''
    blocks = re.findall(re.escape(START) + r'.*?' + re.escape(END), text, re.S)
    if blocks != [POINTER]:
        errors.append('aiguillage personnel historique ou absent : ' + str(path))
    if (destination / '.agents/skills/camptocamp-docs/SKILL.md').exists():
        errors.append('doublon documentaire encore chargé depuis .agents/skills')
    return errors


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('destination', type=Path)
    p.add_argument('--check', action='store_true'); args = p.parse_args()
    if not args.check:
        migrate(args.destination)
    errors = check(args.destination)
    for error in errors:
        print(error)
    raise SystemExit(bool(errors))
