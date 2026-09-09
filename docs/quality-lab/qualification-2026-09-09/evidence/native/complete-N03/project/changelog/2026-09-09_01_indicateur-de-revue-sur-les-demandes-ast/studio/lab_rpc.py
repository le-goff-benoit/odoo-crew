"""Transport XML-RPC partagé par les scripts Studio de ce point.

Cible par défaut : la copie locale du client (banc synthétique).
Surchargeable par ODOO_URL / ODOO_DB / ODOO_LOGIN / ODOO_PASSWORD.
"""

import os
import xmlrpc.client

URL = os.environ.get("ODOO_URL", "http://127.0.0.1:48687")
DB = os.environ.get("ODOO_DB", "lab_client")
LOGIN = os.environ.get("ODOO_LOGIN", "admin")
PASSWORD = os.environ.get("ODOO_PASSWORD", "admin")

MODEL = "x_lab_request"
FIELD = "x_studio_needs_review"
DEPENDS = "x_studio_days,x_studio_kind"

# Ce que Studio écrirait dans l'éditeur de champ calculé, à l'identique :
# une boucle explicite sur self, une affectation par clé, aucune importation.
COMPUTE = (
    "for record in self:\n"
    "    record['x_studio_needs_review'] = "
    "record['x_studio_days'] >= 7 and record['x_studio_kind'] == 'rental'\n"
)

# Contexte Studio : Odoo marque lui-même l'enregistrement et lui crée
# son identifiant externe dans studio_customization (web_studio/models/studio_mixin.py).
STUDIO = {"context": {"studio": True}}


def connect():
    common = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
    uid = common.authenticate(DB, LOGIN, PASSWORD, {})
    if not uid:
        raise SystemExit(f"authentification refusée sur {DB}@{URL}")
    proxy = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")

    def call(model, method, args, kwargs=None):
        return proxy.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs or {})

    return call
