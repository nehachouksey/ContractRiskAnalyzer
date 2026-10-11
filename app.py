import streamlit as st
import os, re, uuid, html
from datetime import date
from src import core as c
from src import workflow as w
from src.reading import readable_word
from src.coverage import display_name, readable_reason
from src.ui import BRAND, CSS
from src.brief import make as make_brief, recorded_line, SHORT_ACTIONS
st.set_page_config(page_title='AtliQ · Contract review',page_icon='◈',layout='wide',initial_sidebar_state='auto')
# Streamlit's fixed-option selectboxes still expose a search input. Make that
# input read-only while retaining focus, arrow keys and option selection.
st.html('''<script>
(() => {
  const lockDropdowns = () => {
    document.querySelectorAll('[data-testid="stSelectbox"] input').forEach(input => {
      if (!input.readOnly) input.readOnly = true;
      if (input.getAttribute('inputmode') !== 'none') input.setAttribute('inputmode', 'none');
    });
  };
  lockDropdowns();
  if (!window.atliqDropdownObserver) {
    window.atliqDropdownObserver = new MutationObserver(lockDropdowns);
    window.atliqDropdownObserver.observe(document.body, {
      childList: true, subtree: true, attributes: true, attributeFilter: ['readonly']
    });
  }
})();
</script>''', unsafe_allow_javascript=True)
st.markdown('''<style>
.block-container{max-width:1440px;padding:2rem 3rem 4rem}header[data-testid="stHeader"]{background:#F8FAFC}body,p,label{font-size:16px}h1{font-size:2rem!important;letter-spacing:-.045em;font-weight:650!important}h2{font-size:1.4rem!important;letter-spacing:-.025em}h3{font-size:1.06rem!important}p{line-height:1.65}div[data-testid="stVerticalBlockBorderWrapper"]>div{border-radius:10px!important;border-color:#D4DCE6!important;background:white}div.stButton>button{min-height:42px;border:1px solid #94A3B8;border-radius:7px;font-weight:550}div.stButton>button[kind="primary"]{border-color:#1D4ED8}div[data-baseweb="input"],div[data-baseweb="textarea"],div[data-baseweb="select"]>div{border:1px solid #94A3B8!important;background:white!important}button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid #1D4ED8!important;outline-offset:3px}.identity{font-size:18px;font-weight:650;letter-spacing:-.4px}.logo{display:inline-block;padding:7px 11px;background:#0F172A;color:white;border-radius:7px;margin-right:10px}.muted{color:#475569;font-size:14px}.eyebrow{font-size:12px;letter-spacing:.12em;font-weight:650;color:#475569}.badge{display:inline-block;font-size:13px;padding:4px 9px;background:#F1F5F9;border:1px solid #CBD5E1;border-radius:5px;color:#334155}.amber{background:#FFFBEB;border-color:#D97706;color:#92400E}.evidence{line-height:1.8;background:#FFF;border-left:3px solid #1D4ED8;padding:16px;white-space:pre-wrap;overflow-wrap:anywhere}.evidence mark{background:#FEF3C7;color:#0F172A}.contract-title{font-weight:650;font-size:17px;overflow-wrap:anywhere}.footer{margin-top:32px;border-top:1px solid #E2E8F0;padding-top:16px;color:#475569;font-size:13px}@media(max-width:760px){.block-container{padding:1rem}.identity{font-size:15px}}@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>''',unsafe_allow_html=True)
st.markdown(CSS,unsafe_allow_html=True)
if not st.session_state.get('user'):
    st.html(BRAND+'<div class="muted" style="margin-top:-14px;margin-bottom:24px">Contract Obligation &amp; Conflict Review</div>')

def badge(text):
    tone='green' if text=='Review completed' else 'amber' if text in ['Potential conflict','Follow-up needed','Outdated evidence','Insufficient evidence'] else 'blue' if text in ['Ready for human review','Human review recorded'] else 'red' if text=='Analysis failed' else ''
    st.markdown(f'<span class="badge {tone}">{html.escape(text)}</span>',unsafe_allow_html=True)

def note(text): st.caption(text)
_evidence_number=0
def evidence(ref):
    global _evidence_number
    _evidence_number+=1
    c.guard(st.session_state.user)
    with c.db() as db: row=db.execute('SELECT content FROM sources WHERE id=? AND version=?',(ref['source_id'],ref['version'])).fetchone()
    original=c.original_upload(st.session_state.user,ref['source_id'])
    if original: st.download_button('Download original contract',data=original[1],file_name=original[0],key='original_evidence_'+str(_evidence_number))
    st.markdown('**'+ref['source_id'].split('/')[-1].replace('_',' ')+'**')
    note(f"{ref.get('clause','Source passage')} · line {ref['line']}")
    if not row: st.error('This source version is unavailable. Request the original evidence.'); return
    word_source=bool(original and original[0].lower().endswith('.docx'))
    displayed_quote=readable_word(ref['quote']) if word_source else ref['quote']
    st.markdown('<div class="evidence"><mark>'+html.escape(displayed_quote)+'</mark></div>',unsafe_allow_html=True)
    with st.expander('Read complete source, including definitions and exceptions'): st.markdown(readable_word(row[0]) if word_source else row[0])

_document_number=0
def reviewed_contract(run):
    global _document_number
    _document_number+=1
    with st.expander('Reviewed contract · view or download'):
        try:
            doc=c.reviewed_document(st.session_state.user,run['id'])
        except (ValueError,PermissionError) as exc:
            st.info(str(exc)); return
        st.caption('The exact contract saved for this review, including when the current draft has changed.')
        st.download_button('Download reviewed contract',data=doc['data'],file_name=doc['filename'],key='reviewed_download_'+str(_document_number))
        st.markdown(readable_word(doc['text']) if doc['filename'].lower().endswith('.docx') else doc['text'])

