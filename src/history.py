"""Group saved runs without deleting or altering audit records."""
from src.workflow import status

def groups(runs,current,query='',selected_status='All statuses'):
    grouped={}
    for run in sorted(runs,key=lambda r:(r['created'],r['id']),reverse=True):
        grouped.setdefault(run['incoming_id'],[]).append(run)
    result=[]
    for attempts in grouped.values():
        latest=attempts[0]
        if not any(query.casefold().strip() in (r['name']+' '+r.get('review_id','')).casefold() for r in attempts): continue
        if selected_status!='All statuses' and status(latest,current)!=selected_status: continue
        result.append(attempts)
    return result

def page_slice(grouped,page,size=10):
    pages=max(1,(len(grouped)+size-1)//size)
    page=max(0,min(page,pages-1))
    return grouped[page*size:(page+1)*size],page,pages
