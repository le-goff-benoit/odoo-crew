"""Comparer les sorties des shells indépendants après la reprise D-12."""

import json
from pathlib import Path


release = Path(__file__).resolve().parent


def payload(path, marker):
    """Extraire la preuve JSON d'un journal complet du pont."""
    rows = [line.removeprefix(marker) for line in path.read_text().splitlines() if line.startswith(marker)]
    assert len(rows) == 1, f'Preuve absente ou ambiguë : {path}'
    return json.loads(rows[0])


initial = payload(release / 'preuves/inventaire-initial.log', 'INVENTORY_JSON=')
first = payload(release / 'preuves/reprise-1.log', 'REPAIR_JSON=')
second = payload(release / 'preuves/reprise-2.log', 'REPAIR_JSON=')
final = payload(release / 'preuves/inventaire-final.log', 'INVENTORY_JSON=')

assert first['database'] == second['database'] == initial['database'] == final['database'] == 'lab_client'
assert first['draft_count'] == second['draft_count'] == 1
assert first['validated_count'] == second['validated_count'] == 1
assert first['changed_ids'] == [1] and first['changed_count'] == 1
assert second['changed_ids'] == [] and second['changed_count'] == 0
assert first['after'] == second['before'] == second['after']

for old, before in zip(initial['dispatches'], first['before']['dispatches'], strict=True):
    assert all(before[key] == value for key, value in old.items())
for persisted, observed in zip(second['after']['dispatches'], final['dispatches'], strict=True):
    assert all(persisted[key] == value for key, value in observed.items())
assert initial['lines'] == final['lines']
assert [(row['name'], row['state'], row['snapshot_total']) for row in final['dispatches']] == [
    ('LEGACY_DRAFT', 'draft', 20.0),
    ('LEGACY_DONE', 'done', 777.0),
]
print('VALIDÉ : 1 brouillon corrigé au premier passage, 0 au second ; validé, états et lignes inchangés ; relecture indépendante conforme.')
