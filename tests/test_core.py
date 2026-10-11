import unittest, tempfile
from pathlib import Path
from src import core as c
class CoreTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.old=c.STORE; c.STORE=Path(self.tmp.name); c.setup('reviewer','a-long-test-password')
 def tearDown(self): c.STORE=self.old; self.tmp.cleanup()
 def test_access(self):
  self.assertTrue(c.login('reviewer','a-long-test-password')); self.assertFalse(c.login('reviewer','wrong'))
  with self.assertRaises(PermissionError): c.documents('stranger','incoming')
  with self.assertRaises(ValueError): c.setup('other','a-long-test-password')
 def test_inventory_and_versions(self):
  self.assertEqual(len(c.documents('reviewer','incoming')),15)
  self.assertEqual(len(c.documents('reviewer','signed_contracts')),17)
  self.assertEqual(c.snapshot('reviewer'),c.snapshot('reviewer'))
 def test_fabricated_evidence_rejected(self):
  docs=[{'id':'incoming/a','version':'v','text':'original'}, {'id':'signed_contracts/b','version':'v','text':'signed'}]
  f={'outcome':'Potential conflict','title':'test','explanation':'test','scope':'test','dates':'test','clarification':'test','historical_id':'signed_contracts/b','evidence':[{'source_id':'incoming/a','quote':'invented'}]}
  with self.assertRaises(ValueError): c.validate({'comparisons':[f]},docs)
 def test_history_stale_and_rationale(self):
  run={'id':'run','reviewer':'reviewer','created':c.now(),'snapshot':c.snapshot('reviewer'),'comparisons':[{'outcome':'Potential conflict'}]}
  with self.assertRaises(ValueError): c.assessment('reviewer',run,0,'Confirm finding','')
  c.assessment('reviewer',run,0,'Confirm finding','Evidence inspected')
  self.assertEqual(c.history('reviewer')[0]['assessments'][0]['rationale'],'Evidence inspected')
  run['snapshot']={}
  with self.assertRaises(ValueError): c.decision('reviewer',run,'Decision')
if __name__=='__main__': unittest.main()

class PassageTests(unittest.TestCase):
 def test_resolve_exact_text_without_model_copying(self):
  docs=[{'id':'incoming/a','version':'v1','text':'# Draft\n\nExact **wording** — includes punctuation.\n'}, {'id':'signed_contracts/b','version':'v2','text':'# Signed\n\nOriginal commitment.\n'}]
  f={'outcome':'Potential conflict','title':'test','explanation':'test','scope':'test','dates':'test','clarification':'test','historical_id':'signed_contracts/b','evidence':[{'source_id':d['id'],'passage_id':'p1'} for d in docs]}
  result=c.validate({'comparisons':[f]},docs)
  self.assertEqual(result['comparisons'][0]['evidence'][0]['quote'],docs[0]['text'])
 def test_invalid_passage_rejected(self):
  docs=[{'id':'signed_contracts/b','version':'v','text':'original'}]
  f={'outcome':'Insufficient evidence','title':'test','explanation':'test','scope':'test','dates':'test','clarification':'test','historical_id':'signed_contracts/b','evidence':[{'source_id':'signed_contracts/b','passage_id':'p99'}]}
  with self.assertRaises(ValueError): c.validate({'comparisons':[f]},docs)

class UploadTests(CoreTests):
 def test_upload_persistence_and_dedup(self):
  sid=c.upload_contract('reviewer','../../client.txt',b'# New agreement\nComplete text.','New client')
  self.assertTrue(sid.startswith('incoming/upload-'))
  self.assertEqual(sid,c.upload_contract('reviewer','client.md',b'# New agreement\nComplete text.','New client'))
  items=[d for d in c.documents('reviewer','incoming') if d.get('uploaded')]
  self.assertEqual(len(items),1)
  self.assertEqual(items[0]['text'],'# New agreement\nComplete text.')
  self.assertIn(sid,c.snapshot('reviewer'))
 def test_upload_rejections(self):
  for name,data in [('a.pdf',b'pdf'),('a.md',b''),('a.txt',b'\x00binary'),('a.md',b'\xff'),('a.md',b'a'*(2*1024*1024+1))]:
   with self.assertRaises(ValueError): c.upload_contract('reviewer',name,data,'Test')
  with self.assertRaises(PermissionError): c.upload_contract('stranger','a.md',b'text','Test')

class OriginalUploadTests(CoreTests):
 def test_original_download_and_old_schema_migration(self):
  with c.db() as conn:
   conn.execute('DROP TABLE uploads')
   conn.execute('CREATE TABLE uploads (id TEXT PRIMARY KEY, reviewer TEXT, name TEXT, content TEXT, version TEXT, created TEXT, UNIQUE(reviewer,version))')
  sid=c.upload_contract('reviewer','client.txt',b'Original terms','Client')
  self.assertEqual(c.original_upload('reviewer',sid),('client.txt',b'Original terms'))
  with self.assertRaises(PermissionError): c.original_upload('unauthorised',sid)
