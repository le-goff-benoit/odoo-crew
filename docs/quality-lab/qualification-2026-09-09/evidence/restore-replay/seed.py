import base64
import json

payload = b'qualification attachment: restore and filestore, 2026-09-09\n'
attachment = env['ir.attachment'].create({
    'name': 'qualification-proof.txt', 'type': 'binary',
    'datas': base64.b64encode(payload), 'mimetype': 'text/plain',
})
cron = env['ir.cron'].create({
    'name': 'qualification cron', 'model_id': env.ref('base.model_res_partner').id,
    'state': 'code', 'code': 'model.search_count([])', 'active': True,
    'interval_number': 1, 'interval_type': 'days',
})
server = env['ir.mail_server'].create({
    'name': 'qualification mail', 'smtp_host': 'qualification.invalid',
    'smtp_port': 25, 'active': True,
})
env['ir.config_parameter'].set_param('web.base.url', 'https://qualification.invalid')
env.cr.commit()
print('QUALIFICATION_JSON=' + json.dumps({
    'attachment': attachment.id, 'store_fname': attachment.store_fname,
    'cron': cron.id, 'server': server.id,
}))
