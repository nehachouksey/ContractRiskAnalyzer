import unittest
from src.analysis_recovery import recover
from src.core import validate

class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.incoming={'id':'incoming/draft','version':'v','text':'# Draft\nHotel analytics in Dubai.'}
  self.signed=[{'id':f'signed_contracts/{i}','version':'v','text':'# Agreement\nRelevant original terms.'} for i in range(6)]
  self.docs=[self.incoming]+self.signed
 def finding(self,sid,invalid=False):
  return {'historical_id':sid,'outcome':'Potential conflict','title':'Supported conflict','explanation':'Overlap','scope':'Hotel analytics','dates':'Current','clarification':'None','evidence':[{'source_id':self.incoming['id'],'passage_id':'p1'},{'source_id':sid,'passage_id':'p99' if invalid else 'p1'}]}
 def result(self):
  return {'comparisons':[self.finding(self.signed[0]['id'])],'coverage':[{'source_id':d['id'],'status':'assessed','reason':'Compared'} for d in self.signed]}
 def test_missing_outputs_checked_in_bounded_batches(self):
  batches=[]
  def request(ids):
   batches.append(ids)
   return {'comparisons':[],'coverage':[{'source_id':sid,'status':'no candidate','reason':'No scoped restriction retrieved in this agreement'} for sid in ids]}
  result=recover(self.result(),self.signed,self.docs,request,validate,lambda _:None,batch_size=2)
  self.assertEqual([len(b) for b in batches],[2,2,1])
  self.assertEqual(len(result['comparisons']),1)
  self.assertEqual(result['coverage'][0]['status'],'assessed')
  self.assertTrue(all(r['status']=='no candidate' for r in result['coverage'][1:]))
  self.assertEqual(result['automatic_followup']['documents_completed'],5)
 def test_valid_recovered_finding_resolves_exact_passages(self):
  def request(ids):
   return {'comparisons':[self.finding(sid) for sid in ids],'coverage':[{'source_id':sid,'status':'assessed','reason':'Compared exact sources'} for sid in ids]}
  result=recover(self.result(),self.signed,self.docs,request,validate,lambda _:None)
  self.assertEqual(len(result['comparisons']),6)
  self.assertTrue(all(r['status']=='assessed' for r in result['coverage']))
  self.assertEqual(result['comparisons'][1]['evidence'][0]['quote'],self.incoming['text'])
 def test_invalid_citations_cannot_become_clear(self):
  def request(ids):
   return {'comparisons':[self.finding(sid,True) for sid in ids],'coverage':[{'source_id':sid,'status':'no candidate','reason':'Nothing'} for sid in ids]}
  result=recover(self.result(),self.signed,self.docs,request,validate,lambda _:None)
  self.assertEqual(len(result['comparisons']),1)
  self.assertTrue(all(r['status']=='incomplete' for r in result['coverage'][1:]))
 def test_failure_preserves_initial_and_missing_evidence_not_relabelled(self):
  result=self.result(); result['comparisons'][0]['outcome']='Insufficient evidence'
  calls=[]
  def request(ids): calls.extend(ids); raise TimeoutError()
  result=recover(result,self.signed,self.docs,request,validate,lambda _:None)
  self.assertNotIn(self.signed[0]['id'],calls)
  self.assertEqual(result['comparisons'][0]['outcome'],'Insufficient evidence')
  self.assertTrue(all(r['status']=='incomplete' for r in result['coverage']))
 def test_citation_repair_is_bounded_and_validated(self):
  repaired=[]
  def request(ids):
   findings=[self.finding(sid) for sid in ids]
   for f in findings: f['evidence']=f['evidence'][1:]
   return {'comparisons':findings,'coverage':[{'source_id':sid,'status':'assessed','reason':'Compared'} for sid in ids]}
  def repair(ids,feedback):
   repaired.append(ids)
   self.assertTrue(feedback['errors'])
   return {'comparisons':[self.finding(sid) for sid in ids],'coverage':[{'source_id':sid,'status':'assessed','reason':'Compared'} for sid in ids]}
  result=recover(self.result(),self.signed,self.docs,request,validate,lambda _:None,repair=repair)
  self.assertEqual(len(repaired),2)
  self.assertEqual(len(result['comparisons']),6)
  self.assertTrue(all(r['status']=='assessed' for r in result['coverage']))
 def test_bad_repair_does_not_bypass_validation(self):
  def response(ids,*args):
   return {'comparisons':[self.finding(sid,True) for sid in ids],'coverage':[{'source_id':sid,'status':'assessed','reason':'Compared'} for sid in ids]}
  result=recover(self.result(),self.signed,self.docs,response,validate,lambda _:None,repair=response)
  self.assertEqual(len(result['comparisons']),1)
  self.assertTrue(all(r['status']=='incomplete' for r in result['coverage'][1:]))
