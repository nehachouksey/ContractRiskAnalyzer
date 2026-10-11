# Product Requirements Document — AtliQ Contract Risk Analyzer

**Date:** 2026-10-04  
**Updated:** 2026-10-11 — user-approved PDF and Word intake extension  
**Author:** Neha Chouksey  
**Document:** Vibe-coding implementation PRD — version 1.1  
**Scope:** MVP 1 — Step 4: Historical Obligation and Conflict Check  
**Source of truth:** `AtliQ_Contract_Risk_Analyzer_AI_PRD_v2.docx` supplied by the user. Its cover states version 1.1 — Step 4 alignment; this document retains its requirements.  
**Format reference:** `PRD.md` — the supplied telecom PRD provides the 12-section structure only.

This is a separate implementation document. Do not overwrite either source. Product requirements below come from the final Word PRD. The proposed implementation defaults in Sections 9 and 12 translate those requirements into a practical prototype; they are not claims about AtliQ’s existing systems or tested performance. If a technical choice conflicts with the product requirements, preserve the product requirement and document the change.

---

## 1. Overview

Build a human-in-the-loop contract review application using Retrieval-Augmented Generation (RAG) with rule-based checks. It compares an incoming contract with historical exclusivity and non-compete commitments and presents a concise, evidence-linked review brief.

The Authorised Contract Reviewer inspects findings, resolves uncertainty and records an assessment and review decision. Signing remains with the Authorised Signatory outside the application.

MVP 1 focuses on Step 4. Include only the clause extraction from Step 3 needed for these comparisons. The application must not independently approve, reject, renegotiate or sign contracts, or provide definitive legal advice.

**Main workflow:** Select incoming contract → confirm context → retrieve signed commitments → compare scope, dates and exceptions → validate findings and references → show review brief → record human assessment and review decision.

Missing evidence produces a visible clarification request. Changed evidence requires renewed comparison and human review.

---

## 2. Problem Statement

AtliQ has no legal team. Karandeep, the CEO, reviews and signs contracts alongside his other responsibilities. Contract volume is growing while sellers wait for review.

Existing obligations are fragmented across signed documents, negotiation history and personal memory. A new contract can appear acceptable in isolation while conflicting with an earlier commitment. Reviewers must reconstruct that context manually.

**Root cause:** AtliQ lacks accessible institutional contract knowledge that can be applied during a new contract review.

**Job to be done:** When a new contract arrives, help the reviewer find and understand overlap with existing commitments so they can decide what needs clarification, challenge or further review.

---

## 3. Goals

| Goal | Measure |
|---|---|
| Increase reliable review capacity | Correctly completed conflict reviews per reviewer hour |
| Reduce evidence-search and assessment effort | Active review time compared with manual review of similar cases |
| Find relevant historical restrictions | Evaluator-confirmed conflicts missed, reported with counts and denominator |
| Avoid incorrect findings | Incorrect findings divided by all evaluated findings; accepting a real risk does not make it incorrect |
| Support findings with evidence | Correct source versions, relevant passages and explanations supported by those passages |
| Make incomplete checks visible | Correct identification of missing evidence and affected comparisons |

### 3.1 Measurement Rules

- Count each completed contract review once. Include active reviewer time spent on unfinished reviews in the denominator of the North Star metric.
- Establish a manual baseline and agree numerical targets before final evaluation. Do not invent accuracy, time-saving, cost or latency targets.
- Report unresolved cases separately. Report `Not applicable` when a rate has no applicable cases.
- Measure application analysis time separately from human review time. Do not infer active reviewer time from elapsed wall-clock time alone.
- Results describe the synthetic evaluation only; they do not prove real-contract performance or financial returns.

### 3.2 Evaluation Required for MVP

Compare at least two pretrained model configurations on the same evaluator-confirmed cases. Include a keyword-and-rules baseline and test systematic comparison against all extracted candidate restrictions. Separate development cases from final evaluation cases. Record retrieval failures separately from reasoning errors.

| Dataset case | Proposed expectation, subject to evaluator confirmation |
|---|---|
| Gulf Crown / Al Noor | Identify potential overlap between Saudi hotel analytics work and Al Noor’s GCC hospitality restriction. |
| BlueOrchid / Al Noor | Account for Dubai and Muscat properties in the schedule; do not rely only on Indian headquarters. |
| Al Noor’s Seaside waiver | Limit consent to the specified engagement; do not generalise it to other clients, services or affiliates. |
| Datavane / CloudSpan | Assess partnership overlap in India and GCC without extending CloudSpan’s restriction to Europe. |
| Orbit’s expired restriction | Consider expiry and the continuing restriction period as of the dataset review date; do not clear the deal against other agreements. |
| Missing Seaside SOW | Report missing evidence when the SOW is needed to determine waiver applicability. |

These are evaluation hypotheses, not completed test results. Never hard-code outcomes by customer name. Keep expected labels outside the model’s runtime evidence context.