def document_checks(run):
    checks=run.get('coverage',[])
    pending=[item for item in checks if item['status']=='incomplete']
    finished=[item for item in checks if item['status']!='incomplete']
    with st.expander(f'Document checks · {len(pending)} unfinished / {len(checks)} total',expanded=bool(pending)):
        if pending:
            st.markdown('**Some document checks are unfinished**')
            st.write(f'{len(pending)} of {len(checks)} checks need attention. Available findings are retained, but this review cannot yet be completed.')
            st.caption('An unfinished check is not a conflict finding. Retry analysis first; if evidence is missing or unreadable, obtain a complete source before rerunning.')
            reasons={}
            for item in pending:
                reason=readable_reason(item)
                reasons[reason]=reasons.get(reason,0)+1
            for reason,count in reasons.items(): st.write(f'**{count} document(s):** {reason}')
            st.dataframe([{'Agreement':display_name(item['source_id']),'Check status':'Needs attention'} for item in pending],hide_index=True,use_container_width=True)
        else: st.success(f'All {len(checks)} document checks returned a result.' if checks else 'No document check results are available.')
        if finished:
            with st.expander(f'Checked documents ({len(finished)})'):
                st.dataframe([{'Agreement':display_name(item['source_id']),'Check status':'Checked' if item['status']=='assessed' else 'No relevant restriction retrieved','Result':item.get('reason','')} for item in finished],hide_index=True,use_container_width=True)
                st.caption('No relevant restriction retrieved is not whole-contract clearance.')

def decision_brief(run,stale=False):
    brief=make_brief(run,stale)
    st.caption('Review ID: '+run.get('review_id','Assigned when saved'))
    with st.container(border=True):
        st.subheader('Decision brief')
        st.write('**Review result:** '+brief['result'])
        if brief['recorded']:
            st.markdown('**'+html.escape(brief['recorded'])+'**')
            last=run['decisions'][-1]
            st.caption('Recorded by '+last['reviewer']+' · '+last['time']+' (UTC) · Full rationale below')
            if stale: st.warning('This earlier decision does not cover the changed evidence. Reanalyse before recording a new decision.')
            with st.expander('Read full recorded rationale'): st.write(last['text'])
        else:
            st.write('**Suggested next action:** '+brief['suggested'])
            st.caption('A process suggestion based on this review, not a human decision or signing approval.')
        s=brief['summary']
        st.markdown('**Why it matters**')
        concerns=s['conflicts'] or s['missing'] or s['items']
        if not concerns: st.write('No supported comparison is available. Inspect coverage before drawing a conclusion.')
        for item in concerns[:2]:
            st.write('**'+item['title']+'** — '+item['reason'])
            refs=run['comparisons'][item['index']].get('evidence',[])
            with st.expander('Evidence · '+item['title']):
                if not refs: st.info('Supporting evidence is unavailable for this comparison.')
                for ref in refs: evidence(ref)
        if len(concerns)>2: st.caption(f'{len(concerns)-2} more comparison(s) are available in the detailed summary.')
        if brief['outstanding']:
            st.markdown('**Still unresolved**')
            for text in brief['outstanding'][:3]: st.write('• '+text)
            if len(brief['outstanding'])>3: st.caption(f"{len(brief['outstanding'])-3} more outstanding item(s) in the detailed summary.")
        else: st.caption('No outstanding items are recorded in this scoped review.')
        st.caption('Scope: historical exclusivity and non-compete commitments. Signing authority remains outside this application.')
    reviewed_contract(run)

def review_summary(run,stale=False):
    from src.summary import build
    summary=build(run,stale)
    with st.container(border=True):
        st.subheader('Review summary · what this means for your next decision')
        st.markdown('**'+summary['headline']+'**')
        st.write(summary['next_action'])
        note(f"Review date {run['context']['review_date']} · Historical exclusivity and non-compete checks only")
        st.markdown('**1. Main concerns**')
        if not summary['conflicts']: st.write('No potential-conflict finding appears in this run. This does not establish that the whole contract is clear.')
        for item in summary['conflicts']:
            st.write('**'+item['title']+'** — '+item['reason'])
            note('Historical agreement: '+item['source'].split('/')[-1].replace('_',' '))
            a=item['assessment']
            st.write(('Your assessment: '+a['action']+' — '+a['rationale']) if a else 'Your assessment: not recorded yet.')
        st.markdown('**2. Information still needed**')
        if not summary['missing'] and not summary['gaps']: st.write('No missing-evidence finding or incomplete source check is recorded. Review any questions within individual findings.')
        for item in summary['missing']: st.write('**'+item['title']+'** — '+item['clarification'])
        for gap in summary['gaps']: st.write('Incomplete source check: '+gap['source_id'].split('/')[-1].replace('_',' ')+' — '+gap.get('reason','Clarification required.'))
        st.markdown('**3. Risks you have accepted**')
        if not summary['accepted']: st.write('No supported risk acceptance has been recorded.')
        for item in summary['accepted']: st.write('**'+item['title']+'** — '+item['assessment']['rationale'])
        st.markdown('**4. What needs your action**')
        st.write(f"{len(summary['unresolved'])} comparison(s) still need action; {len(summary['gaps'])} source check(s) are incomplete. These counts may relate to the same issue.")
        for item in summary['unresolved']:
            a=item['assessment']
            st.write('**'+item['title']+'** — '+(a['action'] if a else 'Read the evidence and save an assessment.'))
        with st.expander('Comparisons with no conflict identified'):
            for item in summary['items']:
                if item['outcome']=='No conflict identified in this comparison': st.write('**'+item['title']+'** — '+item['reason'])
        st.markdown('**5. Your next decision**')
        if run.get('decisions'):
            decision=run['decisions'][-1]
            st.write('Last recorded next step: **'+(decision.get('next_step') or 'See reviewer rationale')+'**')
            st.write(decision['text']); note(decision['reviewer']+' · '+decision['time']+' (UTC)')
            if stale: st.warning('This decision relates to the earlier evidence snapshot.')
        else: st.write('No overall review decision has been recorded. Choose a next step below after reading the evidence and assessments.')
        st.caption('The application does not decide “sign” or “do not sign”. The authorised signatory makes that decision outside the app, considering accepted risks, unresolved issues and checks beyond this review scope.')

