records=env['lab.qualification'].create([
{'name':'ordered-seed-draft-zero','state':'draft','quantity':0,'unit_price':10},
{'name':'ordered-seed-draft-positive','state':'draft','quantity':3,'unit_price':10},
{'name':'ordered-seed-confirmed-positive','state':'confirmed','quantity':3,'unit_price':10},
])
env.flush_all()
env.cr.commit()
print('ORDERED_SEED_IDS='+repr(records.ids))
