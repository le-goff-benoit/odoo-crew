"""Créer ou mettre à jour uniquement le booléen D-22, en contexte Studio."""
import json
from pathlib import Path
import xmlrpc.client
URL = "http://127.0.0.1:52795"
DB = "lab_client"
uid = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, "admin", "admin", {})
rpc = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
def call(model, method, args, **kwargs):
    return rpc.execute_kw(DB, uid, "admin", model, method, args, kwargs)
model_ids = call("ir.model", "search", [[["model", "=", "x_lab_request"]]])
assert len(model_ids) == 1
existing = call("ir.model.fields", "search_read", [[["model", "=", "x_lab_request"], ["name", "in", ["x_name", "x_studio_days", "x_studio_kind"]]]], fields=["name"])
assert len(existing) == 3
values = {
    "name": "x_studio_needs_review", "field_description": "Revue requise",
    "model_id": model_ids[0], "ttype": "boolean", "state": "manual",
    "store": True, "readonly": True,
    "depends": "x_studio_days,x_studio_kind",
    "compute": "for record in self:\n    record['x_studio_needs_review'] = record['x_studio_days'] >= 7 and record['x_studio_kind'] == 'rental'",
}
ids = call("ir.model.fields", "search", [[["model", "=", "x_lab_request"], ["name", "=", values["name"]]]])
assert len(ids) <= 1
if ids:
    call("ir.model.fields", "write", [ids, values], context={"studio": True})
else:
    ids = [call("ir.model.fields", "create", [values], context={"studio": True})]
xmlids = call("ir.model.data", "search_read", [[["model", "=", "ir.model.fields"], ["res_id", "=", ids[0]], ["module", "=", "studio_customization"]]], fields=["module", "name", "studio", "noupdate"])
assert len(xmlids) == 1 and xmlids[0]["studio"]
Path(__file__).with_name("created.txt").write_text(xmlids[0]["module"] + "." + xmlids[0]["name"] + "\n")
print(json.dumps({"field": ids[0], "xmlid": xmlids[0], "existing_fields": existing}, indent=2))
