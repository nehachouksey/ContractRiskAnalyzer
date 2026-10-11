import unittest
from src.summary import build
class SummaryTests(unittest.TestCase):
 def fixture(self):
  return {'comparisons':[{'title':'Hotel scope','outcome':'Potential conflict','explanation':'Possible overlap','historical_id':'signed/a','clarification':'Obtain consent'}],'assessments':[],'coverage':[]}
 def test_unassessed_and_confirmed_conflicts_need_action(self):
  run=self.fixture(); self.assertEqual(len(build(run)['unresolved']),1)
  run['assessments']=[{'comparison':0,'action':'Confirm finding','rationale':'Checked'}]
  self.assertEqual(len(build(run)['unresolved']),1)
 def test_accepted_risk_remains_visible(self):
  run=self.fixture(); run['assessments']=[{'comparison':0,'action':'Accept supported risk','rationale':'Reason'}]
  s=build(run); self.assertEqual(len(s['accepted']),1); self.assertEqual(len(s['conflicts']),1)
  self.assertIn('signatory',s['headline'])
 def test_missing_stale_and_empty_never_clear(self):
  run=self.fixture(); run['comparisons'][0]['outcome']='Insufficient evidence'
  self.assertIn('Clarification',build(run)['headline']); self.assertIn('Reanalyse',build(run,True)['headline'])
  run['comparisons']=[]; self.assertIn('No comparison',build(run)['headline'])
