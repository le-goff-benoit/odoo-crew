"""Raccordement XML-RPC commun aux scripts Studio de cette release.

La copie locale du banc écoute sur un port non standard ; les identifiants sont
ceux, jetables, du bac à sable (`admin`/`admin`). Rien de secret ici : ce
fichier ne sert que sur la copie synthétique `lab_client`.
"""

import os
import xmlrpc.client

URL = os.environ.get("LAB_ODOO_URL", "http://127.0.0.1:46487")
DB = os.environ.get("LAB_ODOO_DB", "lab_client")
LOGIN = os.environ.get("LAB_ODOO_LOGIN", "admin")
PASSWORD = os.environ.get("LAB_ODOO_PASSWORD", "admin")

# Contexte de Studio : c'est lui qui fait créer par Odoo l'identifiant externe
# dans `studio_customization` (web_studio/models/studio_mixin.py).
STUDIO = {"context": {"studio": True}}


def connect():
    """Retourne un appelant `call(modèle, méthode, args, kwargs)` authentifié."""
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, LOGIN, PASSWORD, {})
    if not uid:
        raise SystemExit(f"authentification refusée sur {DB}")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    def call(model, method, args, kwargs=None):
        return models.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs or {})

    return call
