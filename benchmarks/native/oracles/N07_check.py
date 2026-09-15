import json
model = env['lab.preparation']
auto = model.search([('name', '=', 'LEGACY_AUTO')])
zero = model.search([('name', '=', 'LEGACY_MANUAL_ZERO')])
partial = model.search([('name', '=', 'LEGACY_MANUAL_PARTIAL')])
done = model.search([('name', '=', 'LEGACY_DONE')])
checks = {
    'legacy_auto_repaired': len(auto) == 1 and auto.prepared_qty == 7,
    'legacy_explicit_zero_preserved': len(zero) == 1 and zero.prepared_qty == 0 and zero.manual,
    'legacy_partial_preserved': len(partial) == 1 and partial.prepared_qty == 2 and partial.manual,
    'legacy_done_preserved': len(done) == 1 and done.prepared_qty == 88 and done.state == 'done',
}
try:
    fresh = model.create({'name': 'Oracle manual zero', 'ordered_qty': 9})
    fresh.action_set_manual(0)
    model._cron_prepare()
    checks['explicit_zero_not_false'] = fresh.manual and fresh.prepared_qty == 0
    source = model.create({'name': 'Oracle split', 'ordered_qty': 10, 'delivered_qty': 3, 'prepared_qty': 2, 'manual': True})
    clone = source.copy({'name': 'Oracle duplicate'})
    checks['copy_resets_operational_state'] = (clone.state, clone.ordered_qty, clone.delivered_qty, clone.prepared_qty, clone.manual) == ('draft', 10, 0, 0, False)
    model._cron_prepare()
    checks['copy_then_cron'] = clone.prepared_qty == 10 and source.prepared_qty == 2
    remainder = source.action_remainder()
    checks['remainder_contract'] = len(remainder) == 1 and remainder.parent_id == source and (remainder.state, remainder.ordered_qty, remainder.delivered_qty, remainder.prepared_qty, remainder.manual) == ('draft', 7, 0, 0, False) and source.state == 'done' and source.prepared_qty == 2
    model._cron_prepare()
    checks['remainder_then_cron'] = len(remainder) == 1 and remainder.prepared_qty == 7 and source.prepared_qty == 2
    finished = model.create({'name': 'Oracle no remainder', 'ordered_qty': 3, 'delivered_qty': 3})
    before_count = model.search_count([])
    checks['no_empty_remainder'] = not finished.action_remainder() and before_count == model.search_count([])
    overd = model.create({'name': 'Oracle nonnegative', 'ordered_qty': 2, 'delivered_qty': 4})
    model._cron_prepare()
    checks['negative_remaining_clamped'] = overd.prepared_qty == 0
    records = fresh | source | clone | remainder | zero | partial | done | overd
    before = records.read(['state', 'ordered_qty', 'delivered_qty', 'prepared_qty', 'manual'])
    model._cron_prepare()
    checks['idempotent_cron'] = before == records.read(['state', 'ordered_qty', 'delivered_qty', 'prepared_qty', 'manual'])
except Exception:
    checks['execution_completed'] = False
print('LAB_ORACLE ' + json.dumps(checks))
env.cr.rollback()
