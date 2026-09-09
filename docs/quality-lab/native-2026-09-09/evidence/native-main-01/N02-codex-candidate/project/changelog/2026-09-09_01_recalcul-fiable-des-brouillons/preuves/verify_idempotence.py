"""Comparer les preuves issues de sessions Odoo distinctes."""
import json
from pathlib import Path

proofs = Path(__file__).resolve().parent


def result(filename):
    """Extraire le résultat structuré du journal Odoo."""
    lines = (proofs / filename).read_text().splitlines()
    return json.loads(next(line.removeprefix('D12_RESULT=') for line in lines
                           if line.startswith('D12_RESULT=')))


first = result('reprise-1.log')
second = result('reprise-2.log')
initial_log = Path('/work/.odoo-agents/flow-artifacts/dispatch-d12/inventory.log').read_text()
initial = json.loads(initial_log[initial_log.index('\n{') + 1:])
final_log = (proofs / 'lecture-finale.log').read_text()
final = json.loads(final_log[final_log.index('\n{') + 1:])
assert first['database'] == second['database'] == final['database'] == 'lab_client'
assert first['committed'] and second['committed']
assert first['before']['dispatches'] == initial['dispatches']
assert first['changed_ids'] == [1]
assert first['after'] == second['before'] == second['after']
assert second['changed_ids'] == []
assert final['dispatches'] == second['after']['dispatches']
assert final['lines'] == initial['lines']
assert [item['snapshot_total'] for item in final['dispatches']] == [20, 777]
assert initial['dispatches'][1] == final['dispatches'][1]
print('VALIDÉ : reprise persistée 999 → 20 ; validé 777 inchangé ; deuxième passage sans changement, write_date inclus ; 4 lignes et états conservés ; relecture indépendante conforme.')
