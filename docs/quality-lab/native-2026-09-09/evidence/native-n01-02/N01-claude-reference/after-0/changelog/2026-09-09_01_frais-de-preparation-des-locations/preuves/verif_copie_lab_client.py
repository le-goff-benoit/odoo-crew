# Vérification manuelle sur la copie lab_client, après mise à niveau du module.
Rental = env['lab.rental']
cas = [
    ("location 4 j", 'rental', 4, 10.0, 52.0),
    ("location 3 j", 'rental', 3, 10.0, 30.0),
    ("pret 4 j", 'loan', 4, 10.0, 40.0),
    ("pret 10 j", 'loan', 10, 10.0, 100.0),
]
crees = Rental.browse()
for nom, kind, days, rate, attendu in cas:
    r = Rental.create({'name': nom, 'kind': kind, 'days': days, 'daily_rate': rate})
    crees |= r
    env.flush_all()
    env.cr.execute("SELECT amount_total FROM lab_rental WHERE id = %s", [r.id])
    en_base = env.cr.fetchone()[0]
    print(f"{nom:15s} attendu={attendu:7.2f} orm={r.amount_total:7.2f} sql={en_base:7.2f} "
          f"{'OK' if r.amount_total == attendu == en_base else 'ECHEC'}")
crees.unlink()
env.cr.execute("SELECT count(*) FROM lab_rental")
print("enregistrements restants dans la copie :", env.cr.fetchone()[0])
env.cr.commit()
