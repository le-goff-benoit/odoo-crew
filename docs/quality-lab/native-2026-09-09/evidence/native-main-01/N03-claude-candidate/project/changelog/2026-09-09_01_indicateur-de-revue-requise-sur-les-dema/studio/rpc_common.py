"""Connexion XML-RPC commune aux scripts Studio de ce point.

Cible par défaut : la copie locale du client (`lab_client`). Rien n'est écrit
ailleurs ; le déploiement staging / production passe par `odoo_pack.py`.
"""
import os
import xmlrpc.client

URL = os.environ.get("ODOO_URL", "http://127.0.0.1:50691")
DB = os.environ.get("ODOO_DB", "lab_client")
LOGIN = os.environ.get("ODOO_LOGIN", "admin")
PASSWORD = os.environ.get("ODOO_PASSWORD", "admin")

MODEL = "x_lab_request"
FIELD = "x_studio_needs_review"
SEED_FIELDS = ("x_name", "x_studio_days", "x_studio_kind")


def connect():
    uid = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(
        DB, LOGIN, PASSWORD, {}
    )
    if not uid:
        raise SystemExit("connexion refusée sur %s / %s" % (URL, DB))
    proxy = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")

    def call(model, method, args, kwargs=None):
        return proxy.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs or {})

    return call


def studio(kwargs=None):
    """Contexte de Studio : Odoo crée lui-même l'identifiant externe.

    web_studio/models/studio_mixin.py:20 — `create` et `write` en contexte
    `studio` déposent un `ir.model.data` dans `studio_customization`.
    """
    kwargs = dict(kwargs or {})
    kwargs.setdefault("context", {})
    kwargs["context"] = dict(kwargs["context"], studio=True)
    return kwargs
