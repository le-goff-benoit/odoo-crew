"""Remet volontairement la règle D-21 (5 jours, tous types) pour vérifier que le
scénario de recette sait devenir rouge. Non livré : outil de contrôle."""
import xmlrpc.client
u='http://127.0.0.1:46487'; db='lab_client'; pw='admin'
uid=xmlrpc.client.ServerProxy(u+'/xmlrpc/2/common').authenticate(db,'admin',pw,{})
m=xmlrpc.client.ServerProxy(u+'/xmlrpc/2/object')
def k(*a,**kw): return m.execute_kw(db,uid,pw,*a,**kw)
fid=k('ir.model.fields','search',[[('model','=','x_lab_request'),('name','=','x_studio_needs_review')]])[0]
k('ir.model.fields','write',[[fid],{'compute':
  "for record in self:\n    record['x_studio_needs_review'] = (record['x_studio_days'] or 0) >= 5\n"}],
  {'context':{'studio':True}})
print('règle D-21 (5 jours, tous types) remise en place sur le champ', fid)
