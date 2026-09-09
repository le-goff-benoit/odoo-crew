"""Vérifier les rapports de transactions indépendantes et la relecture finale."""

import json
from pathlib import Path


release = Path(__file__).resolve().parent


def report(path, prefix):
    """Extraire un unique rapport JSON du journal du pont."""
    matches = [line[len(prefix):] for line in path.read_text().splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, path
    return json.loads(matches[0])


first = report(release / 'reprise-1.log', 'REPRISE_D12 ')
second = report(release / 'reprise-2.log', 'REPRISE_D12 ')
final = report(release / 'client-final.log', 'INVENTORY ')
initial = report(release.parents[1] / '.odoo-agents/flow-artifacts/dispatch-d12/inventory.log', 'INVENTORY ')
assert first['changed_ids'] == [1]
assert first['changed_count'] == 1
assert second['changed_ids'] == []
assert second['changed_count'] == 0
assert first['committed'] and second['committed']
assert first['after'] == second['before'] == second['after']
assert final['lines'] == initial['lines']
for before, after, original in zip(first['before'], final['dispatches'], initial['dispatches'], strict=True):
    assert {key: before[key] for key in original} == original
    if before['state'] == 'done':
        assert {key: before[key] for key in after} == after
    else:
        assert before['snapshot_total'] == 999
        assert after['snapshot_total'] == 20
assert {row['id']: row['snapshot_total'] for row in final['dispatches']} == {1: 20, 2: 777}
print('VALIDÉ : 1 brouillon corrigé, 0 modification au rejeu, validé et lignes intacts, relecture persistée conforme.')
