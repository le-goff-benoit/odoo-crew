message_attendu = "Le nombre de jours d'une location ne peut pas être négatif."
Rental = env['lab.rental']

print("PREUVE r2 / A8")
c = getattr(type(Rental), '_check_days_positive', None)
print("objet Constraint present :", c is not None)
if c is not None:
    print("message configure   =", repr(c.message))
    print("definition SQL      =", repr(c._definition))
    print("message == attendu  =", c.message == message_attendu)

# Vérification qu'aucune occurrence de _sql_constraints/api.constrains ne subsiste
import subprocess
out = subprocess.run(['grep', '-rn', '_sql_constraints', '/work/lab_rental/'], capture_output=True, text=True)
print("grep _sql_constraints (vide attendu) :", repr(out.stdout))

# Constat direct sur la base : le message configuré est bien attaché au nom de contrainte pg
cr = env.cr
cr.execute("SELECT conname FROM pg_constraint WHERE conrelid='lab_rental'::regclass AND conname='lab_rental_check_days_positive'")
print("nom de contrainte en base =", cr.fetchone())
