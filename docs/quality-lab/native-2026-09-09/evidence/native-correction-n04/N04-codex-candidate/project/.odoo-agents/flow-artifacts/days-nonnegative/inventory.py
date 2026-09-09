import json

rentals = env['lab.rental'].search([])
rows = rentals.read(['name', 'days', 'daily_rate', 'kind', 'amount_total'])
env.cr.execute("""
    SELECT conname, pg_get_constraintdef(oid), convalidated
      FROM pg_constraint WHERE conrelid = 'lab_rental'::regclass
     ORDER BY conname
""")
constraints = env.cr.fetchall()
print(json.dumps({'rentals': rows, 'negative_count': len(rentals.filtered(lambda r: r.days < 0)),
                  'constraints': constraints,
                  'manual_fields': env['ir.model.fields'].search_count([
                      ('model', '=', 'lab.rental'), ('state', '=', 'manual')]),
                  'automation_installed': env['ir.module.module'].search_count([
                      ('name', '=', 'base_automation'), ('state', '=', 'installed')])},
                 ensure_ascii=False, sort_keys=True))