---

## 4. Non-Goals

- Comprehensive clause-risk review, including general liability, indemnity and NDA fairness.
- General entity/jurisdiction compliance and paperwork checks. Entity information and missing documents remain relevant to scoped conflict comparisons.
- OCR processing, scanned/image-only PDFs and legacy Word `.doc` ingestion. Text-based PDF and Word `.docx` intake are included by the user-approved 2026-10-11 scope extension. Continue reading the supplied Markdown without modifying it.
- Live email, drive or CRM integrations.
- Seller dashboards and post-signature obligation management.
- Automated negotiation, redlining, approval, rejection or signing.
- Fine-tuning or autonomous agents.
- Real-contract rollout as part of the current synthetic-data demonstration.

---

## 5. Users

| User or role | Responsibility |
|---|---|
| Authorised Contract Reviewer — primary application user | Confirms context, inspects evidence, assesses findings and records the review decision. |
| Karandeep — current scenario persona | CEO, primary reviewer and signatory in the supplied scenario. Do not hard-code his name as the application role. |
| Authorised Signatory | Retains signing authority outside the app. Review access does not grant signing authority. |
| Bhavin, Dhaval and Jay — business stakeholders | Bhavin and Dhaval are founders; Jay is a sales executive. They bring contracts in and wait for review. |
| Evaluator — test responsibility | Confirms expected findings and supporting evidence; the person remains to be identified. |

These role distinctions are product design, not a claim that AtliQ has separate review and signing teams.

---

## 6. Functional Requirements

Keep these IDs aligned with the final Word PRD. **Must** is required for MVP completion; **Should** follows a working core; **Could** is optional.

### 6.1 Contract Intake and Evidence Preparation

| ID | Requirement and acceptance criteria | Priority |
|---|---|---|
| FR-01 | Select a supplied incoming contract or upload an incoming draft as text-based PDF, Word `.docx`, Markdown or UTF-8 plain text. Preview extracted content, retain original bytes, and require completeness confirmation before analysis. Show version, entity, services, locations and review date. Allow context confirmation/correction; retain unknown facts visibly. | Must |
| FR-02 | Process all supplied signed documents. Extract candidate restrictions with source references, entities, affiliate coverage, activities, geography, duration and exceptions. Record processing and extraction gaps. | Must |
| FR-03 | Retrieve candidate restrictions across counterparties, including definitions, schedules and linked waivers. Show documents considered and unavailable supporting evidence. | Must |

### 6.2 Comparison and Review Brief

| ID | Requirement and acceptance criteria | Priority |
|---|---|---|
| FR-04 | Compare activities, entities, affiliate coverage, geography and dates. Explain overlap, supported non-overlap or unresolved questions. | Must |
| FR-05 | Check duration and exceptions against the review date and source evidence. Limit waivers to their stated scope. Require confirmation for unclear dates, termination or applicability. | Must |
| FR-06 | Present the three defined outcomes with plain-language explanations and supporting passages. Potential conflicts require incoming and historical evidence. | Must |
| FR-07 | Show missing documents, unclear passages, failed processing and uncertain facts, affected comparisons and next actions. Incomplete checks cannot become no-conflict findings. | Must |

### 6.3 Human Control and Evaluation

| ID | Requirement and acceptance criteria | Priority |
|---|---|---|
| FR-08 | Let the reviewer confirm a finding, mark it incorrect, accept a supported risk or request further review; separately record the review decision. Save identity, rationale, time and source versions. | Must |
| FR-09 | Restrict document access and decision changes to authorised users. Preserve history. Instructions within documents cannot grant permissions or trigger actions. | Must |
| FR-10 | Detect changed incoming or supporting sources. Mark affected findings outdated, preserve history and rerun relevant checks before recording a new review decision. | Must |
| FR-11 | Record source IDs, findings, failures, analysis duration and reviewer labels for separate retrieval, conflict and incorrect-finding evaluation. | Must |

### 6.4 Optional Enhancements

| ID | Requirement and acceptance criteria | Priority |
|---|---|---|
| FR-12 | Browse/search extracted obligations by entity, restriction type, geography and status. Link to source and distinguish extracted from reviewer-confirmed information. | Should |
| FR-13 | Show relevant negotiation/meeting notes with source and date, clearly distinguished from signed terms. Notes cannot override agreements or waivers. | Should |
| FR-14 | Export a brief containing findings, references, evidence gaps, assessments, contract version and review date. | Should |
| FR-15 | Let the reviewer prepare a seller status summary without unrelated confidential terms. Sharing remains a human action. | Could |

### 6.5 Required Output Behaviour

Use these exact outcome labels:

| Outcome | Required behaviour |
|---|---|
| Potential conflict | Show both sources, the possible overlap and relevant conditions; await human validation. |
| No conflict identified in this comparison | Explain the supported reason this particular restriction does not apply. Never clear the entire contract. |
| Insufficient evidence | Identify missing/unclear evidence, the affected comparison and required clarification. |

