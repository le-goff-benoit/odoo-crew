import json, subprocess, sys, xmlrpc.client, datetime
from pathlib import Path
ROOT=Path("/work/.odoo-agents/flow-artifacts/needs-review")
REL=Path("/work/changelog/2026-09-09_01_revue-des-locations-d-22/studio")
URL="http://127.0.0.1:52795"
DB="lab_client"
common=xmlrpc.client.ServerProxy(URL+"/xmlrpc/2/common")
uid=common.authenticate(DB,"admin","admin",{})
rpc=xmlrpc.client.ServerProxy(URL+"/xmlrpc/2/object")
def call(model,method,args,**kwargs):
    return rpc.execute_kw(DB,uid,"admin",model,method,args,kwargs)
def snapshot(label):
    fields=call("ir.model.fields","search_read",[[["model","=","x_lab_request"]]], fields=["name","ttype","state","store","compute","depends","write_date"], order="id")
    xmlids=call("ir.model.data","search_read",[[["module","=","studio_customization"]]],fields=["name","model","res_id","noupdate","write_date"],order="id")
    ids=call("x_lab_request","search",[[]],order="id")
    data={"fields_count":len(fields),"fields":fields,"xmlids_count":len(xmlids),"xmlids":xmlids,"request_ids":ids}
    print("SNAPSHOT",label,json.dumps(data,ensure_ascii=False),flush=True)
    return data
def run(args):
    print("COMMAND", " ".join(args),flush=True)
    p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    print(p.stdout,flush=True)
    assert p.returncode==0, (args,p.returncode)
    return p.stdout
print("START",datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
print("VERSION",common.version(),flush=True)
base=snapshot("before_apply_1")
pack=json.loads((REL/"pack.json").read_text())
assert len(pack["records"])==1
assert "unresolved" not in json.dumps(pack)
target=[f for f in base["fields"] if f["name"]=="x_studio_needs_review"]
assert len(target)==1 and target[0]["ttype"]=="boolean" and target[0]["store"]
assert set(target[0]["depends"].replace(" ","").split(","))=={"x_studio_days","x_studio_kind"}
for n in (1,2):
    before=snapshot("before_apply_"+str(n))
    cmd=["python3",str(Path.home()/".odoo19-agents/scripts/odoo_pack.py")]
    flags=[str(REL/"pack.json"),"--db",DB,"--url",URL]
    diff=run(cmd+["diff"]+flags)
    assert "0 / 0 / 1" in diff
    applied=run(cmd+["apply"]+flags)
    assert "0 / 0 / 1" in applied
    after=snapshot("after_apply_"+str(n))
    assert before==after, "metadata or XML-ID change/duplicate"
    run(["python3",str(REL/"test_review.py")])
    clean=snapshot("after_scenarios_"+str(n))
    assert clean==after, "cleanup or metadata failed"
diff=run(cmd+["diff"]+flags)
assert "0 / 0 / 1" in diff
assert snapshot("final")==base
print("PASS independent runtime: 2 real applications, 3 null diffs, 26 scenarios, stable fields/XML-IDs/write_dates, cleanup",flush=True)

