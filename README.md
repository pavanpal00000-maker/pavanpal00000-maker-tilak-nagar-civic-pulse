# Tilak Nagar Civic Pulse

A student data science project about resident satisfaction with local services in Tilak Nagar, Mumbai.

## Main features

- Top navigation: Home, Dashboard, Complaints, Track Issue, About
- Home page with an introduction and selected survey charts
- Interactive dashboard based on the raw survey CSV
- Separate complaint form with optional photo upload
- Complaint ID and status history
- Admin status updates protected by a configured password
- Survey cleaning notebooks with simple English comments

## Important note

This is an independent project portal. Complaints saved here are not automatically sent to BMC or another municipal authority.

## 1. Install Python

Use a supported Python version (Python 3.10 or newer is recommended).

## 2. Open the project folder

Open this folder in VS Code:

`tilak-nagar-civic-pulse`

## 3. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the terminal without activating and run `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## 4. Install the libraries

```powershell
python -m pip install -r requirements.txt
```

## 5. Run the website

```powershell
python -m streamlit run app.py
```

## Updating the survey later

1. Download the latest complete responses from Google Forms as CSV.
2. Save a backup of the existing `data/raw/survey_responses_raw.csv`.
3. Replace that file with the latest complete CSV export, keeping the same question headers.
4. Refresh the website. The charts read the raw CSV and update automatically.
5. Run notebook `01_data_cleaning.ipynb` when you want to refresh the saved cleaned CSV for reports.

Do not append the full export to the old file, because that can duplicate earlier responses.

## Admin setup

Before using admin status updates, create a `.streamlit` folder and a `secrets.toml` file inside it. Add the SHA-256 hash of a strong password as `ADMIN_PASSWORD_SHA256`.

Example to calculate the hash using Python:

```python
import hashlib
print(hashlib.sha256("CHOOSE-A-STRONG-PASSWORD".encode("utf-8")).hexdigest())
```

Then add this line to `.streamlit/secrets.toml`:

```toml
ADMIN_PASSWORD_SHA256 = "PASTE_THE_HASH_HERE"
```

Keep `secrets.toml` out of GitHub. For a public deployment, use a proper authentication system and persistent private storage before collecting real personal information.

## Privacy and security

- Do not commit the complaint database or uploaded photos to GitHub.
- Ask residents not to upload faces, private documents, or sensitive information.
- This prototype stores complaint photos on the server's local disk. Local files may not persist on some hosting platforms.
- The complaint form does not submit complaints to BMC.