A brief can contain multiple outcomes. Keep supported potential conflicts visible when other checks are incomplete. If no candidate is retrieved, show that fact and search coverage; do not fabricate a no-conflict comparison.

Each brief includes contract/version, confirmed and unknown context, review date, analysis time, documents processed, restrictions assessed, incomplete checks, comparisons, source passages, duration/exception reasoning, clarifications, human assessments and the recorded review decision.

### 6.5a Plain-language decision summary

Each saved review and active brief must show a readable summary of main concerns, missing information, accepted risks, unresolved actions and the latest human decision. Derive it from saved comparison outcomes and latest human assessments; do not create new findings or an AI signing recommendation. Keep disputed findings visible with the human rationale. Confirming a potential conflict does not resolve it; accepting a supported risk does not erase it. Missing evidence remains unresolved even after an assessment.

End with a human-selected next step: seek clarification, request changes or a specific waiver, request further review, refer to the authorised signatory for a signing decision, or do not proceed with this draft. Require rationale and preserve prior decisions. A referral is not approval, clearance or signature. Mark summaries based on outdated evidence prominently and require renewed analysis before recording a new decision. Scope is historical restrictions only; other signing checks remain outside this brief.

### 6.6 Processing States

| State | Behaviour |
|---|---|
| Processing | Show progress; results are not yet a completed brief. |
| Ready for human review | Show comparisons and gaps; this does not mean the contract is cleared. |
| Analysis failed | Explain failure, identify unfinished checks and allow retry without losing saved work. |
| Outdated evidence | Preserve prior findings; require rerun and renewed review before a new decision. |
| Human review recorded | Show reviewer, rationale and time; keep accepted risks and unresolved items visible. |

Store run status separately from per-comparison outcomes. Source changes may make a previously reviewed run outdated without erasing its recorded assessments.

### 6.7 Four Mapped Guardrails

1. **Supporting evidence:** show relevant incoming and historical passages and explain the comparison.
2. **Human validation:** an authorised reviewer checks potential conflicts before action.
3. **Human decision authority:** AI cannot independently approve, reject or renegotiate; signing is outside the app.
4. **Confidentiality:** only authorised users may access contract evidence and recorded decisions.

---

## 7. Non-Functional Requirements

| ID | Requirement and verification |
|---|---|
| NFR-01 | Show progress, timeouts and retry. Measure latency; agree targets after initial testing. |
| NFR-02 | Persist reviews across interruption/restart. Retrying must not duplicate saved assessments or mark incomplete work complete. |
| NFR-03 | Preserve source versions and references. Test missed conflicts, unsupported explanations and contradictory results. |
| NFR-04 | Show processing coverage and gaps. No silent skipping of unsupported files or unclear text. |
| NFR-05 | Enforce authorisation in data-access and write operations, not just UI visibility. Test unauthorised access and document-text attempts to override rules. |
| NFR-06 | Use synthetic data; avoid unnecessary contract text in technical logs. Agree data handling before real-contract use. |
| NFR-07 | Use plain-language outcomes, accessible evidence and clear next actions. Do not rely on colour alone. |
| NFR-08 | Retain review history and mark affected findings outdated after source changes. |
| NFR-09 | Record model/configuration, usage and estimated analysis cost where available. Unknown pricing remains unknown, not zero. |
| NFR-10 | Keep secrets out of code and version control. Provide an example configuration without credentials. |
| NFR-11 | Use a project-local virtual environment and reproducible dependency file. Document the runtime actually tested; do not claim untested compatibility. |

NFR-10 and NFR-11 are implementation hygiene adopted from the Markdown template. Other rows implement the final PRD’s non-functional requirements.

---

## 8. Data Sources

### Local Project and Dataset Setup

**Existing project folder:**

```text
/Users/nitinsuryawanshi/Desktop/Capstone_Codebasics/Neha Project/AtliQ Contact Analyser Project
```

**Existing dataset folder (verified):**

```text
/Users/nitinsuryawanshi/Desktop/Capstone_Codebasics/Neha Project/AtliQ Contact Analyser Project/Dataset
```

Place this Markdown document in the project folder as `PRD.md` and open that folder as the coding workspace. The dataset is already present; do not download, recreate, move or overwrite it. The project folder name is a filesystem path; the product name remains **AtliQ Contract Risk Analyzer**.

Use these project-relative settings in `.env.example` and the local configuration:

```dotenv
DATASET_DIR=./Dataset
STORAGE_DIR=./storage
DEFAULT_REVIEW_DATE=2026-09-28
```

Resolve relative paths against the project root containing `PRD.md`, not the terminal’s current working directory. Allow configuration overrides without hard-coding this computer’s absolute path in application code. Paths contain spaces; quote them when using terminal commands.

