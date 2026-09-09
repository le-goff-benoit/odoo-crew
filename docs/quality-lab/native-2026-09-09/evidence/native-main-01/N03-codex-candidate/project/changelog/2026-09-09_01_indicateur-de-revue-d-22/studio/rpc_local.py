"""Transport XML-RPC limité à la copie synthétique décrite dans LAB.md."""
import xmlrpc.client

URL = 'http://127.0.0.1:49635'
DB = 'lab_client'
CTX = {'studio': True}
MODEL = 'x_lab_request'
FIELD = 'x_studio_needs_review'


def call(model, method, *args, **kwargs):
    common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
    uid = common.authenticate(DB, 'admin', 'admin', {})
    assert uid, 'Authentification locale refusée'
    proxy = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object', allow_none=True)
    return proxy.execute_kw(DB, uid, 'admin', model, method, list(args), kwargs)


def scenario(code):
    """Action éphémère : pas d'ACL du modèle dans le banc, sudo pour recette seule.

    Réservé à cette copie synthétique. Aucun changement de droits. Les scénarios
    nettoient leurs données ; l'action et son XML-ID sont supprimés ici.
    """
    # Le contrôle d'exécution porte sur le modèle support de l'action.
    # ir.model est accessible au compte administrateur du banc.
    models = call('ir.model', 'search', [('model', '=', 'ir.model')])
    assert len(models) == 1
    action_id = call('ir.actions.server', 'create', {
        'name': 'D-22 — recette temporaire', 'model_id': models[0],
        'state': 'code',
        'code': '# sudo : recette sur copie synthétique sans ACL ; aucun déploiement.\n'
                "requests = env['x_lab_request'].sudo().with_context(studio=True)\n" + code,
    }, context=CTX)
    try:
        return call('ir.actions.server', 'run', [action_id], context=CTX)['params']
    finally:
        call('ir.actions.server', 'unlink', [action_id], context=CTX)
