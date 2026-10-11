"""Display formatting only; stored source text and citations are unchanged."""
import re

def readable_word(text):
    text=re.sub(r'(?m)^## Word paragraph \d+\s*\n', '', text)
    text=re.sub(r'(?m)^## Word table \d+\s*$', '### Table',text)
    text=re.sub(r'(?m)^## Word (footnotes|endnotes|header\d*|footer\d*)\s*$',lambda m:'### '+m[1].capitalize(),text)
    # Restore simple numbered section titles without promoting numbered clauses.
    text=re.sub(r'(?m)^(\d+\. [A-Z][^\n]{0,90})$',r'### \1',text)
    return re.sub(r'\n{3,}','\n\n',text).strip()
