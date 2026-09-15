# Déclenche réellement l'action planifiée sur la copie, puis vérifie
# qu'un second passage ne change rien (idempotence sur données réelles).
cron = env.ref('lab_preparation.ir_cron_lab_preparation')
print('cron : %s | modèle=%s | état=%s | actif=%s | %s %s | code=%s' % (
    cron.cron_name, cron.model_id.model, cron.state, cron.active,
    cron.interval_number, cron.interval_type, cron.code))


def releve():
    return {r.id: (r.state, r.ordered_qty, r.delivered_qty, r.prepared_qty, r.manual)
            for r in env['lab.preparation'].search([], order='id')}


avant = releve()
cron.method_direct_trigger()
apres_1 = releve()
cron.method_direct_trigger()
apres_2 = releve()
print('avant     = %s' % avant)
print('1er essai = %s' % apres_1)
print('2e essai  = %s' % apres_2)
print('IDEMPOTENT = %s' % (avant == apres_1 == apres_2))
env.cr.commit()
