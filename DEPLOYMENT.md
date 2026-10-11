# Deploy the capstone demo

Use **Streamlit Community Cloud**: https://share.streamlit.io/

## 1. Put the source on GitHub

Create a GitHub repository and upload `app.py`, `src/`, `Dataset/`,
`requirements.txt`, `.streamlit/config.toml`, and the README. You can also
include the tests, PRD, deployment guide and synthetic test contracts.

**Do not upload** `.env`, `.venv/`, `storage/`, database backups,
`__pycache__/`, or `.streamlit/secrets.toml`. The supplied `.gitignore`
excludes these when using Git; browser uploads require checking manually.
Your local reviewer and history are not transferred.

## 2. Create the cloud app

1. Sign in to Streamlit Community Cloud with GitHub.
2. Click **Create app** and choose your repository and branch.
3. Set the main file path to **app.py**.
4. Open **Advanced settings**. Choose Python **3.14** if offered; otherwise
   use **3.13** and verify the app after deployment.
5. Copy `.streamlit/secrets.example.toml` into the **Secrets** box.
6. Replace all placeholders with your OpenAI API key, reviewer identity
   and a unique reviewer password of at least 12 characters.
7. Click **Deploy**. Share the resulting `https://...streamlit.app` URL.

Top-level Streamlit secrets are exposed as environment variables, which
this app already reads. No `.env` upload or shell commands are needed.
Do not send passwords or API keys in chat or put them in your repository.

## 3. Check the deployed app

Sign in using the identity and password from Secrets. Upload a synthetic
DOCX or PDF, check extracted text, run analysis, assess findings and record
a decision. Confirm the result appears in Review history, then sign out
and sign in again. Test both a completed decision and Need more information.

## Demo limitations

Hosting is free within Community Cloud limits; OpenAI API usage is billed
separately. This deployment uses local SQLite: history and uploaded files
can disappear after a restart, redeploy or platform cleanup. The reviewer
account is recreated from Secrets if the database is reset. Download any
results needed for your submission before restarting the app.

This is a synthetic capstone demonstration, not durable contract storage.
For permanent history, migrate the database and uploaded files to external
storage before using real contracts. Changing reviewer Secrets does not
replace an account already in an existing database.

Official deployment instructions:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
