import psycopg2
from odoo.tools import mute_logger

cr = env.cr
Rental = env['lab.rental']
results = {}

# A1 : création days = -1 refusée
with mute_logger('odoo.sql_db'):
    try:
        with cr.savepoint():
            Rental.create({'name': 'A1 negative create', 'days': -1, 'daily_rate': 10.0})
            env.flush_all()
        results['A1'] = 'ECHEC (pas de refus)'
    except psycopg2.errors.CheckViolation:
        results['A1'] = 'OK (CheckViolation levee)'

# curseur toujours utilisable ?
cr.execute("SELECT 1")
assert cr.fetchone() == (1,)

# Préparer une location valide pour A2/A5
valid = Rental.create({'name': 'valide A2/A5', 'days': 5, 'daily_rate': 10.0})
env.flush_all()

# A2 : écriture days = -3 refusée, valeur restée 5
with mute_logger('odoo.sql_db'):
    try:
        with cr.savepoint():
            valid.write({'days': -3})
            env.flush_all()
        results['A2'] = 'ECHEC (pas de refus)'
    except psycopg2.errors.CheckViolation:
        results['A2'] = 'OK (CheckViolation levee)'

valid.invalidate_recordset()
cr.execute("SELECT days FROM lab_rental WHERE id = %s", (valid.id,))
days_sql = cr.fetchone()[0]
results['A2_valeur_sql'] = days_sql
results['A2_valeur_orm'] = valid.days
results['A2_intacte'] = (days_sql == 5 and valid.days == 5)

# A3 : days = 0 accepté, amount_total == 0.0
r3 = Rental.create({'name': 'A3 zero', 'days': 0, 'daily_rate': 10.0})
env.flush_all()
results['A3'] = 'OK' if r3.amount_total == 0.0 else f'ECHEC amount_total={r3.amount_total}'

# A4 : days=4, daily_rate=12.5 -> amount_total = 50.0
r4 = Rental.create({'name': 'A4 calc', 'days': 4, 'daily_rate': 12.5})
env.flush_all()
results['A4'] = 'OK' if r4.amount_total == 50.0 else f'ECHEC amount_total={r4.amount_total}'

# A5 : la location "valid" survit au rejet A2, curseur utilisable pour la suite
valid.invalidate_recordset()
cr.execute("SELECT name, days, daily_rate FROM lab_rental WHERE id = %s", (valid.id,))
row = cr.fetchone()
results['A5'] = 'OK' if row == ('valide A2/A5', 5, 10.0) else f'ECHEC row={row}'
# curseur encore utilisable après tout ceci :
cr.execute("SELECT count(*) FROM lab_rental")
results['A5_curseur_utilisable_count'] = cr.fetchone()[0]

for k, v in results.items():
    print(f"{k} = {v}")

# Nettoyage : on retire les enregistrements de test créés (ils n'existaient pas avant, base doit rester propre)
env.cr.execute("DELETE FROM lab_rental WHERE name IN ('valide A2/A5', 'A3 zero', 'A4 calc')")
env.cr.commit()
env.cr.execute("SELECT count(*) FROM lab_rental")
print("total apres nettoyage =", env.cr.fetchone()[0])
