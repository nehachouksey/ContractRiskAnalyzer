import unittest
from src.brief import make,recorded_line
class BriefTests(unittest.TestCase):
 def fixture(self):
  return {'comparisons':[{'title':'Scope overlap','outcome':'Potential conflict','explanation':'Supported overlap','historical_id':'signed/a','clarification':'Check consent'}],'coverage':[],'assessments':[],'decisions':[]}
 def test_suggestion_is_not_human_decision(self):
  b=make(self.fixture()); self.assertIsNone(b['recorded']); self.assertIn('potential-conflict',b['result']); self.assertIn('Assess',b['suggested'])
 def test_recorded_rationale_and_stale_label(self):
  r=self.fixture(); r['decisions']=[{'next_step':'Do not proceed with this draft','text':'Request a revised scope.'}]
  self.assertIn('Do not proceed',recorded_line(r)); self.assertIn('Request a revised scope',recorded_line(r))
  self.assertIn('evidence changed',recorded_line(r,True)); self.assertIn('outdated',make(r,True)['result'])
 def test_missing_coverage_and_empty_not_clearance(self):
  r=self.fixture(); r['coverage']=[{'source_id':'signed/b','status':'incomplete','reason':'Missing report'}]
  self.assertIn('Obtain',make(r)['suggested']); self.assertTrue(make(r)['outstanding'])
  r['comparisons']=[]; self.assertIn('not been cleared',make(r)['result'])
