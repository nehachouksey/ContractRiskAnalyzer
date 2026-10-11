"""Reconcile provider claims against the actual registered source inventory."""
import re

def display_name(source_id):
    name=source_id.rsplit('/',1)[-1].rsplit('.',1)[0]
    name=re.sub(r'^\d{4}-\d{2}-\d{2}_','',name).replace('_',' ')
    return ' '.join(word.upper() if word.lower() in {'msa','nda','baa','sow'} else word.capitalize() for word in name.split())

def readable_reason(item):
    reason=item.get('reason','')
    if 'reported as assessed, but no comparison' in reason: return 'No comparison result was returned. Retry analysis.'
    if 'No valid processing report' in reason: return 'No check result was returned. Retry analysis.'
    if 'Duplicate processing reports' in reason: return 'Conflicting check results were returned. Retry analysis.'
    if 'invalid status or missing explanation' in reason: return 'The check result could not be read. Retry analysis.'
    if 'lacks validated supporting evidence' in reason: return 'Supporting evidence could not be verified. Retry or obtain clarification.'
    return reason

def reconcile(raw,signed,comparisons):
    inventory={d['id']:d for d in signed}
    entries={sid:[] for sid in inventory}; issues=[]
    if not isinstance(raw,list):
        raw=[]; issues.append('The analysis returned an invalid coverage list.')
    for entry in raw:
        if not isinstance(entry,dict) or not isinstance(entry.get('source_id'),str) or entry['source_id'] not in inventory:
            issues.append('An unrecognised coverage entry could not be assigned to a registered source.')
        else: entries[entry['source_id']].append(entry)
    result=[]
    for sid in inventory:
        matches=entries[sid]
        related=[f for f in comparisons if f['historical_id']==sid]
        status='incomplete'; reason='No valid processing report was returned for this document. Retry this check.'
        if len(matches)>1: reason='Duplicate processing reports were returned for this document. Retry this check.'
        elif len(matches)==1:
            item=matches[0]
            if isinstance(item.get('status'),str) and item['status'] in {'assessed','no candidate','incomplete'} and isinstance(item.get('reason'),str) and item['reason'].strip():
                status=item['status']; reason=item['reason']
            else: reason='The processing report had an invalid status or missing explanation. Retry this check.'
        if status=='assessed' and not related:
            status='incomplete'; reason='The document was reported as assessed, but no comparison was returned. Retry this check.'
        if status=='no candidate' and related:
            status='incomplete'; reason='The processing report contradicts the returned comparisons. Inspect retained findings and retry this check.'
        if any(f['outcome']=='Insufficient evidence' for f in related):
            status='incomplete'; reason='At least one comparison lacks validated supporting evidence. Obtain clarification or retry analysis.'
        if issues:
            status='incomplete'; reason+=' Coverage also contains unassigned entries; verify the source inventory and rerun analysis.'
        result.append({'source_id':sid,'status':status,'reason':reason})
    return result,issues
