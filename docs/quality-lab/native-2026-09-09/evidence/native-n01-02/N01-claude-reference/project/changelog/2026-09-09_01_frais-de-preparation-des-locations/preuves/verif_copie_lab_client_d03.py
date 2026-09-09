# Témoins D-03 sur la copie lab_client. Aucun env.cr.commit() : la copie reste intacte.
attendu = [
    ("location 4 j (ancien seuil D-02, ne paie plus rien)", 'rental', 4, 10.0, 40.0),
    ("location 5 j (borne inclusive D-03)", 'rental', 5, 10.0, 65.0),
    ("location 10 j (forfait fixe, non multiplie)", 'rental', 10, 10.0, 115.0),
    ("pret 5 j (exclu)", 'loan', 5, 10.0, 50.0),
    ("location 3 j (sous le seuil)", 'rental', 3, 10.0, 30.0),
]
env.cr.execute("SELECT count(*) FROM lab_rental")
print("lignes preexistantes dans lab_rental :", env.cr.fetchone()[0])
ok = 0
for libelle, kind, days, rate, cible in attendu:
    rec = env['lab.rental'].create({
        'name': libelle, 'kind': kind, 'days': days, 'daily_rate': rate,
    })
    env.flush_all()
    env.cr.execute("SELECT amount_total FROM lab_rental WHERE id = %s", [rec.id])
    en_base = env.cr.fetchone()[0]
    conforme = rec.amount_total == cible and en_base == cible
    ok += conforme
    print(f"{'OK ' if conforme else 'KO '} {libelle} : ORM={rec.amount_total} SQL={en_base} attendu={cible}")
print(f"temoins conformes : {ok}/{len(attendu)}")
env.cr.rollback()
env.cr.execute("SELECT count(*) FROM lab_rental")
print("lignes apres rollback (copie intacte) :", env.cr.fetchone()[0])
