#!/usr/bin/env python3
"""Point d'entrée du travail : contexte ciblé, état et prochaines actions Crew."""
import argparse
import json
from pathlib import Path

from odoo_documents import within
import odoo_feedback
import odoo_knowledge


def status(root, release=None, task=None):
    root = Path(root).resolve()
    tasks, warnings = [], []
    if task and not release:
        raise ValueError('release requise pour une tâche')
    if release:
        folder = odoo_knowledge.release_path(root, release)
        if (folder / 'plan.json').is_file():
            import odoo_plan
            plan, _ = odoo_plan.read(folder)
            states = odoo_plan.statuses(plan, root)
            for row in plan['tasks']:
                state, reason = states[row['id']]
                available, blocked = odoo_plan.available(plan, root, row['id'])
                tasks.append({'id': row['id'], 'title': row['title'], 'status': state,
                              'reason': reason, 'ready': available, 'blocked': blocked,
                              'attempt': row.get('attempts', [])[-1:]})
        if task and task not in {t['id'] for t in tasks}:
            raise ValueError('tâche absente du plan sélectionné')
    memory = odoo_knowledge.snapshot(root, release)
    warnings.extend(memory['warnings'])
    feedback = odoo_feedback.snapshot(root, release)
    warnings.extend(feedback['warnings'])
    return {'schema': 1, 'project': str(root), 'release': release, 'task': task,
            'tasks': tasks, 'feedback_pending': feedback['pending'], 'warnings': warnings,
            'next': 'Reprendre le flow existant et ses preuves.' if any(t['attempt'] for t in tasks if not task or task == t['id'])
                    else 'Qualifier la demande avec /odoo-new, ou exécuter le plan autorisé avec /odoo-start.',
            'completion': 'Critères couverts, preuves actuelles et réception publiée. Une preuve valide se réutilise ; un nouvel essai exige une cause.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('status', 'prepare', 'feedback', 'decision', 'start', 'receive', 'preflight'))
    parser.add_argument('project', type=Path)
    parser.add_argument('--release'); parser.add_argument('--task'); parser.add_argument('--query', default='')
    parser.add_argument('--budget', type=int, default=12000); parser.add_argument('--file', type=Path)
    parser.add_argument('--proof'); parser.add_argument('--acceptance'); parser.add_argument('--memory')
    parser.add_argument('--knowledge'); parser.add_argument('--check-proofs', type=Path)
    parser.add_argument('--environment', type=Path, help='Identité attendue de l’environnement de contrôle')
    args = parser.parse_args()
    try:
        if args.action == 'preflight':
            if not args.proof:
                raise ValueError('--proof requis')
            from odoo_evidence import verify
            proof = json.loads(within(args.project, args.proof).read_text())
            environment = json.loads(args.environment.read_text()) if args.environment else None
            verify(proof, args.project, expected_environment=environment)
            print(json.dumps({'reusable': True, 'proof': args.proof,
                              'environment_checked': environment is not None,
                              'limitation': 'Vérifier la pertinence du périmètre et les données de départ ; une empreinte de code seule ne les prouve pas.'}, ensure_ascii=False))
            return
        if args.action in ('start', 'receive'):
            if not args.release or not args.task:
                raise ValueError('--release et --task requis')
            import odoo_plan
            folder = odoo_knowledge.release_path(args.project, args.release)
            print(odoo_plan.mutate(folder, 'start' if args.action == 'start' else 'finish', args.task,
                proof=args.proof, acceptance=args.acceptance, memory=args.memory, knowledge=args.knowledge,
                check_proofs=json.loads(args.check_proofs.read_text()) if args.check_proofs else None))
            return
        if args.action == 'decision':
            if not args.release or not args.file:
                raise ValueError('--release et --file requis ; contribution relue avec ses sources')
            print(odoo_knowledge.publish(args.project, args.release, json.loads(args.file.read_text())))
            return
        current = status(args.project, args.release, args.task)
        if args.action in ('prepare', 'feedback'):
            result = odoo_feedback.automatic(args.project, args.release)
            current['feedback_pending'] = result.get('pending')
            if result.get('warning'): current['warnings'].append(result['warning'])
        print(json.dumps(current, ensure_ascii=False, indent=2))
        if args.action == 'prepare':
            import odoo_briefing
            options = ['odoo_briefing', str(args.project), '--query', args.query, '--budget', str(args.budget), '--offline']
            if args.release: options += ['--release', args.release]
            if args.task: options += ['--task', args.task]
            raise SystemExit(odoo_briefing.main(options))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
