import json
model = env['lab.dispatch']
draft = model.search([('name', '=', 'LEGACY_DRAFT')])
done = model.search([('name', '=', 'LEGACY_DONE')])
checks = {'migration_draft': len(draft) == 1 and draft.snapshot_total == 20,
          'preserved_done': len(done) == 1 and done.snapshot_total == 777 and done.state == 'done'}
new = model.create({'name': 'oracle'})
env['lab.dispatch.line'].create([{'dispatch_id': new.id, 'quantity': 4, 'price': 8}, {'dispatch_id': new.id, 'quantity': 7, 'price': 10, 'cancelled': True}])
try:
    (new | done).action_recalculate()
    checks['mixed_selection'] = new.snapshot_total == 32 and done.snapshot_total == 777
    (draft | done | new).action_recalculate()
    checks['idempotence'] = draft.snapshot_total == 20 and done.snapshot_total == 777 and new.snapshot_total == 32
except Exception:
    checks['mixed_selection'] = False
    checks['idempotence'] = False
fraction = model.search([('name', '=', 'LEGACY_FRACTION')])
checks['fraction_repaired'] = len(fraction) == 1 and fraction.snapshot_total == 20.0
print('LAB_ORACLE ' + json.dumps(checks))
env.cr.rollback()
