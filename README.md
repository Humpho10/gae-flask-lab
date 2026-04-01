# Flask Railway PaaS Lab Starter

This project is a Flask web app designed for Railway deployment with environment variables, a managed database, and CRUD support.

## Files

- `main.py`: Flask app entry point
- `requirements.txt`: Python dependencies
- `Procfile`: Start command used by platforms like Railway
- `.env.example`: Example environment variables
- `schema.sql`: Database schema
- `sample_data.sql`: Sample records for the database
- `railway_report.md`: Report draft for submission
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

## Deploy to Railway

1. Push this folder to GitHub.
2. Go to https://railway.app and sign in.
3. Click `New Project` -> `Deploy from GitHub repo`.
4. Railway detects Python and installs dependencies from `requirements.txt`.
5. Add a Railway PostgreSQL database to the project.
6. Set environment variables:
   - `FLASK_SECRET_KEY`
   - `DATABASE_URL` from the Railway database connection string
7. Ensure Start Command is `gunicorn main:app` (or use `Procfile`).
8. After deployment, open the public domain and copy the URL into `submission_url.txt`.

## Database files

- `schema.sql` shows the table structure.
- `sample_data.sql` provides example records.

## Report

Use `railway_report.md` as the base for your final Word or PDF submission.