Before building ingestion, read `Dataset/README.md` and verify the supplied inventory: 17 signed Markdown documents, 15 incoming Markdown drafts, four meeting notes and 48 tracker rows, plus the supporting files below. Report missing, unreadable or unexpected files rather than silently substituting sample data. These counts describe the current supplied dataset; future documented additions must not be blocked by hard-coded count checks.

Read source files without modifying them. Store generated indexes, extracted records and review history under `./storage`. Keep evaluation answers outside the searchable evidence. Do not ingest `PRD.md`, generated outputs or test answer sheets as contractual evidence.

For a cloud coding environment, upload the complete project/dataset structure and retain these relative paths; the local absolute path above is a location reference, not remote access.

### Supplied Files

| Source | Format / supplied quantity | Use and authority |
|---|---|---|
| `signed_contracts/` | 17 Markdown documents | Primary historical evidence: commitments, restrictions and signed waivers. Extract candidates from every document. |
| `incoming/` | 15 Markdown drafts | Select a draft for review; never treat it as an executed commitment. |
| `atliq_entities.md` | Markdown | Entity identity and relationships; interpret with the agreement’s affiliate definition. |
| `contract_tracker.csv` | CSV, 48 rows | Document location/status and context; does not replace signed evidence. |
| `negotiation_notes.md` | Markdown | Optional context after the core works; not a signed amendment. |
| `meeting_notes/` | Four Markdown notes | Optional context and leads; not authority to override executed terms. |
| `karandeep_contract_checklist.md` | Markdown | Background guidance relevant to the scoped check only. |
| `README.md` | Markdown | Dataset conventions and reference date; not contractual evidence. |

**Evaluation review date:** `2026-09-28`, stored with each run. The PRD creation date is different and must not silently replace it.

### 8.1a Incoming upload extension approved 2026-10-11

This extension supersedes the original PDF-ingestion exclusion only for incoming drafts. It does not add general legal review or change the synthetic evaluation corpus.

- Accept `.pdf`, `.docx`, `.md` and `.txt` through the authorised Contracts UI; limit uploaded originals to 2 MB and PDFs to 200 pages. Reject malformed, encrypted, empty and unsupported documents with a next action.
- Extract PDF text locally with page references. Detect pages without readable text and show **OCR required**; do not submit partial extraction as a complete draft. PDFs containing images or interactive forms require a verified text-only/flattened copy because those contents are not reliably extracted in this increment.
- Extract Word body paragraphs and tables in document order, plus headers, footers, footnotes and endnotes, retaining paragraph/table/cell references. Word page numbers are not available from OOXML and must not be invented. Flag extraction limitations; embedded objects, images, tracked changes and unsupported content require a verified text-only copy with changes resolved.
- Show the extracted text and format-specific limitations for reviewer verification. Require explicit confirmation that all clauses, schedules, tables, definitions and exceptions are complete before saving the draft and starting context confirmation.
- Retain the original file bytes, safe filename, content hash, extraction version and extracted text under generated storage, outside the supplied dataset. Expose original download in the workspace and incoming evidence viewer, with server-side authorisation.
- Reuploading identical original bytes reuses the existing draft for that reviewer. Revised bytes create a new draft/version and preserve prior history. Do not treat extracted text or reviewer corrections as a signed amendment.
- Upload alone never runs analysis. Uploaded contracts default to the current review date; supplied synthetic cases retain 2026-09-28. Reviewer confirms the date before comparisons.
- Test text PDFs, Word paragraphs and tables, original persistence, duplicate upload, malformed input, empty/scanned PDFs, oversized files, old-database migration and denied access. Extraction tests do not establish legal correctness or full format fidelity.

### 8.1 Ingestion Rules

- Register document ID, source type, content hash/version and processing status.
- Preserve original text, headings, clauses and line references. Segment by contractual sections, preserving links to definitions and schedules; do not blindly reuse 600-character chunks.
- Link restrictions, definitions, duration clauses and waivers through explicit source references. Similar names do not prove applicability.
- Keep complete source versions available for inspection; select relevant passages for model context.
- Record uncertain extractions and missing fields as unknown. Each extracted fact must have source evidence or a recorded reviewer correction.
- Re-ingestion of unchanged content must not create duplicate current records. Retain old versions when content changes.
- Track removal, replacement, additions and extraction-configuration changes. Reassess affected coverage; a newly added restriction may affect existing reviews even if it was not previously cited.

### 8.2 Known Limitations

The Seaside SOW referenced by the Al Noor waiver is listed in the tracker but absent from the supplied contract files. Report it as unavailable when needed. One Markdown document contains OCR errors; this is not a requirement to build OCR.

Do not use external legal material or model memory as evidence of AtliQ’s obligations. The derived obligation register is a search/comparison aid, not automatically confirmed company policy.

---

## 9. System Architecture

### 9.1 Proposed Implementation Defaults

These are build choices for the prototype, not additional product scope or previously validated technology decisions.