def history_entry(r,current):
    review_status=w.status(r,current)
    note(f"{r.get('review_id','Saved review')} · {r['reviewer']} · {r['created']} (UTC)")
    badge(review_status)
    st.caption(w.guidance(review_status))
    if r.get('status')=='analysis_failed':
        st.error(r.get('error','Analysis failed. Retry analysis.'))
        st.caption('This failed attempt has no completed analysis. Prior reviews are retained separately.')
    else:
        decision_brief(r,r['snapshot']!=current)
        document_checks(r)
        with st.expander('Detailed review summary'): review_summary(r,r['snapshot']!=current)
    with st.expander('Inspect findings and assessment history'):
        for i,f in enumerate(r['comparisons']):
            st.write(f"**{f['outcome']} · {f['title']}**"); st.write(f['explanation'])
            for a in r['assessments']:
                if a['comparison']==i: st.write(f"{a['action']} · {a['reviewer']} · {a['time']} — {a['rationale']}")
            for ref in f['evidence']: evidence(ref)
        for d in r['decisions']: st.write(f"Review decision · {d['reviewer']} · {d['time']} — {d['text']}")

def sign_in():
    name=st.session_state.login_identity.strip()
    password=st.session_state.login_password
    try:
        if not c.configured(): c.setup(name,password)
        if not c.login(name,password): raise ValueError('Access denied. Check your reviewer identity and password.')
        st.session_state.user=name
        st.session_state.page='Contracts'
        st.session_state.pop('login_error',None)
        st.session_state.login_password=''
    except Exception as exc: st.session_state.login_error=str(exc)

def auth():
    if st.session_state.get('user'): return True
    st.markdown("""<style>
    .block-container:has(.st-key-auth_shell){max-width:1200px;padding-top:2.5rem}
    .st-key-auth_shell{margin-top:1.5rem}
    .st-key-auth_intro{background:linear-gradient(145deg,#0F172A 0%,#172554 100%);border-radius:20px;padding:42px 38px;min-height:540px;color:#FFF}
    .login-eyebrow{font-size:11px;font-weight:650;letter-spacing:.16em;color:#93C5FD;margin-bottom:22px}
    .login-heading{font-size:clamp(32px,3.2vw,44px);font-weight:650;letter-spacing:-.045em;line-height:1.14;margin:0 0 22px;color:white}
    .login-copy{font-size:16px;color:#CBD5E1;line-height:1.8;max-width:390px;margin-bottom:30px}
    .login-steps{border-top:1px solid #334568;padding-top:24px;display:grid;gap:18px}
    .login-step{display:flex;gap:14px;align-items:center}
    .login-number{display:grid;place-items:center;flex-shrink:0;width:32px;height:32px;border-radius:50%;background:#24385C;color:#BFDBFE;font-size:13px;font-weight:650}
    .login-step strong{display:block;font-size:15px;font-weight:600;color:#F8FAFC}
    .login-step small{display:block;color:#AFC0D8;font-size:13px;margin-top:3px}
    .st-key-auth_card{padding:35px 32px;background:white;border:1px solid #E2E8F0;border-radius:20px;box-shadow:0 12px 36px #0F172A08;margin-top:0;min-height:540px}
    @media(min-width:761px){.st-key-auth_shell [data-testid="stHorizontalBlock"]{align-items:stretch}.st-key-auth_shell [data-testid="stColumn"]>div{height:100%}.st-key-auth_intro,.st-key-auth_card{height:100%;box-sizing:border-box}}
    .st-key-auth_card h2{font-size:28px!important;letter-spacing:-.04em;margin-bottom:4px}
    .st-key-auth_card [data-testid="stForm"]{border:0;padding:10px 0 0}
    .st-key-auth_card input{min-height:44px}
    .st-key-auth_card [data-testid="stFormSubmitButton"] button{min-height:48px;border-radius:9px;margin-top:10px;font-weight:600}
    .login-footer{font-size:12px;color:#64748B;line-height:1.8;margin-top:20px;text-align:center}
    @media(max-width:760px){.st-key-auth_intro{padding:28px;min-height:0}.st-key-auth_card{margin-top:0;padding:24px;min-height:0}.login-heading{font-size:32px}}
    </style>""",unsafe_allow_html=True)
    with st.container(key='auth_shell'):
        left,right=st.columns([1,1],gap='large',vertical_alignment='top')
        with left:
            with st.container(key='auth_intro'):
                st.html('''<div class="login-eyebrow">CONTRACT REVIEW WORKSPACE</div>
                <div class="login-heading">Clear contracts.<br>Informed decisions.</div>
                <div class="login-copy">Compare incoming contracts with existing obligations and review the evidence before deciding.</div>
                <div class="login-steps">
                  <div class="login-step"><span class="login-number">01</span><div><strong>Add your contract</strong><small>Upload a draft and confirm its details.</small></div></div>
                  <div class="login-step"><span class="login-number">02</span><div><strong>Review the findings</strong><small>Understand conflicts and inspect source evidence.</small></div></div>
                  <div class="login-step"><span class="login-number">03</span><div><strong>Record your decision</strong><small>Capture your next action with clear reasoning.</small></div></div>
                </div>''')
        with right:
            with st.container(key='auth_card'):
                initial=not c.configured()
                st.markdown('## Create your workspace' if initial else '## Sign in to your workspace')
                st.caption('Set up your local reviewer account to begin.' if initial else 'Sign in to continue your contract reviews.')
                with st.form('login',border=False):
                    name=st.text_input('Reviewer identity',placeholder='Your name or work email',key='login_identity')
                    password=st.text_input('Password',type='password',key='login_password',help='At least 12 characters for initial setup.' if initial else 'Use the password created for this local workspace.')
                    st.form_submit_button('Create reviewer' if initial else 'Sign in',type='primary',use_container_width=True,on_click=sign_in)
                st.html('<div class="login-footer">Synthetic demonstration data · Human review required<br>Signing remains with the authorised signatory.</div>')
                if st.session_state.get('login_error'): st.error(st.session_state.login_error)
    return False
