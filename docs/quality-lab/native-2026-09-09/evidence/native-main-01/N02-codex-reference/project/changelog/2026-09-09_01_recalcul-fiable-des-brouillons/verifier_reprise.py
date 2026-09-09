"""Verify committed repair evidence from three independent Odoo shells."""
import json
from pathlib import Path


def payload(path, prefix):
    """Extract the unique structured result from an Odoo log."""
    rows = [line for line in path.read_text().splitlines() if line.startswith(prefix)]
    assert len(rows) == 1, path
    return json.loads(rows[0][len(prefix):])


proofs = Path(__file__).parent / 'preuves'
initial = payload(proofs / 'inventaire-avant.log', 'INVENTORY ')
first = payload(proofs / 'reprise-1.log', 'REPRISE ')
second = payload(proofs / 'reprise-2.log', 'REPRISE ')
readback = payload(proofs / 'relecture-apres-commit.log', 'INVENTORY ')
assert all(row['database'] == 'lab_client' for row in [initial, first, second, readback])
assert first['committed'] and second['committed']
assert initial['dispatches'] == first['before']
assert first['after'] == second['before'] == second['after'] == readback['dispatches']
assert initial['lines'] == readback['lines']
assert first['writes'] == [{'ids': [1], 'values': {'snapshot_total': 20.0}}]
assert second['writes'] == []
assert {row['name']: row['snapshot_total'] for row in readback['dispatches']} == {
    'LEGACY_DRAFT': 20.0, 'LEGACY_DONE': 777.0,
}
assert [row for row in initial['dispatches'] if row['state'] == 'done'] == [
    row for row in readback['dispatches'] if row['state'] == 'done'
]
print('VALIDÉ : 999 → 20 ; validé 777 inchangé ; premier passage 1 écriture ; second 0 ; états, lignes et commits vérifiés.')
