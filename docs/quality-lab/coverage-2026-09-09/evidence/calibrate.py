import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path('/home/blegoff/.odoo19-agents')
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'scripts'))
import odoo_flow as current
import odoo_coverage as coverage
spec = importlib.util.spec_from_file_location('reference_flow', BASE/'reference/scripts/odoo_flow.py')
previous = importlib.util.module_from_spec(spec); spec.loader.exec_module(previous)
graph = ROOT/'workflows/odoo-workflow.json'
results=[]
for variant, tool, status in [('reference-partial',previous,'partial'), ('candidate-partial',current,'partial'), ('candidate-complete',current,'covered'), ('candidate-false-claim',current,'covered')]:
    root=BASE/'calibration'/variant;root.mkdir(parents=True)
    review=root/'review.md'
    review.write_text("## Critères d'acceptation\n- [ ] **I7** — Message ligne 3 reçu, aucune ligne importée conservée et anciens identifiants et valeurs inchangés.\n")
    proof=root/'proof.md'
    proof.write_text('Message ligne 3 reçu ; count avant/après=8 ; identifiants et valeurs non comparés.' if variant!='candidate-complete' else 'Message ligne 3 reçu ; aucune ligne importée ; les huit identifiants et toutes leurs valeurs comparés et inchangés.')
    state=current.new_state(root,'development',variant,graph)
    state['start_pending']=False
    state['tokens']={e['id']:1 for e in current.incoming_edges(state['graph_snapshot'],'module_high_gate')}
    path=root/'flow.json';current.write_state(path,state)
    current.claim_node(path,graph,'module_high_gate','codex-calibration')
    receipt=root/'coverage.json'
    current.bind_criteria(path,graph,review,receipt,'codex-calibration')
    data=json.loads(receipt.read_text())
    data['criteria'][0].update(status=status,evidence=[{'path':'proof.md','sha256':coverage.digest(proof.read_bytes())}])
    receipt.write_text(json.dumps(data,ensure_ascii=False,indent=2))
    before=path.read_bytes()
    try:
        tool.complete_claimed_node(path,graph,'module_high_gate','pass',[str(proof),str(receipt)],None,'codex-calibration',False)
        accepted=True;error=None
    except current.FlowError as exc:
        accepted=False;error=str(exc)
    results.append({'variant':variant,'accepted':accepted,'error':error,'state_unchanged_on_refusal':before==path.read_bytes() if not accepted else None})
    (root/'status.txt').write_text(current.format_dashboard(current.load_json(path),state['graph_snapshot'],True))
assert [r['accepted'] for r in results]==[True,False,True,True]
(BASE/'calibration.json').write_text(json.dumps({'results':results,'interpretation':'La déclaration partial est bloquée ; un covered mensonger reste accepté et ne satisfait pas le critère métier. Ce témoin interdit toute prétention de jugement sémantique automatique.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
