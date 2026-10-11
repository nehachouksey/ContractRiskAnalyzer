"""Local, non-executing extraction. Originals remain the authority."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET

MAX_BYTES=2*1024*1024
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def extract(filename,data):
    suffix=Path(filename).suffix.lower()
    if suffix not in {'.md','.txt','.pdf','.docx'}: raise ValueError('Upload .pdf, .docx, .md or .txt. Legacy .doc files must first be saved as .docx.')
    if len(data)>MAX_BYTES: raise ValueError('The contract exceeds the 2 MB upload limit.')
    if suffix in {'.md','.txt'}:
        try: text=data.decode('utf-8-sig')
        except UnicodeDecodeError: raise ValueError('Save the contract as UTF-8 text and upload it again.') from None
        warnings=[]
    elif suffix=='.pdf':
        from pypdf import PdfReader
        try:
            reader=PdfReader(BytesIO(data))
            if reader.is_encrypted: raise ValueError('Password-protected PDF. Upload an unencrypted copy you are authorised to review.')
            if len(reader.pages)>200: raise ValueError('PDF exceeds the 200-page extraction limit. Split into complete reviewable documents.')
            parts=[]
            for i,page in enumerate(reader.pages,1):
                value=(page.extract_text(extraction_mode='layout') or '') if page.get_contents() is not None else ''
                if not value.strip(): raise ValueError(f'OCR required: PDF page {i} has no readable text. Upload a searchable PDF or verified text instead.')
                if page.images: raise ValueError(f'PDF page {i} contains images that may hold contract terms. OCR or a verified text-only copy is required before analysis.')
                parts.append(f'## PDF page {i}\n\n{value}')
            if reader.get_fields(): raise ValueError('This PDF contains form fields. Flatten a verified copy with visible field values before uploading.')
            text='\n\n'.join(parts)
            warnings=['PDF text order and table alignment may differ from the original. Check every page, table and schedule before confirming.']
        except ValueError: raise
        except Exception: raise ValueError('This PDF could not be read. Upload a valid, unencrypted text-based PDF.') from None
    else:
        try:
            with ZipFile(BytesIO(data)) as z:
                if sum(i.file_size for i in z.infolist())>20*1024*1024: raise ValueError('Expanded Word document exceeds the 20 MB safety limit.')
                if any(n.startswith('word/embeddings/') for n in z.namelist()): raise ValueError('Embedded attachments cannot be extracted. Include their complete terms as ordinary text before uploading.')
                root=ET.fromstring(z.read('word/document.xml'))
                unsupported=['drawing','pict','object','txbxContent','altChunk','ins','del']
                if any(root.find('.//'+W+tag) is not None for tag in unsupported): raise ValueError('Word document contains images, embedded content or tracked changes. Upload a verified text-only copy with changes resolved; OCR may be required.')
                parts=[]; number=0
                def paragraph(el):
                    return ''.join((n.text or '') if n.tag==W+'t' else '\t' if n.tag==W+'tab' else '\n' if n.tag==W+'br' else '' for n in el.iter())
                body=root.find(W+'body')
                for block in body:
                    if block.tag==W+'p':
                        value=paragraph(block)
                        if value.strip():
                            number+=1; parts.append(f'## Word paragraph {number}\n\n{value}')
                    elif block.tag==W+'tbl':
                        number+=1; rows=[]
                        for ri,row in enumerate(block.findall(W+'tr'),1):
                            cells=['\n'.join(paragraph(p) for p in cell.findall('.//'+W+'p')) for cell in row.findall(W+'tc')]
                            rows.append(f'Row {ri}: '+' | '.join(f'Cell {ci}: {value}' for ci,value in enumerate(cells,1)))
                        parts.append(f'## Word table {number}\n\n'+'\n'.join(rows))
                for member in sorted(z.namelist()):
                    if member.startswith('word/') and (Path(member).name.startswith(('header','footer')) or Path(member).name in {'footnotes.xml','endnotes.xml'}):
                        extra=ET.fromstring(z.read(member))
                        value='\n'.join(paragraph(p) for p in extra.iter(W+'p'))
                        if value.strip(): parts.append(f'## Word {Path(member).stem}\n\n{value}')
                text='\n\n'.join(parts)
                warnings=['Word references use paragraph/table order, not page numbers. Verify tables, numbering, headers, footnotes and schedules against the original.']
        except ValueError: raise
        except (BadZipFile,KeyError,ET.ParseError,TypeError): raise ValueError('This Word file could not be read. Upload a valid .docx document.') from None
    if not text.strip(): raise ValueError('The uploaded contract is empty.')
    if len(text)>2*1024*1024: raise ValueError('Extracted text exceeds the 2 MB limit.')
    if any(ord(ch)<32 and ch not in '\n\r\t' for ch in text): raise ValueError('This file contains binary or unsupported control characters. Upload verified text.')
    return {'text':text,'warnings':warnings,'format':suffix[1:],'extractor':'intake-v1'}
