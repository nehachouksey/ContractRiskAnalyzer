import unittest,tempfile
from pathlib import Path
from src import core as c
from src import workflow as w
class WorkflowTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.old=c.STORE; c.STORE=Path(self.tmp.name); c.setup('reviewer','test-password-1234')
 def tearDown(self): c.STORE=self.old; self.tmp.cleanup()
 def run_record(self,outcome='No conflict identified in this comparison'):
  return {'id':'workflow','reviewer':'reviewer','created':c.now(),'snapshot':c.snapshot('reviewer'),'comparisons':[{'outcome':outcome}], 'coverage':[{'status':'assessed'}], 'assessments':[{'comparison':0,'action':'Confirm finding','rationale':'Evidence checked'}],'decisions':[]}
 def test_complete_persist_and_lock(self):
  r=self.run_record(); c.complete_review('reviewer',r,'Reviewed current evidence','Refer to authorised signatory for a signing decision')
  self.assertEqual(w.status(c.history('reviewer')[0],c.snapshot('reviewer')),'Review completed')
  with self.assertRaises(ValueError): c.assessment('reviewer',r,0,'Confirm finding','Revised')
  with self.assertRaises(ValueError): c.complete_review('reviewer',r,'Again','Do not proceed with this draft')
  self.assertEqual(w.status(r,{}),'Outdated evidence')
 def test_backend_blocks_missing_stale_and_followup(self):
  for field,value in [('assessments',[]),('snapshot',{}),('coverage',[{'status':'incomplete'}]),('comparisons',[]),('status','analysis_failed')]:
   r=self.run_record(); r[field]=value
   with self.assertRaises(ValueError): c.complete_review('reviewer',r,'Rationale','Refer to authorised signatory for a signing decision')
  r=self.run_record()
  with self.assertRaises(ValueError): c.complete_review('reviewer',r,'Rationale','Request further review')
  with self.assertRaises(ValueError): c.complete_review('reviewer',r,'','Do not proceed with this draft')
 def test_conflict_and_missing_evidence(self):
  r=self.run_record('Potential conflict')
  with self.assertRaises(ValueError): c.complete_review('reviewer',r,'Reviewed','Refer to authorised signatory for a signing decision')
  c.complete_review('reviewer',r,'Confirmed restriction; do not proceed','Do not proceed with this draft')
  r=self.run_record('Insufficient evidence'); r['assessments'][0]['action']='Accept supported risk'
  with self.assertRaises(ValueError): c.complete_review('reviewer',r,'Reviewed','Do not proceed with this draft')
 def test_legacy_status_and_followup(self):
  r=self.run_record(); r['decisions']=[{'text':'Legacy'}]
  self.assertEqual(w.status(r,r['snapshot']),'Human review recorded')
  r['decisions'][-1]['workflow_status']='follow_up'
  self.assertEqual(w.status(r,r['snapshot']),'Follow-up needed')
 def test_specific_queue_actions_and_legacy_choice_mapping(self):
  r=self.run_record('Potential conflict'); r['comparisons'][0]['title']='Test conflict'
  action=w.route(r,r['snapshot'])
  self.assertEqual((action['label'],action['step']),('Resolve 1 risk',3))
  r['assessments']=[]
  action=w.route(r,r['snapshot'])
  self.assertEqual((action['label'],action['step'],action['index']),('Review findings',2,0))
  r['assessments']=[{'comparison':0,'action':'Accept supported risk','rationale':'Authorised acceptance'}]
  self.assertEqual(w.route(r,r['snapshot'])['label'],'Record decision')
  self.assertEqual(w.choice_for('Request contract changes or a specific waiver'),'Need more information')
  self.assertIsNone(w.choice_for(None))
 def test_pending_findings_match_completion_rules(self):
  for outcome in c.OUTCOMES:
   for assessment in c.ACTIONS:
    for next_step in w.DECISION_ACTIONS.values():
     r=self.run_record(outcome); r['assessments'][0]['action']=assessment
     checks=dict((label,passed) for label,passed,_ in w.checklist(r,r['snapshot'],next_step))
     self.assertEqual(not w.pending_findings(r,next_step),checks['Every comparison has an assessment and rationale'] and checks['Outstanding findings are addressed'])