if not auth(): st.stop()
user=st.session_state.user
def scroll_to_page(): st.session_state.scroll_target='workspace-top'
if 'page_next' in st.session_state:
    st.session_state.page=st.session_state.pop('page_next')
    st.session_state.scroll_target='workspace-top'
if 'scroll_target' in st.session_state:
    target=st.session_state.pop('scroll_target')
    st.html("""<script>
    (() => {
        const scroll = () => {
            const target = document.getElementById('"""+target+"""');
            if (target) target.scrollIntoView({block:'start',behavior:'instant'});
        };
        requestAnimationFrame(() => requestAnimationFrame(scroll));
        setTimeout(scroll, 150);
        setTimeout(scroll, 400);
    })();
    </script>""" + '<!-- navigation-'+uuid.uuid4().hex+' -->', unsafe_allow_javascript=True)
st.html('<div id="workspace-top" style="scroll-margin-top:70px"></div>')
with st.sidebar:
    st.html(BRAND)
    st.caption('WORKSPACE')
    pages=['Contracts','Review workspace','Review history'] if st.session_state.get('active') else ['Contracts','Review history']
    page=st.radio('Workspace navigation',pages,label_visibility='collapsed',key='page',on_change=scroll_to_page)
    st.divider()
    st.caption('REVIEWER')
    st.write(user)
    if st.button('Sign out',key='sign_out',use_container_width=True,help='Ends this session. Saved reviews remain available when you sign in again.'):
        for key in list(st.session_state): del st.session_state[key]
        st.rerun()
    st.caption('Contract Obligation & Conflict Review')
contracts=c.documents(user,'incoming')
if 'active' not in st.session_state: st.session_state.active=None
if 'run' not in st.session_state: st.session_state.run=None

if page=='Contracts':
    st.markdown('<div class="eyebrow">REVIEW QUEUE</div>',unsafe_allow_html=True)
    st.title('Contracts')
    st.write('Start with a draft. Confirm the deal context, then check historical commitments.')
    queue_runs=c.history(user)
    queue_current=c.snapshot(user)
    queue_latest={}
    for item in queue_runs: queue_latest.setdefault(item['incoming_id'],item)
    statuses=[w.status(queue_latest.get(d['id']),queue_current) for d in contracts]
    tiles=[(len(contracts),'Incoming contracts'),(statuses.count('Not reviewed'),'Awaiting review'),(statuses.count('Follow-up needed'),'Follow-up needed'),(statuses.count('Review completed'),'Completed reviews')]
    st.html('<div class="queue-stats">'+''.join(f'<div class="queue-stat"><strong>{number}</strong><span>{label}</span></div>' for number,label in tiles)+'</div>')
    with st.expander('＋ Upload a new contract'):

        st.caption('Upload a text-based PDF, Word (.docx), Markdown or UTF-8 text file, up to 2 MB. Scans require OCR. Include all schedules and exceptions; check extracted text against the original.')
        uploaded=st.file_uploader('Contract file',type=['pdf','docx','md','txt'],max_upload_size=2)
        if uploaded is not None:
            try:
                raw=uploaded.getvalue()
                from src.intake import extract
                extraction=extract(uploaded.name,raw)
                preview=extraction['text']
                for warning in extraction['warnings']: st.warning(warning)
                name=st.text_input('Contract name',value=uploaded.name.rsplit('.',1)[0].replace('_',' '),key='upload_name_'+uploaded.name)
                st.caption(f'{len(raw):,} bytes · Draft · Not analysed')
                with st.expander('Preview contract',expanded=True): st.markdown(readable_word(preview) if uploaded.name.lower().endswith('.docx') else preview)
                checked=st.checkbox('I have checked that this draft includes the complete contract text',key='upload_checked_'+__import__('hashlib').sha256(raw).hexdigest())
                if st.button('Save draft & start review',type='primary',disabled=not checked):
                    source_id=c.upload_contract(user,uploaded.name,raw,name)
                    st.session_state.active=source_id
                    st.session_state.run=next((r for r in c.history(user) if r['incoming_id']==source_id),None)
                    st.session_state.pop('analysis_error',None)
                    st.session_state.page_next='Review workspace'
                    st.rerun()
            except (ValueError,OSError) as exc: st.error(str(exc))
    search=st.text_input('Find a contract',placeholder='Search by contract name')
    note(f'{len(contracts)} incoming drafts · Evaluation review date: 28 September 2026')
    if not contracts: st.info('No incoming contracts are available. Check DATASET_DIR and restore the incoming Markdown files.')
    runs=c.history(user)
    current=c.snapshot(user)
    st.html('<div class="queue-heading"><span>Contract / latest decision</span><span>Review status</span><span>Next action</span></div>')
    for d in contracts:
        if search.lower() not in d['name'].lower(): continue
        prev=next((r for r in runs if r['incoming_id']==d['id']),None)
        queue_action=w.route(prev,current)
        with st.container(border=True):
            a,b,cc=st.columns([5,2,1.5],vertical_alignment='center')
            with a:
                st.markdown('<div class="contract-title">'+html.escape(d['name'])+'</div>',unsafe_allow_html=True)
                entities=[x for x in ['AtliQ Technologies Pvt Ltd','AtliQ Technologies Inc.'] if x in d['text']]
                note((' · '.join(entities) or 'Entity needs confirmation')+' · Draft')
                if prev:
                    line=recorded_line(prev,prev['snapshot']!=current,limit=120)
                    if line: st.caption(line)
                    if not prev.get('completion'): st.caption(queue_action['text'])
            review_status=w.status(prev,current)
            with b: badge(review_status)
            with cc:
                if st.button(queue_action['label'],key=d['id'],use_container_width=True,help=queue_action['text']):
                    st.session_state.pop('analysis_error',None)
                    st.session_state.active=d['id']; st.session_state.run=prev
                    st.session_state['step_'+d['id']]=queue_action['step']
                    if prev and queue_action['index'] is not None: st.session_state['index_'+prev['id']]=queue_action['index']
                    st.session_state.page_next='Review workspace'; st.rerun()
