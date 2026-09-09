import psycopg2

model = env['lab.rental']
obj = model._table_objects['lab_rental_check_days_positive']
print("NOM SQL:", obj.full_name(model), "| DEFINITION:", obj.get_definition(env.registry))

try:
    with env.cr.savepoint():
        model.create({'name': 'QA copie — message', 'days': -1})
        env.flush_all()
except psycopg2.Error as exc:
    print("MESSAGE RENDU A L'UTILISATEUR:", model._sql_error_to_message(exc))

env.cr.execute("SELECT count(*) FROM lab_rental")
print("LIGNES DANS LA COPIE:", env.cr.fetchone()[0])
