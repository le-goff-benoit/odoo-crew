#!/usr/bin/env python3
"""Recompute campaign measurements without modifying native archives or reviews."""
import argparse
from datetime import datetime
import json
from pathlib import Path


def summarize(campaign, reviews):
    rows = []
    for path in sorted(Path(campaign).glob('N0[67]-*/state.json')):
        state = json.loads(path.read_text())
        review_path = Path(reviews) / path.parent.name / 'semantic-review.json'
        review = json.loads(review_path.read_text()) if review_path.exists() else {}
        timing = review.get('time', {})
        seconds = review.get('review_seconds', timing.get('active_review_seconds'))
        finished = review.get('finished_at_utc', timing.get('finished_utc'))
        wall = None
        if finished and state.get('started_at'):
            wall = (datetime.fromisoformat(finished) - datetime.fromisoformat(state['started_at'])).total_seconds()
            if wall < 0:
                raise ValueError('review predates trial: ' + path.parent.name)
        elapsed = state.get('elapsed_to_oracle_seconds')
        work = round(elapsed + seconds, 3) if elapsed is not None and seconds is not None else None
        verdict = review.get('verdict', 'pending')
        turns = state.get('turns', [])
        counts = [turn.get('tool_calls') for turn in turns]
        tool_calls = sum(counts) if counts and all(isinstance(n, int) for n in counts) else None
        unreserved = (verdict == 'accepted' and state.get('status') == 'executed'
                      and state.get('oracle', {}).get('passed') is True
                      and state.get('reception', {}).get('passed') is True)
        rows.append({
            'trial': path.parent.name,
            'execution': state['status'],
            'requested': state.get('config'),
            'observed_model': [t.get('actual_model') for t in state.get('turns', [])],
            'observed_effort': [t.get('actual_effort') for t in state.get('turns', [])],
            'setup_seconds': state.get('setup_seconds'),
            'agent_seconds': state.get('agent_seconds'),
            'oracle_seconds': state.get('oracle_seconds'),
            'tool_calls': tool_calls,
            'bridge_calls': state.get('bridge_calls'),
            'oracle_passed': state.get('oracle', {}).get('passed'),
            'mechanical_gate': state.get('reception', {}).get('passed'),
            'semantic_verdict': verdict,
            'review_seconds': seconds,
            'review_queue_seconds': round(wall - work, 3) if wall is not None and work is not None else None,
            'measured_work_to_verdict_seconds': work,
            'wall_to_verdict_seconds': round(wall, 3) if wall is not None else None,
            'time_to_unreserved_receipt_seconds': round(wall, 3) if wall is not None and unreserved else None,
            'principal_rework_seconds': None,
            'post_reception_rework_performed': False if review else None,
            'avoidable_bridge_seconds_lower_bound': review.get('avoidable_bridge_seconds_lower_bound'),
        })
    return {'scope': 'One observation per pair; separate provider/effort settings. No model ranking.',
            'timing': 'Work sums setup, agent, oracle and independent review. Wall time also includes review queue/coordination. Unknown is null; reserved acceptance is not unreserved reception.',
            'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', required=True, type=Path)
    parser.add_argument('--reviews', type=Path, default=Path(__file__).parent / 'evidence/native')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(summarize(args.campaign, args.reviews), ensure_ascii=False, indent=2) + '\n')
