# AtliQ Contract Risk Analyzer

**Contract Obligation & Conflict Review** — a local app that compares incoming contracts with signed agreements, shows supporting evidence, and records a human review decision.

## 1. Set up

Open a terminal in the project folder. Python **3.14** is the tested version.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
cp -n .env.example .env
```

The copy command keeps an existing `.env` file unchanged. Edit `.env` and set:

```dotenv
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4.1
LLM_API_KEY=your_openai_api_key
```

Use a model enabled for your API account. Analysis uses API credits; keep your key private. Leave the other settings at their defaults unless needed.

## 2. Start the app

Run these commands from the project folder each time you start it:

```bash
source .venv/bin/activate
set -a
source .env
set +a
streamlit run app.py
```

Open **http://127.0.0.1:8501/**. On first use, create a reviewer identity and a password of at least **12 characters**. There is no default login. For later visits, use that same account.

To stop the app, press **Ctrl+C** in the terminal. Restart it after changing `.env`.

## 3. Review a contract

1. **Contracts:** select a supplied draft or expand **Upload a new contract**. Upload PDF, DOCX, Markdown or text, up to **2 MB**. Check the extracted text before saving. Scanned PDFs require OCR first; legacy `.doc` files are unsupported.
2. **Confirm details:** check the entity, services, locations and review date. Tick the confirmation and click **Analyse contract**.
3. **Review findings:** inspect each finding and its evidence, select your assessment, enter a reason, and save. Accept a supported risk only if authorised.
4. **Make your decision:** choose one of the following:

| Choice | Result |
|---|---|
| **Proceed for signing approval** | Completes eligible reviews and refers the decision to the authorised signatory. |
| **Do not proceed** | Completes eligible reviews with a decision to stop this draft. |
| **Need more information** | Saves follow-up and keeps the review open. Explain what is needed. |

Enter your decision reason, tick the acknowledgement, and save. If completion is blocked, use **Open finding N** to resolve the indicated item. Missing evidence and unfinished document checks cannot be bypassed.

## 4. Find saved results

**Review history** contains saved findings, assessments and decisions. Search by contract name or **Review ID**, expand the entry, and view or download the exact reviewed contract. Completed reviews show **View decision** in Contracts.

Use **Sign out** in the sidebar when finished. Contracts and saved reviews remain stored locally in `storage/`; signing out does not delete them. A new analysis creates a separate review attempt.

## Checks and limitations

For a free hosted capstone demo, follow [DEPLOYMENT.md](DEPLOYMENT.md).

```bash
.venv/bin/python -m unittest discover -s tests -v
```

This capstone uses synthetic data and local authentication. Verify extracted text and model conclusions against the originals. Completing a review **does not sign a contract**. See [PRD.md](PRD.md) for detailed requirements.
