cr = env.cr
cr.execute("DELETE FROM lab_rental WHERE days < 0")
env.cr.commit()
cr.execute("SELECT count(*) FROM lab_rental")
print("total apres nettoyage lignes violantes =", cr.fetchone()[0])
