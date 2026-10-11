"""Summarise saved evidence and human labels without generating new conclusions."""
NEXT_STEPS=['Seek clarification or missing documents','Request contract changes or a specific waiver','Request further review','Refer to authorised signatory for a signing decision','Do not proceed with this draft']

def build(run,stale=False):
    latest={a['comparison']:a for a in run.get('assessments',[])}
    items=[]
    for i,f in enumerate(run.get('comparisons',[])):
        a=latest.get(i)
        items.append({'index':i,'title':f['title'],'outcome':f['outcome'],'reason':f['explanation'],'clarification':f.get('clarification',''),'source':f['historical_id'],'assessment':a})
    conflicts=[x for x in items if x['outcome']=='Potential conflict']
    missing=[x for x in items if x['outcome']=='Insufficient evidence']
    accepted=[x for x in items if x['assessment'] and x['assessment']['action']=='Accept supported risk']
    unresolved=[x for x in items if not x['assessment'] or x['outcome']=='Insufficient evidence' or x['assessment']['action'] in ['Request further review','Mark finding incorrect'] or (x['outcome']=='Potential conflict' and x['assessment']['action']!='Accept supported risk')]
    gaps=[x for x in run.get('coverage',[]) if x['status']=='incomplete']
    if run.get('completion') and not stale:
        headline='Review completed for this evidence snapshot'
        next_action='Read the recorded decision below. Completion records the human review; it does not approve or sign this contract.'
        if run['completion'].get('next_step')=='Do not proceed with this draft':
            unresolved=[x for x in unresolved if not (x['outcome']=='Potential conflict' and x['assessment'] and x['assessment']['action']=='Confirm finding')]
    elif stale:
        headline='Reanalyse before making a new decision'
        next_action='The evidence library changed after this review. Run analysis again and reassess the current evidence.'
    elif not items:
        headline='No comparison finding is available'
        next_action='Inspect search coverage and any incomplete checks. No candidate retrieved does not establish that the contract can be signed.'
    elif missing or gaps:
        headline='Clarification is needed before an informed signing decision'
        next_action='Obtain the missing information below and complete the affected checks. Keep any supported conflicts in view.'
    elif unresolved:
        headline='Human review still needs action'
        next_action='Assess the findings below. For unresolved conflicts, consider changing the scope, obtaining a specific signed waiver or seeking further review.'
    else:
        headline='Assessments are recorded; the signing decision remains with the authorised signatory'
        next_action='Check the recorded rationale and any accepted risks, then decide whether to refer this draft to the authorised signatory. This check covers historical restrictions only.'
    return dict(headline=headline,next_action=next_action,items=items,conflicts=conflicts,missing=missing,accepted=accepted,unresolved=unresolved,gaps=gaps)
