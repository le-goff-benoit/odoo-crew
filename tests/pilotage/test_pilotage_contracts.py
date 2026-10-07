"""Business mutations, durable learning and reserve retention on synthetic projects."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_pilotage as p
import odoo_knowledge as k
from odoo_documents import reference

class PilotageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        folder = self.root / 'changelog/R1'; folder.mkdir(parents=True)
        (folder/'README.md').write_text('<!-- release ouverte -->')
        (folder/'plan.json').write_text(json.dumps({'tasks':[{'id':'T1','scopes':['module']}]}))

    def file(self, name, value):
        path=self.root/name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value)); return reference(self.root,name)

    def test_business_mutations_are_rejected(self):
        contract=self.file('contract.json', {'schema':1,'reviewed_by':'independent','basis':'signed example',
            'cases':[{'id':'one','population':[1,2],'expected':{'allowed':False,'net':'120.00'}}]})
        good={'cases':[{'id':'one','population':[1,2],'observed':{'allowed':False,'net':'120.00'}}]}
        self.assertTrue(p.business_results(self.root,contract,self.file('observed.json',good))['passed'])
        for value in [0, None, True]:
            bad=json.loads(json.dumps(good)); bad['cases'][0]['observed']['allowed']=value
            with self.assertRaises(ValueError): p.business_results(self.root,contract,self.file('observed.json',bad))
        good['cases'][0]['population']=[True,2]
        with self.assertRaises(ValueError): p.business_results(self.root,contract,self.file('observed.json',good))

    def test_readiness_never_assumes_missing_browser(self):
        definition={'schema':1,'series':'19.0','environment':'local','required':['browser'],'checks':[]}
        self.assertFalse(p.readiness(self.root,definition)['ready'])
        definition['checks']=[{'id':'browser','status':'available','evidence':self.file('browser.json',
            {'series':'19.0','environment':'local','capability':'browser','available':True})}]
        self.assertTrue(p.readiness(self.root,definition)['ready'])
        definition['environment']='staging'
        with self.assertRaises(ValueError): p.readiness(self.root,definition)

    def test_reserves_need_resolution_and_do_not_mean_deployed(self):
        ref=self.file('publication.json', {'published':True})
        reserve={'missing_control':'browser','next_action':'run on local copy','owner':'tester'}
        row={'status':'published_with_reservations','target':'github','tasks':['T1'],
             'evidence':ref,'decision':ref,'reservations':[reserve]}
        p.delivery_record(self.root,'R1',row)
        self.assertFalse(p.delivery_snapshot(self.root,'R1')['verified'])
        simple={k:v for k,v in row.items() if k not in ('decision','reservations')}; simple['status']='published'
        with self.assertRaises(ValueError):p.delivery_record(self.root,'R1',simple)
        simple['resolutions']=[{'reservation':reserve,'result':'browser passed','evidence':ref}]
        p.delivery_record(self.root,'R1',simple)
        self.assertEqual(len(json.loads((self.root/'changelog/R1/delivery-status.json').read_text())['history']),1)
        simple['tasks']=['unknown']
        with self.assertRaises(ValueError):p.delivery_record(self.root,'R1',simple)

    def test_discovery_projection_idempotent_tamper_and_fresh_brief(self):
        source=self.file('review.json', {'review':'accepted'})
        row={'schema':1,'id':'lesson','kind':'discovery','state':'accepted','statement':'Use rounded totals',
             'author':'analyst','scope':[],'sources':[source],'review':source,'reviewed_by':'reviewer',
             'effect':'Compare saved totals','exceptions':['Historical imports']}
        k.publish(self.root,'R1',row); k.publish(self.root,'R1',row)
        self.assertEqual(len(p.learnings(self.root)),1)
        self.assertIn('Use rounded totals', k.brief(self.root,'R1')['text'])
        path=self.root/'.odoo-agents/LEARNINGS.json'; data=json.loads(path.read_text())
        data['items'][0]['statement']='Invented'; path.write_text(json.dumps(data))
        self.assertFalse(p.learnings(self.root)[0]['current'])

    def test_read_cache_refresh_and_copy_isolation(self):
        calls=[]
        def reader(plan, root):calls.append(1);return {'T1':['validated','']}
        with p.read_session():
            p.cached_statuses({}, self.root, reader)['T1'][0]='stale'
            self.assertEqual(p.cached_statuses({},self.root,reader)['T1'][0],'validated')
            with p.read_session():p.cached_statuses({},self.root,reader)
        self.assertEqual(len(calls),1)
        with p.read_session():p.cached_statuses({},self.root,reader)
        self.assertEqual(len(calls),2)

    def test_express_registry_preserves_cross_release_attribution(self):
        import odoo_effort as effort
        from tests.pilotage.test_odoo_effort import EffortTests
        flow=self.root/'.odoo-agents/flows/caption.json'; flow.parent.mkdir(parents=True)
        flow.write_text('{"kind":"express"}')
        result=effort.express_init(self.root,'.odoo-agents/flows/caption.json','Corriger le libellé')
        folder=Path(result['folder'])
        self.assertEqual(effort.location(folder)[1],self.root)
        self.assertEqual(effort.report_data(folder,effort.state(folder))['missing_tasks'],['EXPRESS'])
        with patch.object(effort,'normalized_usage',return_value=EffortTests.usage(self)):
            effort.import_usage(folder,'EXPRESS','odoo-developer','codex','native')
            (self.root/'changelog/R1/plan.json').unlink()
            effort.init(self.root/'changelog/R1')
            effort.add_task(self.root/'changelog/R1','T1','Tâche')
            with self.assertRaisesRegex(ValueError,'déjà attribuée'):
                effort.import_usage(self.root/'changelog/R1','T1','odoo-developer','codex','native')

    def test_long_tool_does_not_stop_native_collection(self):
        import odoo_effort_watch as watcher
        binding=self.root/'binding.json'; binding.write_text('{}')
        pending={'status':'incomplete','source_sha256':'one'}
        with patch.object(watcher,'sample',side_effect=[pending,pending,{'status':'sealed'}]) as sample, \
             patch.object(watcher.time,'monotonic',side_effect=[0,1,10000,10001]), \
             patch.object(watcher.time,'sleep'):
            watcher.watch(binding,idle_seconds=10)
        self.assertEqual(sample.call_count,3)

    def test_answered_questions_remain_visible_without_blocking_plan(self):
        import odoo_intentions as intentions
        data={'schema':1,'items':[{'id':'I1','text':'Demande','purpose':'Résultat','source':{'sha256':'x'},
            'status':'planned','questions':[{'text':'Quelle société ?','answer':'B'}],
            'constraints':[],'decisions':[],'tasks':['T1']}]}
        intentions.validate_data(data)
        self.assertEqual(intentions.open_questions(data['items'][0]),[])
        data['items'][0]['questions'][0]['answer']=''
        with self.assertRaises(ValueError):intentions.validate_data(data)
