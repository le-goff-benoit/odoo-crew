"""Transport XML-RPC réservé à la copie synthétique décrite dans /work/LAB.md."""

from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4
import subprocess
import xmlrpc.client

URL = 'http://127.0.0.1:43303'
DB = 'lab_client'
MODEL = 'x_lab_request'
FIELD = 'x_studio_needs_review'
CONTEXT = {'studio': True, 'lang': 'en_US'}


class Lab:
    def __init__(self):
        common = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common')
        assert common.version()['server_serie'] == '19.0'
        # Identifiants jetables publiés par LAB.md, exclusivement pour ce banc.
        self.uid = common.authenticate(DB, 'admin', 'admin', {})
        assert self.uid
        self.proxy = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')

    def call(self, model, method, *args, **kwargs):
        kwargs['context'] = CONTEXT
        return self.proxy.execute_kw(DB, self.uid, 'admin', model, method, list(args), kwargs)

    def rows(self, model, domain, fields):
        return self.call(model, 'search_read', domain, fields=fields, order='id')

    def model_id(self):
        rows = self.rows('ir.model', [('model', '=', MODEL)], ['model', 'state'])
        assert len(rows) == 1 and rows[0]['state'] == 'manual'
        return rows[0]['id']

    def xmlids(self, model, rid):
        return self.rows('ir.model.data', [('model', '=', model), ('res_id', '=', rid)],
                         ['module', 'name', 'model', 'res_id', 'studio', 'noupdate'])

    def refresh_access_cache(self):
        result = subprocess.run(
            ['/bridge/labctl', 'shell', str(Path(__file__).with_name('refresh_lab_cache.py'))],
            capture_output=True, text=True, check=True,
        )
        proof = Path(__file__).with_name('proofs')
        proof.mkdir(exist_ok=True)
        with (proof / 'cache-refresh.log').open('a', encoding='utf-8') as log:
            log.write(result.stdout + result.stderr)
        assert 'D22_CACHE_REFRESHED' in result.stdout

    @contextmanager
    def recipe_access(self):
        """ACL de fixture uniquement : le modèle du banc n'a pas d'accès initial."""
        group = self.rows('ir.model.data', [('module', '=', 'base'),
                                          ('name', '=', 'group_system')], ['res_id'])
        assert len(group) == 1
        before = self.rows('ir.model.access', [('model_id.model', '=', MODEL)],
                           ['name', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'])
        acl = self.call('ir.model.access', 'create', {
            'name': 'D-22 — recette ' + uuid4().hex,
            'model_id': self.model_id(), 'group_id': group[0]['res_id'],
            'perm_read': True, 'perm_write': True, 'perm_create': True, 'perm_unlink': True,
        })
        xmlids = self.xmlids('ir.model.access', acl)
        try:
            self.refresh_access_cache()
            yield
        finally:
            self.call('ir.model.access', 'unlink', [acl])
            # Odoo supprime normalement les XML-ID avec l'enregistrement.
            remaining = self.call('ir.model.data', 'search', [('id', 'in', [r['id'] for r in xmlids])])
            if remaining:
                self.call('ir.model.data', 'unlink', remaining)
            self.refresh_access_cache()
            after = self.rows('ir.model.access', [('model_id.model', '=', MODEL)],
                              ['name', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'])
            assert after == before, 'La fixture doit restituer les droits initiaux'