elif page=='Review workspace':
    selected=next((d for d in contracts if d['id']==st.session_state.active),None)
    if selected is None:
        st.title('Your review workspace'); st.info('No contract selected. Choose an incoming draft from Contracts to begin.'); st.stop()
    st.markdown('<div class="eyebrow">INCOMING CONTRACT</div>',unsafe_allow_html=True)
    st.title(selected['name'])
    run=st.session_state.run
    review_status=w.status(run,c.snapshot(user))
    badge(review_status)
    stepkey='step_'+selected['id']
    st.session_state.setdefault(stepkey,3 if run and (run.get('completion') or run.get('decisions')) else 2 if run and run.get('status')!='analysis_failed' else 1)
    step=st.session_state[stepkey]
    if not run or run.get('status')=='analysis_failed': step=1
    steps=st.columns(3)
    for n,label in enumerate(['Confirm details','Review findings','Record decision'],1):
        with steps[n-1]:
            if st.button(f'{n}. {label}',key='stage_'+str(n),type='primary' if n==step else 'secondary',help=['Check the selected contract and confirm its details. Upload new contracts from Contracts.','Inspect findings and save your assessments.','Read the summary and record your next action.'][n-1],disabled=n>1 and (not run or run.get('status')=='analysis_failed'),use_container_width=True):
                st.session_state[stepkey]=n; st.session_state.scroll_target='review-step'; st.rerun()
    st.html('<div id="review-step" style="scroll-margin-top:70px"></div>')
    st.caption(f'Step {step} of 3 · '+['Check the text and deal details, then analyse.','Read the evidence, save your assessment and move to the next finding.','Choose a next action and record your decision.'][step-1])
    if review_status=='Outdated evidence':
        st.warning('Evidence changed. Go to step 1 and reanalyse before recording a new decision.')
    note('Draft · '+(run['context']['review_date'] if run else 'Review date awaiting confirmation'))
    if step==1:
        if st.session_state.get('analysis_error'): st.error('Analysis failed · '+st.session_state.analysis_error)
        elif run and run.get('status')=='analysis_failed': st.error('Analysis failed · '+run.get('error','Retry analysis.'))
        with st.container(border=True):
            st.subheader('Check contract details')
            st.caption('Confirm the scope before analysis. Original source remains available; your corrections are stored separately.')
            with st.expander('Original incoming agreement'):
                original=c.original_upload(user,selected['id'])
                if original: st.download_button('Download original contract',data=original[1],file_name=original[0],key='original_'+selected['id'])
                st.caption('Contract text · Check tables and schedules against the original file. Paragraph references are available in the evidence details.')
                st.markdown(readable_word(selected['text']) if original and original[0].lower().endswith('.docx') else selected['text'])
            with st.form('context_'+selected['version']):
                original_entity='AtliQ Technologies Pvt Ltd' if 'AtliQ Technologies Pvt Ltd' in selected['text'] else 'Unknown — confirm from source'
                scope_match=re.search(r'(?ims)^## [^\n]*(?:SCOPE|SERVICES|PROJECT)[^\n]*\n(.*?)(?=^## |\Z)',selected['text'])
                source_scope=scope_match.group(1).strip() if scope_match else 'Unknown — confirm activities and locations from the original source'
                st.caption('Extracted scope passage — original wording, not a confirmed interpretation')
                st.write(source_scope)
                draft_context=st.session_state.get('context_'+selected['id'],run['context'] if run else {})
                entity=st.text_input('AtliQ entity',value=draft_context.get('entity',original_entity))
                scope=st.text_area('Services, activities and locations',value=draft_context.get('scope',source_scope),height=100)
                dt=st.date_input('Review date',value=date.fromisoformat(draft_context.get('review_date',str(date.today()) if selected.get('uploaded') else os.getenv('DEFAULT_REVIEW_DATE','2026-09-28'))))
                confirmed=st.checkbox('I have checked the deal context against the source')
                go=st.form_submit_button('Analyse contract',type='primary')
            if go:
                context={'entity':entity,'scope':scope,'review_date':str(dt),'original_entity':original_entity}
                st.session_state['context_'+selected['id']]=context
                if not confirmed: st.error('Confirm the context before running analysis.')
                else:
                    try:
                        before=c.snapshot(user)
                        with st.status('Analysis in progress',expanded=True) as status:
                            result=c.analyze(user,selected,context,st.write)
                            status.update(label='Ready for human review',state='complete')
                        if before != c.snapshot(user): raise ValueError('Evidence changed during analysis. Retry with the current sources.')
                        run={'id':str(uuid.uuid4()),'reviewer':user,'created':c.now(),'incoming_id':selected['id'],'name':selected['name'],'version':selected['version'],'context':context,'snapshot':c.snapshot(user),'status':'ready',**result,'assessments':[],'decisions':[]}
                        c.save(user,run); st.session_state.run=run; st.session_state[stepkey]=2; st.session_state.scroll_target='finding-top'; st.session_state.pop('analysis_error',None); st.rerun()
                    except Exception as e:
                        st.session_state.analysis_error=str(e) if isinstance(e,ValueError) else 'The analysis service failed or timed out. Check provider configuration and retry. Your context and previous assessments are retained.'
                        failed_run={'id':str(uuid.uuid4()),'reviewer':user,'created':c.now(),'incoming_id':selected['id'],'name':selected['name'],'version':selected['version'],'context':context,'snapshot':c.snapshot(user),'status':'analysis_failed','error':st.session_state.analysis_error,'comparisons':[],'coverage':[],'duration':0,'assessments':[],'decisions':[]}
                        c.save(user,failed_run)
                        if not run or run.get('status')=='analysis_failed':
                            st.session_state.run=failed_run
                        st.rerun()
        st.stop()
    if st.session_state.get('analysis_error'): st.error('Analysis failed · '+st.session_state.analysis_error)
    if not run:
        with st.container(border=True):
            st.subheader('Ready when you are')
            st.write('Confirm the context above to compare this draft against the signed evidence library.')
            note(f"{len(c.documents(user,'signed_contracts'))} signed documents available · No comparisons have run")
        st.stop()
    if run.get('status')=='analysis_failed':
        st.error(run.get('error','Analysis failed. Retry analysis.'))
        st.info('Next: open Deal context & original source above, confirm context and retry analysis. Earlier saved reviews remain in Review history.')
        st.stop()
    stale=run['snapshot']!=c.snapshot(user)
    # Current workflow status is shown in the compact header above.
    if stale: st.warning('Evidence has changed. Previous assessments are preserved. Confirm context and run analysis again before recording a new decision.')
    if step in [2,3]:
        incomplete=sum(item['status']=='incomplete' for item in run['coverage'])
        if incomplete: st.warning(f'{incomplete} document checks are unfinished. This review cannot be completed until those checks are resolved.')
        if step==2 or incomplete: document_checks(run)
    findings=run['comparisons']
    if not findings and step==2:
        st.info('No candidate restriction retrieved. Inspect coverage; this does not clear the contract.')
        if st.button('Continue to decision',type='primary'): st.session_state[stepkey]=3; st.session_state.scroll_target='review-step'; st.rerun()
        st.stop()
    if step==2:
        indexkey='index_'+run['id']
        st.session_state.setdefault(indexkey,0)
        index=min(st.session_state[indexkey],len(findings)-1)
        latest={a['comparison']:a for a in run['assessments']}
        with st.sidebar:
            st.divider()
            st.caption('FINDINGS IN THIS REVIEW')
            for finding_index,finding in enumerate(findings):
                saved=finding_index in latest
                if st.button(f"{finding_index+1}. {finding['title']}",key='finding_nav_'+run['id']+str(finding_index),type='primary' if finding_index==index else 'secondary',use_container_width=True,help='Assessment saved' if saved else 'Assessment not yet saved'):
                    st.session_state[indexkey]=finding_index
                    st.session_state.scroll_target='finding-top'
                    st.rerun()
        st.html('<div id="finding-top" style="scroll-margin-top:70px"></div>')
        st.subheader(f'Finding {index+1} of {len(findings)}')
        st.caption(f'{len(findings)-len(latest)} still need assessment · Save each assessment before continuing.')
        navleft,navright=st.columns(2)
        with navleft:
            if st.button('Previous finding',disabled=index==0): st.session_state[indexkey]=index-1; st.session_state.scroll_target='finding-top'; st.rerun()
        with navright:
            if st.button('Next finding',disabled=index==len(findings)-1): st.session_state[indexkey]=index+1; st.session_state.scroll_target='finding-top'; st.rerun()
        with st.container():
            f=findings[index]
            with st.container(border=True):
                badge(f['outcome']); st.subheader(f['title']); note(f['historical_id'].split('/')[-1].replace('_',' '))
                show=st.toggle('View evidence',key='evidence_'+run['id']+str(index))
                if show:
                    width=st.select_slider('Evidence panel width',options=['Compact','Balanced','Wide'],value='Balanced',key='width_'+run['id']+str(index))
                    detail,source=st.columns({'Compact':[2,1],'Balanced':[1,1],'Wide':[1,2]}[width])
                else:
                    detail=st.container()
                with detail:
                    st.markdown('### What was found'); st.write(f['explanation'])
                    st.markdown('### Why the sources may overlap or differ'); st.write(f['scope'])
                    st.markdown('### Incoming deal versus existing commitment')
                    st.table({'Source':['Incoming deal','Existing commitment'],'Agreement':[selected['name'],f['historical_id'].split('/')[-1].replace('_',' ')]})
                    st.markdown('### Relevant dates & exceptions'); st.write(f['dates'])
                    st.markdown('### Clarification needed'); st.write(f['clarification'])
                if show:
                    with source:
                        st.subheader('Source evidence')
                        if not f['evidence']: st.info('Missing evidence. Request the sources identified below.')
                        for ref in f['evidence']: evidence(ref)
                st.divider(); st.markdown('### Human assessment')
                previous=[a for a in run['assessments'] if a['comparison']==index]
                if previous: st.success('Assessment saved · '+previous[-1]['action']); note(previous[-1]['rationale'])
                # A persistent shadow draft survives switching evidence, comparisons and views.
                draftkey='draft_'+run['id']+str(index)
                st.session_state.setdefault(draftkey,{'action':previous[-1]['action'] if previous else c.ACTIONS[0],'rationale':previous[-1]['rationale'] if previous else ''})
                draft=st.session_state[draftkey]
                actions=[a for a in c.ACTIONS if a!='Accept supported risk' or f['outcome']=='Potential conflict']
                actionkey='action_'+draftkey
                if draft['action'] not in actions: draft['action']='Confirm finding'
                if st.session_state.get(actionkey) not in actions: st.session_state[actionkey]=draft['action']
                action=st.selectbox('Assessment',actions,index=actions.index(draft['action']),key=actionkey,format_func=lambda value: {'Confirm finding':'I agree with this finding','Mark finding incorrect':'I disagree with this finding','Accept supported risk':'Accept this supported risk','Request further review':'Request further review'}.get(value,value))
                if f['outcome']=='No conflict identified in this comparison':
                    st.caption('Agree with the no-conflict conclusion? Choose I agree with this finding. If you disagree, choose I disagree with this finding or Request further review.')
                elif f['outcome']=='Potential conflict':
                    st.caption('I agree with this finding confirms that the conflict exists; it does not resolve it. Accept this supported risk only if authorised. Otherwise request changes, seek further review, or choose Do not proceed in the decision step.')
                rationale=st.text_area('Assessment rationale',value=draft['rationale'],key='rationale_'+draftkey,placeholder='Explain your reasoning and refer to the supporting evidence.')
                st.session_state[draftkey]={'action':action,'rationale':rationale}
                if st.button('Save assessment & continue to decision' if index==len(findings)-1 else 'Save & next',key='save_'+draftkey,type='primary',disabled=stale or bool(run.get('completion')),help='Completed reviews are preserved. Run a new analysis to make renewed assessments.'):
                    try:
                        c.assessment(user,run,index,action,rationale)
                        st.session_state[indexkey]=min(index+1,len(findings)-1)
                        if index==len(findings)-1:
                            st.session_state[stepkey]=3
                            st.session_state.scroll_target='review-step'
                        else: st.session_state.scroll_target='finding-top'
                        st.rerun()
                    except Exception as e: st.error(str(e))
        st.caption('You can record a follow-up decision even if some findings remain unassessed. The remaining work will stay visible.')
        if st.button('Continue to decision',disabled=stale,help='Opens the summary and decision form. Unfinished checks will result in Follow-up needed.'):
            st.session_state[stepkey]=3; st.session_state.scroll_target='review-step'; st.rerun()
        st.stop()
    st.divider()
    decision_brief(run,stale)
    with st.expander('Detailed review summary'): review_summary(run,stale)
    if run.get('completion'):
        st.success('Review completed for this evidence snapshot.' if not stale else 'Earlier review completed; evidence is now outdated.')
        st.caption('This record is preserved. To make a new review, return to step 1 and run analysis again.')
        st.stop()
    st.subheader('Make your decision')
    st.caption('Choose one outcome. The app will explain any work needed before you can save it.')
    choice_draft='decision_choice_draft_'+run['id']
    previous_action=run['decisions'][-1].get('next_step') if run.get('decisions') else st.session_state.get('next_step_draft_'+run['id'])
    initial_choice=st.session_state.get(choice_draft,w.choice_for(previous_action))
    choice=st.radio('Your decision',w.DECISIONS,index=w.DECISIONS.index(initial_choice) if initial_choice in w.DECISIONS else None,key='decision_choice_'+run['id'],help='Proceed refers the review to the authorised signatory; it does not sign the contract. Do not proceed closes the review with that decision. Need more information keeps the review open.')
    st.session_state[choice_draft]=choice
    next_step=w.DECISION_ACTIONS.get(choice)
    checks=w.checklist(run,c.snapshot(user),next_step)
    blockers=[(label,help_text) for label,passed,help_text in checks if not passed and label!='A final next step is selected']
    final_choice=choice in w.DECISIONS[:2]
    pending=w.pending_findings(run,next_step)
    if choice==w.DECISIONS[2]:
        st.info('This will save Follow-up needed. Describe what you need in your reason below. You can return when that information is available.')
    elif final_choice and blockers:
        st.warning('This decision cannot be completed yet. Use the next step below, or choose Need more information to keep the review open.')
    elif final_choice:
        st.success('Ready to complete. Enter your reason, acknowledge the review, and save your decision.')
    else:
        st.info('Select a decision above to see your next step.')
    if pending and choice!=w.DECISIONS[2]:
        st.markdown(f"**Next step: review {len(pending)} outstanding finding(s)**")
        for item in pending:
            st.write(f"**Finding {item['index']+1} — {item['title']}**")
            st.caption(item['reason'])
            if st.button(f"Open finding {item['index']+1}",key='resolve_finding_'+run['id']+str(item['index'])):
                st.session_state['index_'+run['id']]=item['index']
                st.session_state[stepkey]=2
                st.session_state.scroll_target='finding-top'
                st.rerun()
    other_blockers=[label for label,_ in blockers if label not in ['Every comparison has an assessment and rationale','Outstanding findings are addressed']]
    if final_choice and other_blockers:
        st.caption('The document checks or source evidence also need attention. A final decision cannot bypass them.')
        if st.button('Open contract details',key='decision_contract_details'):
            st.session_state[stepkey]=1
            st.session_state.scroll_target='review-step'
            st.rerun()
    decision_draft='decision_draft_'+run['id']
    text=st.text_area('Why is this your decision?',value=st.session_state.get(decision_draft,''),key='decision_'+run['id'],help='For follow-up, describe the information or changes needed. For a final decision, explain why you are referring or stopping this draft.')
    st.session_state[decision_draft]=text
    acknowledged=st.checkbox('I have reviewed the evidence, summary and outstanding items',key='ack_'+run['id'])
    save_label='Save follow-up' if choice==w.DECISIONS[2] else 'Complete review — refer for signing' if choice==w.DECISIONS[0] else 'Complete review — do not proceed' if choice==w.DECISIONS[1] else 'Save decision'
    if st.button(save_label,key='save_review_decision',type='primary',disabled=stale or choice is None or (final_choice and bool(blockers)),help='Final decisions complete the review only after all required checks pass. Follow-up decisions keep it open.',use_container_width=True):
        if not text.strip(): st.error('Enter your decision rationale above.')
        elif not acknowledged: st.error('Confirm that you have reviewed the evidence, summary and outstanding items.')
        else:
            try:
                if final_choice:
                    c.complete_review(user,run,text,next_step)
                    recorded='Review completed'
                else:
                    c.decision(user,run,text,next_step)
                    recorded='Follow-up needed'
                st.session_state.run=run
                st.session_state['recorded_'+run['id']]=recorded
                st.session_state.scroll_target='review-step'
                st.rerun()
            except Exception as e: st.error(str(e))
    if st.session_state.get('recorded_'+run['id']): st.success('Decision saved · '+st.session_state['recorded_'+run['id']])

