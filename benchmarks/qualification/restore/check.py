import base64
import json

attachment = env['ir.attachment'].search([('name', '=', 'qualification-proof.txt')])
cron = env['ir.cron'].with_context(active_test=False).search([('name', '=', 'qualification cron')])
server = env['ir.mail_server'].with_context(active_test=False).search([('name', '=', 'qualification mail')])
admin = env['res.users'].browse(2)
params = env['ir.config_parameter']
print('QUALIFICATION_JSON=' + json.dumps({
    'attachment_bytes': len(attachment) == 1 and base64.b64decode(attachment.datas) == b'qualification attachment: restore and filestore, 2026-09-09\n',
    'cron_disabled': len(cron) == 1 and not cron.active,
    'mail_disabled': len(server) == 1 and not server.active,
    'neutralized': params.get_param('database.is_neutralized') == 'true',
    'admin_active': admin.active and admin.login == 'admin',
    'local_url': params.get_param('web.base.url') == 'http://localhost:8079',
    'url_frozen': params.get_param('web.base.url.freeze') == 'True',
}))
