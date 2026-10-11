"""A compact decision brief derived only from saved findings and human decisions."""
from src.summary import build

SHORT_ACTIONS={
 'Seek clarification or missing documents':'Obtain clarification',
 'Request contract changes or a specific waiver':'Request changes or waiver',
 'Request further review':'Seek further review',
 'Refer to authorised signatory for a signing decision':'Refer to authorised signatory',
 'Do not proceed with this draft':'Do not proceed with this draft'}

def recorded_line(run,stale=False,limit=180):
    decisions=run.get('decisions',[])
    if not decisions: return None
    last=decisions[-1]
    action=SHORT_ACTIONS.get(last.get('next_step'),'See recorded rationale')
    rationale=' '.join(last.get('text','').split())
    if len(rationale)>limit: rationale=rationale[:limit].rsplit(' ',1)[0]+'…'
    return ('Earlier human decision (evidence changed): ' if stale else 'Recorded human decision: ')+action+(' — '+rationale if rationale else '')

def make(run,stale=False):
    s=build(run,stale)
    if run.get('status')=='analysis_failed':
        result='Analysis did not finish; no completed review result is available.'
        suggested='Retry analysis before assessing this draft.'
    elif stale:
        result='This review uses outdated evidence.'
        suggested='Reanalyse the current sources before making a new decision.'
    elif not s['items']:
        result='No comparison finding was returned; the contract has not been cleared.'
        suggested='Inspect search coverage and obtain further evidence or review.'
    else:
        parts=[]
        if s['conflicts']: parts.append(f"{len(s['conflicts'])} potential-conflict finding(s)")
        if s['missing']: parts.append(f"{len(s['missing'])} comparison(s) with insufficient evidence")
        if s['gaps']: parts.append(f"{len(s['gaps'])} incomplete source check(s)")
        result='; '.join(parts)+'.' if parts else 'No conflict identified in the returned comparisons; this is not whole-contract clearance.'
        if s['missing'] or s['gaps']:
            suggested='Obtain the missing information and complete the affected checks before referral for a signing decision.'
        elif s['unresolved']:
            suggested='Assess the outstanding findings; consider clarification, scope changes, a specific waiver or further review.'
        elif s['accepted']:
            suggested='Review the explicitly accepted risks and consider referral to the authorised signatory.'
        else:
            suggested='Review the supporting evidence and decide whether to refer this draft to the authorised signatory.'
    outstanding=[x['title']+' — '+x['clarification'] for x in s['missing']]
    if s['gaps']: outstanding.append(f"{len(s['gaps'])} document checks are unfinished. Retry analysis; see Document checks for the affected agreements.")
    outstanding += [x['title']+' — '+(x['assessment']['action'] if x['assessment'] else 'Assessment not saved') for x in s['unresolved'] if x not in s['missing']]
    return {'result':result,'suggested':suggested,'summary':s,'outstanding':outstanding,'recorded':recorded_line(run,stale)}
