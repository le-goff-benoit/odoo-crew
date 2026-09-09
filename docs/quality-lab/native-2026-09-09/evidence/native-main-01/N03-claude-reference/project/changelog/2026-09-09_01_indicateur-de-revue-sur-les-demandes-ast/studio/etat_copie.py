import xmlrpc.client, sys
u='http://127.0.0.1:46487'; db='lab_client'; pw='admin'
uid=xmlrpc.client.ServerProxy(u+'/xmlrpc/2/common').authenticate(db,'admin',pw,{})
m=xmlrpc.client.ServerProxy(u+'/xmlrpc/2/object')
def k(*a,**kw): return m.execute_kw(db,uid,pw,*a,**kw)
f=k('ir.model.fields','search_read',[[('model','=','x_lab_request')]],{'fields':['name','ttype','store','depends']})
print('champs du modèle :', sorted(x['name'] for x in f))
print('occurrences de x_studio_needs_review :', sum(1 for x in f if x['name']=='x_studio_needs_review'))
d=k('ir.model.data','search_read',[[('module','=','studio_customization')]],{'fields':['name','model','res_id','noupdate','studio']})
print('identifiants externes studio_customization :', len(d))
for x in sorted(d,key=lambda r:r['name']): print('   ', x['name'], '| noupdate=',x['noupdate'],'| studio=',x['studio'])
print('modèles x_lab_request en ir.model :', k('ir.model','search_count',[[('model','=','x_lab_request')]]))
