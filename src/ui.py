"""Presentation assets; review rules remain in core/workflow."""
import base64

LOGO='''<svg width="36" height="40" viewBox="0 0 36 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M8 3h14l8 8v23a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3Z" stroke="currentColor" stroke-width="2.2"/><path d="M22 3v8h8M11 16h12M11 21h7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="m15 28 4 4 9-10" stroke="#60A5FA" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
LOGO_IMAGE='<img width="42" height="46" alt="" src="data:image/svg+xml;base64,'+base64.b64encode(LOGO.replace('currentColor','#F8FAFC').encode()).decode()+'">'
BRAND=f'<div class="brand"><span class="brand-symbol">{LOGO_IMAGE}</span><div><div class="brand-name">AtliQ</div><div class="brand-product">Contract Risk Analyzer</div></div></div>'
CSS='''<style>
:root{--ink:#172033;--line:#E5E9F0;--accent:#2563EB}
.stApp{background:#F7F8FA;color:var(--ink)}
.block-container{max-width:1320px;padding:2.2rem 3.2rem 4rem}
header[data-testid="stHeader"]{background:#F7F8FAE8}
h1{font-size:2.15rem!important;line-height:1.2!important;letter-spacing:-.045em;font-weight:650!important;margin-bottom:.4rem!important}
h2{font-size:1.3rem!important;font-weight:600!important}h3{font-size:1.05rem!important;font-weight:600!important}
p{line-height:1.65} [data-testid="stCaptionContainer"]{color:#64748B}
.brand{display:flex;align-items:center;gap:12px;margin:8px 0 26px}.brand-symbol{color:#F8FAFC;background:#14233E;display:grid;place-items:center;width:60px;height:64px;border-radius:14px}.brand-name{font-size:30px;letter-spacing:-1px;font-weight:750;line-height:1.2}.brand-product{font-size:12px;color:#64748B;margin-top:3px}
[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid var(--line)}
[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:1.5rem}
[data-testid="stSidebar"] [role="radiogroup"]{gap:6px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:11px 14px;border-radius:8px;width:100%;font-weight:500}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#EFF4FF;color:#1D4ED8}
[data-testid="stSidebar"] [role="radiogroup"] label>div:first-child{display:none}
div[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:var(--line)!important;border-radius:12px!important;background:white}
[data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:10px!important;background:white}
[data-testid="stExpander"] summary{padding:14px 16px!important}
div.stButton>button{border:1px solid #D5DDE8;border-radius:8px;min-height:42px;font-size:14px;font-weight:550;background:white;color:#334155;transition:background .15s,border-color .15s}
div.stButton>button:hover{background:#F1F5FB;border-color:#93ACD5;color:#1D4ED8}
div.stButton>button[kind="primary"]{background:#2563EB;color:white;border-color:#2563EB}
div.stButton>button[kind="primary"]:hover{background:#1D4ED8;color:white}
div.stButton>button:disabled{opacity:.45}
div[data-baseweb="input"],div[data-baseweb="textarea"],div[data-baseweb="select"]>div{border:1px solid #CFD8E5!important;border-radius:8px!important;background:white!important}
[data-testid="stForm"]{border-color:var(--line);border-radius:12px;padding:20px}
.badge{font-size:12px;font-weight:550;display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border:1px solid #E2E8F0;background:#F1F5F9;border-radius:6px;white-space:normal;color:#475569}
.badge:before{content:'';height:6px;width:6px;border-radius:50%;background:currentColor;flex-shrink:0}
.badge.amber{color:#9A6700;background:#FFF8E6;border-color:#F7E4B5}.badge.green{color:#16724C;background:#EDF8F2;border-color:#CDEBD9}.badge.blue{color:#2456A8;background:#EDF3FE;border-color:#D7E4FC}.badge.red{color:#AE3B3B;background:#FFF1F1;border-color:#F5D7D7}
.eyebrow{font-size:11px;letter-spacing:.14em;color:#64748B;font-weight:650;margin-bottom:10px}
.contract-title{font-size:16px;font-weight:600;letter-spacing:-.015em}.muted{color:#64748B;font-size:13px}
.queue-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:20px 0 28px}
.queue-stat{background:white;border:1px solid var(--line);border-radius:12px;padding:18px 22px}.queue-stat strong{display:block;font-size:28px;font-weight:650;letter-spacing:-1px;margin-bottom:4px}.queue-stat span{color:#64748B;font-size:12px}
.queue-heading{display:grid;grid-template-columns:5fr 2fr 1.5fr;gap:16px;padding:12px 18px;color:#64748B;font-size:11px;letter-spacing:.07em;text-transform:uppercase}
[data-testid="stHorizontalBlock"]:has([class*="st-key-stage_"]){padding:12px;background:#EDF1F7;border-radius:12px}
.evidence{border-radius:8px;background:#F8FAFD;border-left:3px solid #3B82F6}
.footer{font-size:12px;color:#94A3B8;border-color:var(--line)}
@media(max-width:760px){.block-container{padding:1.25rem}.queue-stats{grid-template-columns:repeat(2,1fr);gap:8px}.queue-stat{padding:14px}.queue-heading{display:none}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>'''
