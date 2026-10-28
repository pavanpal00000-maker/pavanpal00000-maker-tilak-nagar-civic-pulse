# 🏙️ Tilak Nagar Civic Pulse

> **Citizen Satisfaction Analytics for Local Governance**  
> A T.Y.B.Sc. Data Science Project — Semester V  
> N. G. Acharya & D. K. Marathe College of Arts, Science & Commerce, Chembur, Mumbai

---

## 📌 Project Overview

**Tilak Nagar Civic Pulse** is a full-stack data science web application that measures and visualizes citizen satisfaction with local civic services in the Tilak Nagar area of Mumbai.

The platform has two sides:
- **Resident-facing portal** — Submit complaints with photo evidence, track complaint status in real time, and view survey-driven insights about local service quality.
- **Admin dashboard** — Manage and update complaint statuses, view analytics, and monitor trends across departments.

Survey data was collected from **52 residents** (50 valid consented responses) across Tilak Nagar, Chembur, and surrounding localities. Key findings show that **Public Toilets (3.22/5)** and **Roads (3.64/5)** are the lowest-rated civic services, while **Water Supply (4.02/5)** is the highest-rated.

---

## 👨‍🎓 Student Details

| Field | Details |
|---|---|
| **Name** | Pavan Suresh Pal |
| **Roll No.** | 27 |
| **Class** | T.Y.B.Sc. Data Science, Semester V |
| **College** | N. G. Acharya & D. K. Marathe College |
| **Project Guide** | Ms. Kohinoor Khan |
| **Email** | pavanpal00000@gmail.com |

---

## ✨ Features

### 🏠 Resident Portal
- **Home Page** — Introduction, project overview, and key survey highlights
- **Interactive Dashboard** — Live charts and graphs from survey data (ratings by service, age group, locality)
- **Complaint Form** — Submit civic complaints with category, location, description, and optional photo
- **Track Issue** — Enter Complaint ID to view full status history
- **About Page** — Project background and data methodology

### 🔐 Admin Panel
- Secure login protected by SHA-256 hashed password
- View all submitted complaints with filters
- Update complaint status (Submitted → In Progress → Resolved)
- Add internal notes on each status change
- Full history log per complaint

### 📊 Data Science Components
- Survey data cleaning and preprocessing (Jupyter Notebooks)
- Statistical analysis of service ratings
- Visualizations: bar charts, pie charts, correlation heatmaps
- Locality-wise and age-group-wise breakdowns

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / UI** | Streamlit |
| **Backend / Logic** | Python 3.10+ |
| **Database** | SQLite (`complaints.db`) |
| **Data Analysis** | Pandas, NumPy |
| **Visualizations** | Matplotlib, Seaborn, Plotly |
| **Survey Data** | Google Forms → CSV |
| **Version Control** | Git + GitHub |

---

## 📁 Project Structure

```
work_civic/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── .streamlit/
│   └── secrets.toml                # 🔒 Admin password hash (NOT in GitHub)
│
├── data/
│   ├── raw/
│   │   └── survey_responses_raw.csv    # Original survey export (52 responses)
│   └── processed/
│       └── responses_clean.csv         # Cleaned data (50 valid responses)
│
├── database/
│   └── db.py                       # SQLite DB setup and query functions
│
├── utils/
│   ├── complaint_tracker.py        # Complaint ID generation & tracking logic
│   ├── data_cleaning.py            # Survey data cleaning utilities
│   ├── department_mapping.py       # Category → Department mapping
│   └── image_handler.py            # Photo upload handling
│
├── complaints/
│   └── uploads/                    # 🔒 Uploaded complaint photos (NOT in GitHub)
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb      # Survey data preprocessing
│   ├── 02_eda.ipynb                # Exploratory Data Analysis
│   ├── 03_visualizations.ipynb     # Chart generation
│   └── 04_insights.ipynb           # Key findings & conclusions
│
└── tests/
    └── test_ui_helpers.py          # Unit tests (11 tests, all passing)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or newer
- Git

### 1. Clone the Repository

```powershell
git clone https://github.com/pavanpal00000-maker/pavanpal00000-maker-tilak-nagar-civic-pulse.git
cd pavanpal00000-maker-tilak-nagar-civic-pulse
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> ⚠️ If PowerShell blocks activation, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Set Up Admin Password

Create the `.streamlit` folder and `secrets.toml` file:

```powershell
mkdir .streamlit
```

Generate your password hash in Python:

```python
import hashlib
password = "YOUR-STRONG-PASSWORD"
print(hashlib.sha256(password.encode("utf-8")).hexdigest())
```

Create `.streamlit/secrets.toml`:

```toml
ADMIN_PASSWORD_SHA256 = "PASTE_YOUR_HASH_HERE"
```

> 🔒 **Never commit `secrets.toml` to GitHub.** It is already listed in `.gitignore`.

### 5. Run the Application

```powershell
python -m streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## 📊 Survey Key Findings

Based on **50 valid survey responses** collected from Tilak Nagar and surrounding areas:

| Civic Service | Avg. Rating (out of 5) |
|---|---|
| 💧 Water Supply | 4.02 ⭐ *(Highest)* |
| 🧹 Cleanliness | 4.00 |
| 💡 Street Lighting | 3.90 |
| 🌧️ Drainage | 3.87 |
| 🛣️ Roads | 3.64 |
| 🗑️ Garbage Collection | 3.62 |
| 💻 Online Services | 3.35 |
| 🚽 Public Toilets | 3.22 ⚠️ *(Lowest)* |
| **Overall Governance** | **3.66 / 5.0** |

**Other findings:**
- 84% of respondents are from Tilak Nagar
- 64% of respondents are aged 18–30
- **74% have never reported a complaint** to any authority

---

## 🔒 Privacy & Security

- `complaints.db` (SQLite database) is **excluded from GitHub** via `.gitignore`
- `secrets.toml` (admin password) is **excluded from GitHub**
- Uploaded complaint photos are **excluded from GitHub**
- This is a **prototype** — complaints submitted here are **not** forwarded to BMC or any municipal authority
- Do not upload faces, Aadhaar cards, or any sensitive personal documents via the complaint photo form

---

## 🧪 Running Tests

```powershell
python -m pytest tests/ -v
```

All 11 unit tests should pass.

---

## 📖 Updating Survey Data

1. Export latest responses from Google Forms as `.csv`
2. Backup existing `data/raw/survey_responses_raw.csv`
3. Replace it with the new export (keep same column headers)
4. Refresh the app — charts update automatically
5. Run `notebooks/01_data_cleaning.ipynb` to refresh the cleaned CSV

> ⚠️ Do **not** append new exports to the old file — this will duplicate responses.

---

## 📝 License

This project is developed for academic purposes as part of the T.Y.B.Sc. Data Science curriculum at N. G. Acharya & D. K. Marathe College, Chembur, Mumbai. Not intended for commercial use.

---

<p align="center">Made with ❤️ by <strong>Pavan Suresh Pal</strong> | Roll No. 27 | T.Y.B.Sc. Data Science, Sem V</p>
