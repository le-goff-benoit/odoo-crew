import json

# Lecture de la copie synthétique : le modèle initial n'a aucune ACL.
records = env['x_lab_request'].sudo().search([]).read(
    ['x_name', 'x_studio_days', 'x_studio_kind']
)
print('D22_EXISTING ' + json.dumps(records, ensure_ascii=False))
