"""Reprendre D-02 sur le bac lab_client après update, via labctl shell."""

assert env.cr.dbname == 'lab_client', 'Script réservé au bac synthétique lab_client.'
rentals = env['lab.rental'].search([])
env.add_to_compute(rentals._fields['amount_total'], rentals)
rentals._recompute_recordset(['amount_total'])
env.flush_all()
env.cr.commit()
print(f'LAB_RECOMPUTE_OK {len(rentals)} enregistrements')
