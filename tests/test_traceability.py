import tempfile,unittest
from pathlib import Path
from src import core as c
from src.history import groups

class TraceabilityTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.old=c.STORE; c.STORE=Path(self.temp.name)
  c.setup('tester','test-password-long-enough')
 def tearDown(self):
  c.STORE=self.old; self.temp.cleanup()
 def test_stable_id_exact_saved_document_and_search(self):
  source=c.upload_contract('tester','draft.txt',b'Original reviewed contract','Test contract')
  doc=next(d for d in c.documents('tester','incoming') if d['id']==source)
  run={'id':'test-run','reviewer':'tester','created':c.now(),'incoming_id':source,'version':doc['version'],'name':'Test contract','snapshot':{},'decisions':[]}
  c.save('tester',run); reference=run['review_id']
  c.save('tester',run)
  self.assertEqual(c.history('tester')[0]['review_id'],reference)
  self.assertEqual(reference,'REV-000001')
  with c.db() as conn:
   conn.execute('INSERT INTO sources VALUES (?,?,?)',(source,'new-version','Changed text'))
  saved=c.reviewed_document('tester',run['id'])
  self.assertEqual(saved['data'],b'Original reviewed contract')
  self.assertEqual(saved['text'],'Original reviewed contract')
  self.assertEqual(saved['filename'],'draft.txt')
  self.assertEqual(len(groups(c.history('tester'),{},reference)),1)
  with self.assertRaises(PermissionError): c.reviewed_document('tester','missing-review')
 def test_legacy_review_gets_stable_reference(self):
  import json
  legacy={'id':'legacy','reviewer':'tester','created':c.now()}
  with c.db() as conn: conn.execute('INSERT INTO runs VALUES (?,?,?,?)',('legacy','tester',legacy['created'],json.dumps(legacy)))
  first=c.history('tester')[0]['review_id']
  self.assertEqual(first,c.history('tester')[0]['review_id'])
