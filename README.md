# Flask Cloud Deployment Lab Starter

This project is a Flask web app that can be deployed to Google App Engine, Render, or Railway.

## Files

- `main.py`: Flask app entry point
- `requirements.txt`: Python dependencies
- `app.yaml`: GAE deployment config
- `Procfile`: Start command used by platforms like Railway
- `templates/index.html`: Home page template
- `submission_url.txt`: Text file for assignment submission URL

## Run locally (PowerShell)

```powershell
cd "c:\Users\Humphrey Junior\Desktop\Software engineering\year 3 sem 2\cloud computing\gae-flask-lab"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Open: http://127.0.0.1:8080

## Deploy to App Engine (PowerShell)

```powershell
# Install Google Cloud CLI first if needed
# https://cloud.google.com/sdk/docs/install

gcloud auth login
gcloud config set project <YOUR_PROJECT_ID>
gcloud app create --region=us-central
gcloud app deploy
gcloud app browse
```

After deployment, copy the URL into `submission_url.txt`.

## Deploy to Render (Recommended for quick class demo)

1. Push this folder to GitHub.
2. Go to https://render.com and sign in.
3. Click `New +` -> `Web Service` -> connect your GitHub repo.
4. Use these settings:
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
5. Click `Create Web Service` and wait for deployment.
6. Open the generated URL and copy it into `submission_url.txt`.

## Deploy to Railway

1. Push this folder to GitHub.
2. Go to https://railway.app and sign in.
3. Click `New Project` -> `Deploy from GitHub repo`.
4. Railway detects Python and installs dependencies from `requirements.txt`.
5. Ensure Start Command is `gunicorn main:app` (or use `Procfile`).
6. After deployment, open the public domain and copy the URL into `submission_url.txt`.
