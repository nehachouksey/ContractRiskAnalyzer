import unittest
from src.history import groups,page_slice
class HistoryTests(unittest.TestCase):
 def run_record(self,i,attempt=0):
  return {'incoming_id':str(i),'id':f'{i}-{attempt}','name':f'Contract {i}','created':f'2026-10-{10+attempt:02d}','snapshot':{},'decisions':[]}
 def test_groups_latest_first_and_retains_attempts(self):
  runs=[self.run_record(1),self.run_record(1,1),self.run_record(2)]
  grouped=groups(runs,{})
  self.assertEqual(len(grouped),2); self.assertEqual(grouped[0][0]['id'],'1-1'); self.assertEqual(len(grouped[0]),2)
  self.assertEqual(len(groups(runs,{},'contract 1')),1)
 def test_pages_and_filter_empty(self):
  grouped=groups([self.run_record(i) for i in range(23)],{})
  rows,page,pages=page_slice(grouped,0)
  self.assertEqual((len(rows),page,pages),(10,0,3))
  rows,page,pages=page_slice(grouped,99)
  self.assertEqual((len(rows),page,pages),(3,2,3))
  self.assertEqual(groups([self.run_record(1)],{},selected_status='Review completed'),[])
  self.assertEqual(page_slice([],4),([],0,1))