else:
    st.title('Review history'); st.write('A preserved record of evidence, assessments and human decisions.')
    runs=c.history(user)
    if not runs: st.info('No saved reviews yet. Run an analysis and save your assessment to begin the history.')
    current=c.snapshot(user)
    from src.history import groups,page_slice
    search_col,status_col=st.columns([2,1])
    with search_col: query=st.text_input('Search review history',placeholder='Contract name or Review ID, e.g. REV-000001',key='history_search')
    with status_col:
        selected_status=st.selectbox('Latest review status',['All statuses','Review completed','Follow-up needed','Ready for human review','Analysis failed','Outdated evidence','Human review recorded'],key='history_status',help='Filters each contract by its latest review. Older reviews remain available inside the contract group.')
    filters=(query,selected_status)
    if st.session_state.get('history_filters')!=filters:
        st.session_state.history_page=0
        st.session_state.history_filters=filters
    grouped=groups(runs,current,query,selected_status)
    visible,page_index,page_count=page_slice(grouped,st.session_state.get('history_page',0))
    st.session_state.history_page=page_index
    if grouped:
        note(f'Showing {page_index*10+1}–{page_index*10+len(visible)} of {len(grouped)} contracts · Latest review first · All earlier reviews retained')
    elif runs: st.info('No contracts match these filters. Change the search or select All statuses.')
    for attempts in visible:
        latest=attempts[0]
        label=f"{latest['name']} · {w.status(latest,current)} · {latest['created'][:10]} · {latest.get('review_id','Saved review')}"
        if latest.get('decisions'):
            last=latest['decisions'][-1]
            label+=' · '+('Earlier decision: ' if latest['snapshot']!=current else 'Decision: ')+SHORT_ACTIONS.get(last.get('next_step'),'See rationale')
        with st.expander(label,expanded=False):
            history_entry(latest,current)
            if len(attempts)>1:
                with st.expander(f'Previous reviews ({len(attempts)-1})',expanded=False):
                    for older in attempts[1:]:
                        with st.expander(f"{older['created']} (UTC) · {w.status(older,current)} · {older.get('review_id','Saved review')}",expanded=False):
                            history_entry(older,current)
    if grouped:
        previous_col,page_col,next_col=st.columns([1,2,1])
        with previous_col:
            if st.button('Previous page',disabled=page_index==0,use_container_width=True):
                st.session_state.history_page=page_index-1; st.session_state.scroll_target='workspace-top'; st.rerun()
        with page_col: st.caption(f'Page {page_index+1} of {page_count} · 10 contracts per page')
        with next_col:
            if st.button('Next page',disabled=page_index==page_count-1,use_container_width=True):
                st.session_state.history_page=page_index+1; st.session_state.scroll_target='workspace-top'; st.rerun()
st.markdown('<div class="footer">Synthetic contract dataset · Evidence supports review; human judgement remains essential.</div>',unsafe_allow_html=True)
