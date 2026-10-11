"""Bounded follow-up checks for documents omitted by the initial response."""
import copy
from src.coverage import reconcile

def recover(result,signed,docs,request,validate,stage,batch_size=4,repair=None):
    coverage,_=reconcile(result.get('coverage'),signed,result['comparisons'])
    # Recheck missing output, never relabel an unresolved evidence finding as clear.
    related={f['historical_id'] for f in result['comparisons']}
    targets=[row['source_id'] for row in coverage if row['status']=='incomplete' and row['source_id'] not in related]
    rows={row['source_id']:row for row in coverage}
    recovered=[]
    for offset in range(0,len(targets),batch_size):
        batch=targets[offset:offset+batch_size]
        stage(f'Checking remaining documents · {offset+1}–{offset+len(batch)} of {len(targets)}')
        try:
            response=request(batch)
            if repair:
                errors=[]
                for candidate in response.get('comparisons',[]) if isinstance(response.get('comparisons'),list) else []:
                    try: validate({'comparisons':[copy.deepcopy(candidate)]},docs)
                    except (ValueError,TypeError,KeyError,AttributeError) as exc:
                        errors.append({'historical_id':candidate.get('historical_id') if isinstance(candidate,dict) else None,'error':str(exc)})
                if errors:
                    stage('Verifying missing citation references for this group')
                    try:
                        corrected=repair(batch,{'errors':errors,'previous_response':response,'instruction':'Return the complete corrected response for this group. Cite BOTH the incoming and historical documents for each comparison. Do not invent references or change a supported finding merely to pass validation.'})
                        if isinstance(corrected,dict): response=corrected
                    except Exception: pass
            findings=response.get('comparisons')
            if not isinstance(findings,list): raise ValueError('Missing comparison output')
            if any(not isinstance(f,dict) or f.get('historical_id') not in batch for f in findings):
                raise ValueError('Follow-up response included an unrequested document')
            validated=[]
            for finding in findings:
                try:
                    validated.append(validate({'comparisons':[copy.deepcopy(finding)]},docs)['comparisons'][0])
                except (ValueError,TypeError,KeyError,AttributeError):
                    # Invalid source references must leave this document unfinished.
                    pass
            requested=[d for d in signed if d['id'] in batch]
            checked,_=reconcile(response.get('coverage'),requested,validated)
            for row in checked:
                # Invalid findings cannot be hidden by a contradictory no-candidate claim.
                if any(f.get('historical_id')==row['source_id'] for f in findings) and not any(f['historical_id']==row['source_id'] for f in validated):
                    row={'source_id':row['source_id'],'status':'incomplete','reason':'The follow-up comparison evidence could not be verified.'}
                rows[row['source_id']]=row
                if row['status']!='incomplete': recovered.append(row['source_id'])
            result['comparisons'].extend(validated)
        except Exception:
            # A failed batch must not discard the valid initial analysis.
            for sid in batch:
                rows[sid]={'source_id':sid,'status':'incomplete','reason':'This document check did not finish after an automatic follow-up. Existing findings are retained.'}
    result['coverage'],result['coverage_issues']=reconcile(list(rows.values()),signed,result['comparisons'])
    result['automatic_followup']={'documents_requested':len(targets),'documents_completed':len(recovered)}
    return result
