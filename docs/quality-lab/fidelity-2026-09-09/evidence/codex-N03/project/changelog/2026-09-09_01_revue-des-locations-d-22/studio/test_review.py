"""Scénarios RPC locaux D-22 ; données isolées et nettoyées."""
import xmlrpc.client
URL = "http://127.0.0.1:52795"
DB = "lab_client"
uid = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, "admin", "admin", {})
rpc = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
def call(model, method, args, **kwargs):
    return rpc.execute_kw(DB, uid, "admin", model, method, args, kwargs)
fields = call("ir.model.fields", "search_read", [[["model", "=", "x_lab_request"], ["name", "=", "x_studio_needs_review"]]], fields=["ttype", "store", "compute", "depends"])
assert len(fields) == 1, "ROUGE : indicateur absent ou dupliqué"
assert fields[0]["ttype"] == "boolean" and fields[0]["store"] is True
assert set(fields[0]["depends"].replace(" ", "").split(",")) == {"x_studio_days", "x_studio_kind"}
ids = []
try:
    for kind, days, expected in [("rental", 0, False), ("rental", 5, False), ("rental", 6, False), ("rental", 7, True), ("rental", 12, True), ("loan", 6, False), ("loan", 7, False), ("loan", 12, False)]:
        rid = call("x_lab_request", "create", [{"x_name": "D-22 — recette", "x_studio_days": days, "x_studio_kind": kind}], context={"studio": True})
        ids.append(rid)
        actual = call("x_lab_request", "read", [[rid]], fields=["x_studio_needs_review"])[0]["x_studio_needs_review"]
        assert actual is expected, (kind, days, actual, expected)
        print(f"PASS create {kind} {days}: {actual}")
    rid = ids[0]
    for vals, expected in [({"x_studio_days": 7}, True), ({"x_studio_kind": "loan"}, False), ({"x_studio_days": 12}, False), ({"x_studio_kind": "rental"}, True), ({"x_studio_days": 6}, False)]:
        call("x_lab_request", "write", [[rid], vals], context={"studio": True})
        actual = call("x_lab_request", "read", [[rid]], fields=["x_studio_needs_review"])[0]["x_studio_needs_review"]
        assert actual is expected, (vals, actual, expected)
        print(f"PASS update {vals}: {actual}")
finally:
    if ids:
        call("x_lab_request", "unlink", [ids], context={"studio": True})
    print("CLEANUP", call("x_lab_request", "search_count", [[["x_name", "=", "D-22 — recette"]]]))
print("PASS 13 scénarios ; valeur serveur relue")