| Layer | Default |
|---|---|
| UI | Streamlit review workspace, rather than a chat-first interface |
| Application | One Python application with separate ingestion, retrieval, comparison, validation and persistence modules |
| Orchestration | LangChain where useful for retrieval/model adapters; ordinary Python for dates, permissions and persistence |
| Evidence search | Local persistent Chroma store for semantic retrieval, with source/version metadata |
| Structured records | SQLite for source register, candidate obligations, review runs, findings and human assessments |
| Embeddings | Configurable local pretrained embedding model; selection subject to retrieval testing |
| LLM | Configurable provider/model adapter; Groq is a candidate from the reference app, not a locked selection |
| Access | Authenticated identity plus server-side reviewer permissions; choose provider/configuration before a shared deployment |

Do not hard-code the telecom model ID, reasoning setting, top-three retrieval limit or performance targets. Verify selected-provider support during implementation. Low temperature is not a guarantee of truth or determinism.

### 9.2 Architecture Flow

```text
Evidence preparation
  Supplied signed Markdown + supporting sources
    -> preserve source versions and section references
    -> extract candidate obligations and evidence gaps
    -> SQLite: structured register + Chroma: searchable passages

Review workflow
  Authenticated, authorised reviewer
    -> select incoming draft and confirm deal context/review date
    -> retrieve candidate restrictions across counterparties
    -> expand evidence with definitions, schedules and signed waivers
    -> AI scope comparison + rules using supported date inputs
    -> validate structured output, citations and evidence support
    -> review brief: findings + sources + coverage + clarifications
    -> human assessment and review decision saved in SQLite

Source/context changes
    -> mark affected review stale; preserve history
    -> rerun comparisons -> require renewed human review
```

### 9.3 Retrieval and Comparison Rules

Start by testing systematic comparison against all extracted candidate restrictions in this small corpus. Use semantic retrieval and keyword matching to locate supporting evidence; do not let a fixed top-k silently exclude relevant restrictions. Record which candidates were assessed and which were not.

Search across counterparties. Do not exclude a document solely because its company or headline geography differs from the incoming deal. Expand retrieved clauses to include referenced definitions, schedules, dates and exceptions. If evidence is too large for one request, process comparisons separately and merge their results without losing coverage records.

The LLM extracts and interprets wording. Application code validates source identifiers, calculates dates from confirmed inputs, enforces permissions and tracks versions. Humans resolve uncertainty and decide what action to take.

Use structured, schema-validated output rather than a free-text-only parser. A reference must resolve to the stored version and passage. Citation existence does not establish semantic correctness; test evidence support and require human validation. Reject malformed output or mark affected comparisons incomplete, with an explicit error; never silently convert failures into no conflict.

### 9.4 Proposed Minimum Data Model

| Record | Required information |
|---|---|
| Source version | Source ID/type/path, content hash, preserved content, processing status and timestamp |
| Passage | Passage ID, source version, section/clause, line range and exact text |
| Candidate obligation | ID/type, entities, affiliate wording, activity, geography, duration, exceptions; field-level references, unknowns and confirmation state |
| Review run | ID, incoming version, confirmed context and revisions, review date, reviewer ID, source/index snapshot, model/prompt versions, status, timing and usage |
| Comparison | Run/obligation IDs, outcome, scope explanation, incoming/historical references, exception reasoning, gaps and clarification needed |
| Human assessment | Comparison ID, authorised reviewer, assessment, rationale, timestamp and reviewed source versions |
| Review decision | Run ID, reviewer, decision text, unresolved items, timestamp and source snapshot |
| Evaluation record | Case/split, expected references and labels, actual findings, evaluator labels and measured results |

Use stable IDs and explicit relationships. Store human assessments as history; do not overwrite them with AI output. Separate model findings from human labels. Store evaluation expectations separately from retrieval evidence.

**Upload storage:** add original bytes/filename, format, original content hash, extraction implementation version, extracted text, extraction warnings and authorised owner. Existing text-only uploads remain readable after schema migration. Original downloads must check the authorised owner.

**Comparison payload:** `comparison_id`, `obligation_id`, `outcome`, `explanation`, `scope_comparison`, `incoming_evidence[]`, `historical_evidence[]`, `duration_and_exceptions`, `evidence_gaps[]`, `required_clarification[]`.

Each evidence reference contains `source_id`, `version`, `passage_id` and exact quoted text. Enforce the three allowed outcome labels. Do not request invented numeric confidence or severity scores.

### 9.5 Proposed Workspace Layout

```text
PRD.md                         # this implementation specification
Dataset/                       # existing supplied sources; preserve unchanged
  incoming/
  signed_contracts/
  meeting_notes/
  contract_tracker.csv
  atliq_entities.md
  negotiation_notes.md
  karandeep_contract_checklist.md
  README.md
app.py                         # review UI
src/
  auth.py                      # identity and permissions
  ingest.py                    # source registration/versioning
  extract.py                   # context and candidate obligations
  retrieve.py                  # candidate/evidence retrieval
  compare.py                   # model comparison and date rules
  validate.py                  # output and citation checks
  storage.py                   # SQLite persistence/history
  evaluate.py                  # evaluation runner, separate labels
storage/                       # generated DB and search index
  reviews.sqlite
  chroma/
tests/                         # acceptance and failure-path tests
evaluation/                    # evaluator-confirmed cases/results
.env.example                   # no secrets
requirements.txt
README.md                      # setup, ingestion, run and evaluation
```

