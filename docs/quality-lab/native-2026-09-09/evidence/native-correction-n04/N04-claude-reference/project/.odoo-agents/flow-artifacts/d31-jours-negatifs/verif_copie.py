from psycopg2 import IntegrityError

env.cr.execute("""SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
                  WHERE conrelid = 'lab_rental'::regclass AND contype = 'c'""")
print("CONTRAINTES CHECK:", env.cr.fetchall())

env.cr.execute("SELECT count(*) FROM lab_rental WHERE days < 0")
print("LIGNES NEGATIVES RESTANTES:", env.cr.fetchone()[0])

Rental = env['lab.rental']
ref = Rental.create({'name': 'QA copie — location valide', 'days': 4, 'daily_rate': 10.0})
env.flush_all()
print("REFERENCE:", ref.id, ref.days, ref.amount_total)

try:
    with env.cr.savepoint():
        Rental.create({'name': 'QA copie — refus creation', 'days': -2, 'daily_rate': 10.0})
        env.flush_all()
    print("CREATION NEGATIVE: NON REFUSEE  <-- ANOMALIE")
except IntegrityError as exc:
    print("CREATION NEGATIVE REFUSEE:", str(exc).strip().splitlines()[0])

try:
    with env.cr.savepoint():
        ref.days = -5
        env.flush_all()
    print("ECRITURE NEGATIVE: NON REFUSEE  <-- ANOMALIE")
except IntegrityError as exc:
    print("ECRITURE NEGATIVE REFUSEE:", str(exc).strip().splitlines()[0])

env.invalidate_all()
print("APRES REFUS, REFERENCE:", ref.days, ref.amount_total)

zero = Rental.create({'name': 'QA copie — zero', 'days': 0, 'daily_rate': 10.0, 'kind': 'loan'})
env.flush_all()
print("ZERO ACCEPTE:", zero.days, zero.amount_total)

print("MESSAGE METIER:", Rental._table_objects['check_days_positive'].get_error_message(Rental)
      if hasattr(Rental, '_table_objects') else 'n.a.')

# Nettoyage : la copie repart dans l'état où elle était (0 ligne lab.rental).
(ref | zero).unlink()
env.flush_all()
env.cr.execute("SELECT count(*) FROM lab_rental")
print("LIGNES APRES NETTOYAGE:", env.cr.fetchone()[0])
env.cr.commit()
