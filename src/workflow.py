"""Shared UI and backend rules for review completion."""
from src.summary import NEXT_STEPS

def checklist(run, current, next_step=None):
    findings=run.get('comparisons',[])
    latest={a['comparison']:a for a in run.get('assessments',[])}
    assessed=all(i in latest and latest[i].get('rationale','').strip() for i in range(len(findings)))
    gaps=any(x.get('status')=='incomplete' for x in run.get('coverage',[]))
    unresolved=[]
    for i,f in enumerate(findings):
        a=latest.get(i,{})
        action=a.get('action')
        if f['outcome']=='Insufficient evidence' or action in ['Request further review','Mark finding incorrect']:
            unresolved.append(i)
        elif f['outcome']=='Potential conflict' and not (action=='Accept supported risk' or (action=='Confirm finding' and next_step=='Do not proceed with this draft')):
            unresolved.append(i)
    return [
        ('Evidence is current',run.get('snapshot')==current,'Reanalyse changed evidence before recording a new decision.'),
        ('Analysis and coverage are complete',run.get('status')!='analysis_failed' and bool(run.get('coverage')) and not gaps,'Retry failed analysis or obtain missing evidence and rerun incomplete checks.'),
        ('Comparisons are available',bool(findings),'No candidate retrieved is not clearance. Further investigation is required before completing this review.'),
        ('Every comparison has an assessment and rationale',assessed,'Select each comparison and save an assessment with your reasoning.'),
        ('Outstanding findings are addressed',not unresolved,'Resolve missing evidence, further-review requests and disputed findings through reanalysis. For a confirmed conflict, explicitly accept the supported risk or choose not to proceed with this draft.'),
        ('A final next step is selected',next_step in ['Refer to authorised signatory for a signing decision','Do not proceed with this draft'],'Clarification, change requests and further review remain follow-up actions, not completed reviews.')]

def status(run,current):
    if not run: return 'Not reviewed'
    if run.get('snapshot')!=current: return 'Outdated evidence'
    if run.get('status')=='analysis_failed': return 'Analysis failed'
    if run.get('completion'): return 'Review completed'
    if run.get('decisions'):
        return 'Follow-up needed' if run['decisions'][-1].get('workflow_status')=='follow_up' else 'Human review recorded'
    return 'Ready for human review'

def button(label):
    return {'Not reviewed':'Start review','Analysis failed':'Retry analysis','Outdated evidence':'Reanalyse','Review completed':'View decision','Human review recorded':'View decision'}.get(label,'Continue review')

def guidance(label):
    return {
      'Not reviewed':'Next: confirm the deal context and run analysis.',
      'Analysis failed':'Next: check the failure message, then confirm context and retry analysis.',
      'Outdated evidence':'Next: confirm context and reanalyse. Earlier decisions remain in history.',
      'Ready for human review':'Next: read each finding, inspect its evidence and save your assessment. Then record your decision below.',
      'Follow-up needed':'Next: obtain the requested information or changes, reanalyse as needed, then reassess outstanding findings.',
      'Human review recorded':'A decision was recorded under the earlier workflow. Inspect the checklist and explicitly complete the review if eligible.',
      'Review completed':'Review is complete for this evidence snapshot. View the decision below. Signing remains outside this application.'}[label]


DECISIONS=['Proceed for signing approval','Do not proceed','Need more information']
DECISION_ACTIONS={
    DECISIONS[0]:'Refer to authorised signatory for a signing decision',
    DECISIONS[1]:'Do not proceed with this draft',
    DECISIONS[2]:'Seek clarification or missing documents'}

def choice_for(action):
    if action==DECISION_ACTIONS[DECISIONS[0]]: return DECISIONS[0]
    if action==DECISION_ACTIONS[DECISIONS[1]]: return DECISIONS[1]
    return DECISIONS[2] if action else None

def pending_findings(run,next_step=None):
    latest={a['comparison']:a for a in run.get('assessments',[])}
    pending=[]
    for i,finding in enumerate(run.get('comparisons',[])):
        a=latest.get(i,{})
        if not a.get('rationale','').strip(): reason='Save an assessment and your reasoning.'
        elif finding['outcome']=='Insufficient evidence': reason='Obtain the missing evidence or clarification.'
        elif a['action'] in ['Mark finding incorrect','Request further review']: reason='Resolve the disputed finding or request for further review.'
        elif finding['outcome']=='Potential conflict' and a['action']!='Accept supported risk' and not (a['action']=='Confirm finding' and next_step=='Do not proceed with this draft'):
            reason='The conflict is confirmed, but the risk has not been accepted. Accept it only if authorised, or choose Do not proceed.'
        else: continue
        pending.append({'index':i,'title':finding.get('title',f'Finding {i+1}'),'reason':reason})
    return pending

def route(run,current):
    """A specific queue action; never imply that saved assessments complete a review."""
    label=status(run,current)
    if label in ['Not reviewed','Analysis failed','Outdated evidence']:
        return {'label':button(label),'step':1,'index':None,'text':guidance(label)}
    if label in ['Review completed','Human review recorded']:
        return {'label':'View decision','step':3,'index':None,'text':guidance(label)}
    latest={a['comparison']:a for a in run.get('assessments',[])}
    unassessed=[i for i in range(len(run.get('comparisons',[]))) if not latest.get(i,{}).get('rationale','').strip()]
    if unassessed:
        return {'label':'Review findings','step':2,'index':unassessed[0],'text':f'{len(unassessed)} finding(s) need your assessment.'}
    last=run.get('decisions',[])
    next_step=last[-1].get('next_step') if last else None
    pending=pending_findings(run,next_step)
    if pending:
        kind='risk' if all(run['comparisons'][item['index']]['outcome']=='Potential conflict' for item in pending) else 'finding'
        noun=kind if len(pending)==1 else kind+'s'
        return {'label':f'Resolve {len(pending)} {noun}','step':3,'index':None,'text':'Choose whether to proceed, stop this draft, or keep the review open.'}
    return {'label':'Record decision','step':3,'index':None,'text':'Assessments are saved. Record your final decision to complete the review.'}