Suggested configuration: `DATASET_DIR`, `STORAGE_DIR`, `LLM_PROVIDER`, `LLM_MODEL`, provider credentials, `EMBEDDING_MODEL`, and `DEFAULT_REVIEW_DATE=2026-09-28`. Authentication configuration depends on the selected identity provider. Do not ship an enabled authentication bypass.

### 9.6 UI Requirements

1. Contract selection and context confirmation.
2. Analysis progress with clear failure/retry behaviour.
3. Review brief with comparison outcomes, evidence and coverage.
4. Source viewer that opens the exact referenced version/passage.
5. Human assessment and review-decision forms with saved history.

A chat interface, CLI conversation and token streaming are not required. Show analysis progress without displaying unvalidated text as a completed finding. Keep implementation terms and model configuration out of the main review flow unless needed to explain a failure.

---

## 10. User Stories

| ID | As a... | I want to... | So that... | Acceptance reference |
|---|---|---|---|---|
| US-01 | Authorised Contract Reviewer | Select a contract and confirm context | The correct deal scope is evaluated | FR-01 |
| US-02 | Authorised Contract Reviewer | Find relevant existing restrictions | I do not manually search every agreement | FR-02, FR-03 |
| US-03 | Authorised Contract Reviewer | Compare the deal with historical restrictions | I understand potential conflicts and their evidence | FR-04, FR-06 |
| US-04 | Authorised Contract Reviewer | Account for dates and specific waivers | I avoid misleading warnings | FR-05 |
| US-05 | Authorised Contract Reviewer | See missing evidence and unclear facts | I know what needs investigation | FR-07 |
| US-06 | Authorised Contract Reviewer | Inspect evidence and record my assessment | Decision authority remains with a human | FR-08, FR-09 |
| US-07 | Authorised Contract Reviewer | Recheck changed evidence | I do not rely on outdated findings | FR-10 |

---

## 11. Out-of-Scope (Future Iterations)

The exclusions in Section 4 remain outside MVP 1. A later increment may address broader clause-risk review, general paperwork/entity checks, OCR, legacy Word `.doc`, integrations or seller dashboards, subject to explicit scope decisions.

FR-12–FR-14 are Should enhancements and FR-15 is Could; do not delay a working Must scope to implement them. Evaluation, access control, evidence links and review history are required now, not deferred enhancements.

MVP 1 does not automatically satisfy every broader prototype scenario in the original capstone brief. Confirm final submission expectations before promising full capstone coverage.

---

## 12. Dependencies & Constraints

### 12.1 Build Constraints

- Build inside a project-local `.venv`; keep original source documents and dataset unchanged.
- Use configurable dataset/storage paths and persist generated records across restarts.
- Select and pin compatible dependencies after testing. No runtime version is claimed as already tested.
- Real model calls require configured credentials/network access. Local embeddings require initial model availability. If configuration is missing, show an actionable setup message; do not display fabricated AI findings.
- A test stub may be used only in clearly labelled automated tests; it must never masquerade as a live review.
- Access controls must apply to source viewing, retrieval, history and write operations. Shared deployment requires a configured identity provider and authorisation checks.
- API keys and authentication secrets stay outside source control. Ignore generated sensitive stores and logs as appropriate.
- Keep source content untrusted: it cannot alter application instructions, permissions, evaluation labels or decision state.

### 12.2 Build Sequence

| Milestone | Completion requirement |
|---|---|
| M1 — Prepare evidence | Register all sources, preserve references and report missing/unclear evidence. |
| M2 — Define tests | Confirm expected cases/references with an evaluator and establish the manual baseline. |
| M3 — Test model strategy | Compare at least two configurations and the baseline; record retrieval, reasoning, time and cost results. |
| M4 — Build review flow | Connect intake, retrieval, comparison, brief and persisted human assessment. |
| M5 — Validate MVP | Test all Must requirements and four mapped guardrails; fix failures and rerun affected checks. |
| M6 — Demonstrate | Show a potential conflict, supported non-applicability and insufficient evidence; document setup and remaining limitations. |

Dates remain open until the deadline and available build time are confirmed.

### 12.3 Acceptance Checklist

