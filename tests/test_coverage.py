import unittest
from src.coverage import reconcile
class CoverageTests(unittest.TestCase):
 def setUp(self):
  self.docs=[{'id':'signed/a'},{'id':'signed/b'}]
  self.findings=[{'historical_id':'signed/a','outcome':'Potential conflict'}]
 def test_missing_entry_keeps_valid_findings(self):
  raw=[{'source_id':'signed/a','status':'assessed','reason':'Compared sources'}]
  records,issues=reconcile(raw,self.docs,self.findings)
  self.assertEqual([x['status'] for x in records],['assessed','incomplete'])
  self.assertEqual(self.findings[0]['outcome'],'Potential conflict')
 def test_duplicates_and_bad_status(self):
  raw=[{'source_id':'signed/a','status':'assessed','reason':'Compared'}]*2+[{'source_id':'signed/b','status':'done','reason':'Done'}]
  records,_=reconcile(raw,self.docs,self.findings)
  self.assertTrue(all(x['status']=='incomplete' for x in records))
 def test_malformed_and_unknown(self):
  for raw in [None,{},[None],[{'source_id':[]}],[{'source_id':'unknown','status':'assessed'}]]:
   records,issues=reconcile(raw,self.docs,self.findings)
   self.assertEqual(len(records),2); self.assertTrue(issues)
   self.assertTrue(all(x['status']=='incomplete' for x in records))
 def test_contradictions_and_valid_no_candidate(self):
  raw=[{'source_id':'signed/a','status':'no candidate','reason':'None'},{'source_id':'signed/b','status':'no candidate','reason':'No scoped restriction'}]
  records,_=reconcile(raw,self.docs,self.findings)
  self.assertEqual([x['status'] for x in records],['incomplete','no candidate'])
 def test_insufficient_never_complete(self):
  records,_=reconcile([{'source_id':'signed/a','status':'assessed','reason':'Compared'}],self.docs,[{'historical_id':'signed/a','outcome':'Insufficient evidence'}])
  self.assertEqual(records[0]['status'],'incomplete')
