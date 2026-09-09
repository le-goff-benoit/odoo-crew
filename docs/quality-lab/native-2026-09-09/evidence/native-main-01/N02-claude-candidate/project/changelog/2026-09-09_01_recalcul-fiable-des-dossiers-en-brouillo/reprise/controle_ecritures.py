"""Contrôle : le dossier validé n'a été écrit par aucune passe de reprise."""
for d in env['lab.dispatch'].search([]).sorted('id'):
    print('%-14s state=%-5s create=%s write=%s ecrit_apres_creation=%s' % (
        d.name, d.state, d.create_date, d.write_date, d.write_date > d.create_date))