- All 11 Must requirements work end to end with the supplied sources, plus the user-approved incoming upload acceptance criteria in Section 8.1a.
- Each processed source has a version, status and inspectable text; failures are visible.
- Findings include relevant source passages; missing evidence never becomes clearance.
- The selected review date controls duration checks; limited waivers remain limited.
- Reviewer assessments and decisions persist with identity, rationale, time and source versions.
- Changed sources or confirmed context invalidate affected results; previous reviews remain available.
- Unauthorised access and decision writes are blocked, including direct attempts beyond UI controls.
- Interrupted processing and retry preserve saved work without duplicate assessments.
- Evaluation separates retrieval misses, reasoning errors, incorrect findings and unresolved checks.
- All four mapped guardrails pass. Remaining performance limitations and open decisions are documented.
- Setup, ingestion, run and evaluation instructions reproduce the demonstrated workflow.

These are acceptance requirements, not statements that the app has already passed them. Numerical performance acceptance remains pending agreement.

### 12.4 Open Decisions

| Decision | Required next step |
|---|---|
| Evaluator | Identify who confirms expected findings and evidence. |
| Numerical quality/time/cost targets | Measure baseline and initial results; agree before final evaluation. |
| Model, embedding configuration and hosting | Compare candidate configurations; verify provider support and data handling. |
| Identity provider and authorised reviewers | Configure authentication and explicit reviewer permissions before shared use. This is an implementation detail of the existing access requirement. |
| Submission date and build time | Confirm before committing to dates or optional features. |
| Broader capstone submission scope | Check original brief expectations beyond Step 4 MVP 1. |

### 12.5 Source Traceability

| This implementation PRD | Final Word PRD sections |
|---|---|
| Overview, problem and scope | 1–3 and 13 |
| Goals and evaluation | 11–12 |
| Users and user stories | 4 |
| Functional requirements | 6; original FR-01–FR-15 preserved |
| Outcomes, statuses and guardrails | 9–10 |
| Non-functional requirements | 8, plus clearly identified template implementation hygiene |
| Data and processing | 5 and 7 |
| Architecture | Implementation of 5–9, with proposed stack/schema defaults explicitly identified |
| Build sequence, acceptance and open decisions | 14–16 |

The source PRD references the discovery workbook, AI Opportunity Mapping, original capstone brief, agreed revisions and supplied synthetic dataset. This implementation document does not introduce new legal conclusions, business facts or measured results.


### Workflow completion extension approved 2026-10-11

Display shared workflow status and next-action guidance across Contracts, the workspace and collapsed history rows. Use Not reviewed, Analysis in progress (transient), Analysis failed, Ready for human review, Follow-up needed, Human review recorded (legacy records only), Review completed and Outdated evidence. Failed analysis attempts are saved without invented completed comparisons; earlier reviews remain intact.

Expose a completion checklist with plain-language blocking reasons and tooltips as supplementary help. Complete review requires current evidence, successful analysis with source coverage and no incomplete checks, at least one comparison, a rationale-based assessment on every comparison, no missing-evidence/disputed/further-review findings, overall rationale and explicit reviewer acknowledgement. A supported potential conflict must be explicitly accepted to refer for signing; alternatively, a confirmed conflict can support completing the review with **Do not proceed with this draft**. Requests for clarification, changes or further review remain follow-up decisions. Enforce completion rules server-side as well as in the UI.

Record completion identity, timestamp, next step, rationale and evidence snapshot. Preserve completed reviews as read-only; renewed analysis creates a new run. Legacy decisions are not automatically promoted to completion. Changed evidence makes a completed review outdated while retaining its original completion. Completion is a human review record, not approval or execution of a contract.


### Simplified three-step interaction approved 2026-10-11

The preceding completion criteria remain in force, but replace separate completion/follow-up buttons and the visible checklist with one guided flow:

1. **Add contract:** select/upload, check original/extracted content and confirm context; one primary **Analyse contract** action.
2. **Review findings:** show one finding at a time, with evidence adjacent on demand, a finding counter and saved-assessment progress. **Save & next** persists the assessment and advances. Previous/Next permit revisiting without clearing draft rationale. Coverage remains expandable and incomplete checks stay visible. After all assessments, proceed to decision; reviewers may also proceed earlier to record follow-up.
3. **Record decision:** show the plain-language summary, chosen next action and rationale. Explain in advance whether the saved status will be Review completed or Follow-up needed and give concrete remaining-work messages. Use one **Record decision** action; require rationale and explicit acknowledgement. Backend rules determine completion automatically from the same criteria. This automatic status calculation never chooses the human decision or signs a contract.

Show only the selected step's content. Preserve assessment and decision drafts when changing steps. Completed records show their decision rather than an editable form. Contracts use Start review, Continue review, View decision and Reanalyse (Retry analysis remains available for failed attempts). No silent promotion of legacy reviews; completion is evaluated on a new explicit decision submission.


### Coverage recovery implementation clarification

Reconcile model coverage against the registered signed-source inventory. Retain validated comparison findings when coverage entries are missing, duplicated, malformed or contradictory; mark affected source checks incomplete with a plain-language reason and next action. Unassignable entries must be recorded as coverage issues and cannot establish completeness. Do not infer no-conflict or no-candidate outcomes from omitted entries. Any incomplete coverage blocks review completion. Registration counts must be labelled as registered documents rather than a claim that every source was successfully assessed.

