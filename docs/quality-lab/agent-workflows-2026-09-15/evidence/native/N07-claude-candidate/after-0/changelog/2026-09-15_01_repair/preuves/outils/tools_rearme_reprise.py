# Remet la copie synthétique dans son état d'avant reprise, pour rejouer
# le script de migration et prouver qu'il est bien l'auteur du recalcul.
env.cr.execute(
    "UPDATE ir_module_module SET latest_version = '19.0.1.0.0' WHERE name = 'lab_preparation'")
env['lab.preparation'].browse(1).prepared_qty = 999
env.cr.commit()
env.cr.execute("SELECT latest_version FROM ir_module_module WHERE name = 'lab_preparation'")
print('latest_version=%s' % env.cr.fetchone()[0])
print('prepared_qty(1)=%s' % env['lab.preparation'].browse(1).prepared_qty)
