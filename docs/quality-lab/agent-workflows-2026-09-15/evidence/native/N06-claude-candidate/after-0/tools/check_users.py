for login in ('n06_operator', 'n06_restricted'):
    u = env['res.users'].sudo().search([('login', '=', login)])
    print(login, 'id=', u.id, 'company=', u.company_id.name, 'companies=', u.company_ids.mapped('name'))
    print('   groups:', sorted(u.group_ids.mapped('full_name'))[:12])
    print('   is_admin:', u._is_admin(), 'is_system:', u._is_system())