### Decision brief approved 2026-10-11

At the top of Record decision, show a compact brief containing the review result, up to two key concerns with expandable evidence, outstanding items and a suggested next process action. Derive all text from stored findings, coverage and human assessments; do not introduce new legal conclusions or an AI signing recommendation. Keep the full review summary expandable.

After a human decision is recorded, prominently display a one-line action and rationale excerpt, with reviewer identity, timestamp and full rationale available. Use **Recorded human decision**, not CEO attribution unless the authenticated reviewer's role is known. Show the recorded line in Contracts and the brief in History; collapsed history rows include the recorded action. Clearly label outdated decisions as earlier decisions based on changed evidence. Analysis results and process suggestions must remain separate from recorded human decisions and signing authority.

### Review navigation and session exit
- Previous/Next finding changes the displayed finding and scrolls to its heading; it does not save an assessment.
- Save & next saves the current assessment and advances one finding. Saving the last finding opens Record decision, including when revisiting previously assessed findings.
- Step navigation scrolls to the selected step. Opening a contract starts at the workspace top; completed reviews open on the recorded decision.
- Assessment drafts remain available while moving between findings in the same session. Existing saved assessments populate the form when no draft exists.
- Sign out is available beside the reviewer identity on every authenticated page. It clears session state and returns to sign-in; persisted review records remain unchanged.

### Readable review references and document traceability
- Each saved analysis attempt has a permanent, unique Review ID (REV-000001 format), including existing reviews. Saving assessments or decisions retains that ID.
- Review history accepts contract names or Review IDs, including IDs belonging to earlier attempts within a contract group.
- Decision details provide View / Download access to the exact stored incoming document version reviewed. Uploaded originals are retained; supplied Markdown sources download as Markdown. Never substitute the current source for an unavailable historical version.
- Main headings omit content fingerprints. Technical details are hidden from the reviewer interface; the stored source version still links each review to its original evidence.

### Visual system and navigation presentation
- Use the document-and-check app symbol with AtliQ branding, a neutral workspace, one blue accent and consistent typography, spacing and surfaces.
- Authenticated navigation and sign-out appear in the sidebar. Review workspace is contextual and becomes available after selecting a contract.
- Contracts displays summary counts, aligned contract/status/action rows and existing upload controls. Review history retains grouping, filtering and pagination.
- Highlight the current review step. Findings can be selected directly from the sidebar, with the existing Previous/Next controls retained.
- Assessment labels use plain language while retaining the existing stored actions and backend eligibility checks.
- Present the decision brief before reviewed-document details. Preserve evidence access, original downloads, review IDs, audit history, draft retention, completion checks and source validation.

### Readable document checks
- Keep completion requirements and avoid automatically redirecting incomplete reviews into analysis or adding a separate retry control for document checks. The action-specific queue labels described below replace Continue review.
- Replace Processing coverage & gaps with Document checks. Show unfinished counts, readable agreement names, repeated reasons once per group, successfully checked documents collapsed. Raw processing details are hidden from the reviewer interface.
- Unfinished checks still prevent completion. Reviewers can use Confirm details and Analyse contract when a new analysis is needed; earlier attempts remain in history.

### Automatic recovery of omitted document checks
- After the initial whole-library analysis, reconcile the returned coverage against the registered signed documents.
- For unfinished documents with no returned comparison, automatically request follow-up checks in batches of at most four, once per document. Keep the full source library available so related definitions, schedules and waivers remain visible.
- Validate every recovered comparison against exact source passages. Preserve initial findings. A failed batch, malformed response, invalid citation or genuine evidence gap remains unfinished; never infer no-conflict from missing output.
- Retain aggregate API token usage, processing duration and automatic follow-up counts in the saved analysis. Do not require reviewers to retry each omitted document manually.
- The final finding uses Save assessment & continue to decision. Earlier findings retain Save & next.
- If a follow-up comparison omits required citations, request one correction for that group and revalidate the corrected output. Never add invented quotations or accept unsupported conclusions.

### Simplified human decision flow (current UI)
- Offer exactly three decisions: Proceed for signing approval, Do not proceed, Need more information. Require an explicit choice for a new review. Preserve existing saved decisions and map older actions to the corresponding visible choice.
- Use specific contract-queue actions: Review findings, Resolve N risks/findings, Record decision, View decision. Keep existing start, failed-analysis and stale-evidence actions.
- Show the exact outstanding findings with Open finding N buttons. Preserve the decision choice and rationale while navigating to evidence and back.
- A final choice must never silently save as follow-up. Disable final completion when requirements fail; show the work needed and allow an explicit Need more information choice instead. Backend completion rules remain authoritative.
- Need more information saves Follow-up needed with a rationale and acknowledgement. Final choices complete only when all existing checks pass. Signing remains outside the app.
