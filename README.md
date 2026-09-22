# AI Resume Analyzer & ATS Compatibility Predictor

A web-based AI-powered application designed for students and job seekers to evaluate, analyze, and optimize resumes for Applicant Tracking Systems (ATS) and recruiter screening.

Developed using **Python, Django, MySQL (with SQLite auto-fallback), NLTK, SpaCy, Scikit-learn, PyPDF2, python-docx, Bootstrap 5, and Chart.js**.

---

## 🌟 Key Features

1. **User Authentication & Profiles**:
   - Secure Registration, Login, and Profile Management for **Job Seekers / Students** and **Administrators**.
   - Profile-level target career preferences, experience level, and uploaded resumes tracking.

2. **Multi-Format Resume Parsing**:
   - Accepts **PDF (`.pdf`)** and **Word (`.docx`)** formats.
   - Extracts candidate contact information (Name, Email, Phone, LinkedIn, GitHub, Portfolio).
   - Segments standard sections: Summary, Work Experience, Education, Skills, Projects, Certifications.

3. **Multi-Factor ATS Compatibility Scoring Engine (0 - 100%)**:
   - **Keyword Matching (30%)**: TF-IDF Cosine similarity between resume text and job requirements.
   - **Skills Coverage (25%)**: Ratio of core required skills vs. preferred skills.
   - **Experience & Impact (15%)**: Action verbs density and quantified achievements ($ / % / metrics).
   - **Education & Credentials (10%)**: Degree level and relevant domain alignment.
   - **Section Completeness (10%)**: Verification of key structural sections.
   - **Formatting & Readability (10%)**: Page length (1-2 pages optimal), structure, and parseability.

4. **Skill Gap Analysis**:
   - Compares candidate skills against **20+ pre-calibrated tech job roles** or **custom pasted Job Descriptions (JD)**.
   - **Matched Skills**: Visualized in green pills.
   - **Missing Critical Skills**: Highlighted in red with warning notices.
   - **Recommended / Trending Skills**: Blue pills for competitive edge.

5. **AI-Driven Actionable Recommendations**:
   - Actionable phrasing suggestions utilizing the **Google XYZ formula** (*"Accomplished [X] as measured by [Y], by doing [Z]"*).
   - Curated portfolio project suggestions to bridge missing skills.
   - Recommended industry certifications (AWS, Azure, GCP, PCEP, etc.).

6. **Interactive Visual Reports & PDF Export**:
   - Circular animated ATS score gauge with dynamic rating badges.
   - Chart.js Radar Chart for criteria sub-scores and Doughnut Chart for skill distribution.
   - One-click **Print / Download PDF Report**.
   - Resume Iteration Comparison to track before-and-after improvements.

7. **Comprehensive Admin Portal & Analytics**:
   - Platform metrics: Total Users, Total Scans, Platform Average ATS Score, High Match Rate.
   - Curriculum gap analytics: Top missing skills across all applicants.
   - Full CRUD management for **Job Roles** and **Skills Taxonomy**.
   - Audit logs repository with **CSV Export**.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Django (MTV Architecture), Django ORM |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons, Chart.js |
| **Database** | MySQL (Default / Configurable) with automatic SQLite fallback |
| **NLP & AI** | PyPDF2, python-docx, NLTK, SpaCy, Scikit-learn (TF-IDF, Cosine Similarity) |
| **Styling** | Custom CSS3 with glassmorphism, responsive grids, dark/light accents |

---

## 📁 Project Directory Structure

```
trai_pro/
├── manage.py
├── requirements.txt
├── README.md
├── verify_system.py
├── create_sample_resumes.py
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── signals.py
├── analyzer/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── nlp/
│   │   ├── text_extractor.py
│   │   ├── resume_parser.py
│   │   └── skill_extractor.py
│   ├── scoring/
│   │   ├── ats_calculator.py
│   │   └── skill_gap.py
│   ├── recommender/
│   │   └── suggestions.py
│   └── management/commands/
│       └── seed_data.py
├── admin_dashboard/
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── templates/
│   ├── base.html
│   ├── navbar.html
│   ├── footer.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── analyzer/
│   │   ├── index.html
│   │   ├── upload.html
│   │   ├── report.html
│   │   ├── report_pdf.html
│   │   ├── history.html
│   │   └── compare.html
│   └── admin_dashboard/
│       ├── dashboard.html
│       ├── manage_users.html
│       ├── manage_roles.html
│       ├── role_form.html
│       ├── manage_skills.html
│       └── resume_logs.html
└── static/
    ├── css/
    │   ├── style.css
    │   └── report.css
    └── js/
        ├── main.js
        └── report_charts.js
```

---

## 🚀 Quick Setup & Installation

### 1. Clone or Open the Project
```bash
cd c:\Users\vignan\Desktop\f23\trai_pro
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration (MySQL / SQLite)
- **SQLite (Default / Zero Config)**: Works immediately out of the box.
- **MySQL (Optional)**: If you wish to use MySQL, set environment variables or update `core/settings.py`:
  ```bash
  # Windows PowerShell
  $env:USE_MYSQL="True"
  $env:DB_NAME="ai_resume_db"
  $env:DB_USER="root"
  $env:DB_PASSWORD="your_password"
  $env:DB_HOST="localhost"
  $env:DB_PORT="3306"
  ```

### 4. Run Automated Setup & Verification
Run the all-in-one verification script to apply migrations, seed the taxonomy database (250+ skills & 10+ roles), create demo users, and test the full NLP pipeline:
```bash
python verify_system.py
```

Or execute standard Django commands manually:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

### 5. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Default Credentials

| Role | Username | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Full Admin Portal (`/admin-panel/`) & Django Admin (`/admin/`) |
| **Demo Job Seeker** | `demo_user` | `demo123` | Resume Upload, Audit Reports, History, Comparison |

---

## 🧪 Testing & Verification

1. **Upload Test**:
   - Sign in as `demo_user`.
   - Click **Analyze Resume**.
   - Upload any sample PDF or DOCX file (e.g. generate via `python create_sample_resumes.py`).
   - Select target role **Full Stack Developer** or paste a custom Job Description.
   - Click **Run AI Resume Evaluation**.
2. **Review Interactive Report**:
   - Inspect the ATS score meter, radar chart, skill gap pills (Matched, Missing, Recommended), and action items.
   - Click **Print / Export PDF** to test PDF report generation.
3. **Admin Verification**:
   - Sign in as `admin`.
   - Navigate to **Admin Portal** from top navigation.
   - Review platform-wide score distribution, curriculum gaps, and download CSV export.
