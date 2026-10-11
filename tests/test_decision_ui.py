"""Regression journeys for the simplified decision screen, using isolated data."""
import tempfile,unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src import core as c, workflow as w

class DecisionJourneyTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.old=c.STORE; c.STORE=Path(self.temp.name)
  c.setup('tester','test-only-password-123')
  self.incoming=c.documents('tester','incoming')[0]
  historical=c.documents('tester','signed_contracts')[0]
  self.run={'id':'decision-journey','reviewer':'tester','created':c.now(),'incoming_id':self.incoming['id'],'name':self.incoming['name'],'version':self.incoming['version'],'context':{'entity':'Test entity','scope':'Test scope','review_date':'2026-09-28'},'snapshot':c.snapshot('tester'),'duration':0,'coverage':[{'source_id':historical['id'],'status':'assessed','reason':'Test fixture'}],'comparisons':[{'historical_id':historical['id'],'outcome':'Potential conflict','title':f'Test risk {i+1}','explanation':'Synthetic UI test only','scope':'Test scope','dates':'Test dates','clarification':'None','evidence':[]} for i in range(2)],'assessments':[{'comparison':i,'action':'Confirm finding','rationale':'Supported conflict confirmed','reviewer':'tester','time':c.now()} for i in range(2)],'decisions':[]}
 def tearDown(self): c.STORE=self.old; self.temp.cleanup()
 def open(self):
  c.save('tester',self.run)
  app=AppTest.from_file('app.py',default_timeout=60)
  for key,value in {'user':'tester','active':self.incoming['id'],'run':self.run,'page':'Review workspace','step_'+self.incoming['id']:3}.items(): app.session_state[key]=value
  app.run(); self.assertFalse(app.exception)
  return app
 def choose(self,app,choice):
  next(r for r in app.radio if r.label=='Your decision').set_value(choice).run()
  self.assertFalse(app.exception)
 def save(self,app,reason):
  next(t for t in app.text_area if t.label=='Why is this your decision?').set_value(reason).run()
  next(x for x in app.checkbox if x.label.startswith('I have reviewed')).check().run()
  next(b for b in app.button if b.key=='save_review_decision').click().run()
  self.assertFalse(app.exception)
 def test_proceed_blocked_opens_exact_risk_and_preserves_drafts(self):
  app=self.open()
  self.assertTrue(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.choose(app,'Proceed for signing approval')
  self.assertTrue(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.assertEqual([b.label for b in app.button if (b.key or '').startswith('resolve_finding_')],['Open finding 1','Open finding 2'])
  next(t for t in app.text_area if t.label=='Why is this your decision?').set_value('Draft decision rationale').run()
  next(b for b in app.button if b.label=='Open finding 2').click().run()
  self.assertTrue(any(x.value=='Finding 2 of 2' for x in app.subheader))
  next(b for b in app.button if b.label=='3. Record decision').click().run()
  self.assertEqual(next(r for r in app.radio if r.label=='Your decision').value,'Proceed for signing approval')
  self.assertEqual(next(t for t in app.text_area if t.label=='Why is this your decision?').value,'Draft decision rationale')
  self.assertEqual(c.history('tester')[0]['decisions'],[])
 def test_do_not_proceed_completes_confirmed_conflicts_and_queue_views_decision(self):
  app=self.open(); self.choose(app,'Do not proceed')
  self.assertFalse(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.assertFalse(any((b.key or '').startswith('resolve_finding_') for b in app.button))
  self.save(app,'Confirmed restrictions; stop this draft')
  saved=c.history('tester')[0]
  self.assertEqual(saved['completion']['next_step'],'Do not proceed with this draft')
  self.assertTrue(all(a['action']=='Confirm finding' for a in saved['assessments']))
  app.run()
  next(r for r in app.radio if r.label=='Workspace navigation').set_value('Contracts').run()
  contract=next(b for b in app.button if b.key==self.incoming['id'])
  self.assertEqual(contract.label,'View decision')
  contract.click().run()
  self.assertFalse(app.exception)
  self.assertTrue(any('Review completed for this evidence snapshot' in x.value for x in app.success))
  self.assertFalse(any(b.key=='save_review_decision' for b in app.button))
 def test_followup_explicitly_remains_open_with_unfinished_checks(self):
  self.run['coverage'][0]['status']='incomplete'; self.run['assessments']=[]
  app=self.open(); self.choose(app,'Do not proceed')
  self.assertTrue(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.choose(app,'Need more information')
  self.assertFalse(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.save(app,'Obtain the missing schedule from the counterparty')
  saved=c.history('tester')[0]
  self.assertNotIn('completion',saved)
  self.assertEqual(saved['decisions'][-1]['workflow_status'],'follow_up')
  self.assertIn('missing schedule',saved['decisions'][-1]['text'])
  self.assertEqual(w.status(saved,c.snapshot('tester')),'Follow-up needed')
 def test_proceed_completes_only_explicitly_accepted_risks(self):
  for assessment in self.run['assessments']: assessment['action']='Accept supported risk'
  app=self.open(); self.choose(app,'Proceed for signing approval')
  self.assertFalse(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.save(app,'Authorised risk acceptance recorded; refer for a signing decision')
  self.assertEqual(c.history('tester')[0]['completion']['next_step'],'Refer to authorised signatory for a signing decision')
 def test_stale_review_cannot_save_any_decision(self):
  self.run['snapshot']={}
  app=self.open()
  for choice in w.DECISIONS:
   self.choose(app,choice)
   self.assertTrue(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.assertEqual(c.history('tester')[0]['decisions'],[])
 def test_disputed_finding_cannot_be_closed_by_do_not_proceed(self):
  self.run['assessments'][1]['action']='Mark finding incorrect'
  app=self.open(); self.choose(app,'Do not proceed')
  self.assertTrue(next(b for b in app.button if b.key=='save_review_decision').disabled)
  self.assertEqual([b.label for b in app.button if (b.key or '').startswith('resolve_finding_')],['Open finding 2'])

 def test_reason_and_acknowledgement_required_for_followup(self):
  app=self.open(); self.choose(app,'Need more information')
  next(b for b in app.button if b.key=='save_review_decision').click().run()
  self.assertTrue(any('rationale' in e.value for e in app.error))
  next(t for t in app.text_area if t.label=='Why is this your decision?').set_value('Request clarification').run()
  next(b for b in app.button if b.key=='save_review_decision').click().run()
  self.assertTrue(any('Confirm that' in e.value for e in app.error))
  self.assertEqual(c.history('tester')[0]['decisions'],[])
