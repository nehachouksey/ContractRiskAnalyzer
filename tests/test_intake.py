import unittest
from io import BytesIO
from zipfile import ZipFile
from src.intake import extract
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject

def word(body,extras=None):
    out=BytesIO()
    with ZipFile(out,'w') as z:
        z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+body+'</w:body></w:document>')
        for name,value in (extras or {}).items(): z.writestr(name,value)
    return out.getvalue()
def pdf(text=True):
    writer=PdfWriter(); page=writer.add_blank_page(600,800)
    if text:
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
        stream=DecodedStreamObject(); stream.set_data(b'BT /F1 12 Tf 50 700 Td (Contract terms and exceptions) Tj ET')
        page[NameObject('/Contents')]=writer._add_object(stream)
    out=BytesIO(); writer.write(out); return out.getvalue()
class IntakeTests(unittest.TestCase):
    def test_pdf_text_and_page_reference(self):
        result=extract('agreement.pdf',pdf())
        self.assertIn('PDF page 1',result['text']); self.assertIn('Contract terms and exceptions',result['text'])
        self.assertTrue(result['warnings'])
    def test_scan_or_empty_page_blocked(self):
        with self.assertRaisesRegex(ValueError,'OCR required'): extract('scan.pdf',pdf(False))
    def test_docx_order_tables_and_footnotes(self):
        body='<w:p><w:r><w:t>First clause</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Exception</w:t></w:r></w:p></w:tc></w:tr></w:tbl><w:p><w:r><w:t>Last clause</w:t></w:r></w:p>'
        text=extract('agreement.docx',word(body))['text']
        self.assertLess(text.index('First clause'),text.index('Exception')); self.assertLess(text.index('Exception'),text.index('Last clause')); self.assertIn('Cell 1',text)
    def test_unsupported_word_and_malformed(self):
        with self.assertRaisesRegex(ValueError,'tracked changes'): extract('agreement.docx',word('<w:p><w:ins><w:r><w:t>Unaccepted</w:t></w:r></w:ins></w:p>'))
        for filename in ['a.pdf','a.docx','a.doc']:
            with self.assertRaises(ValueError): extract(filename,b'invalid')
