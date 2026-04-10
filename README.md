# ElevaTech — Smart Elevator Maintenance & Service Tracking System

A complete, production-ready Django web application for elevator companies to manage installations, technicians, fault reports, and maintenance schedules.

---

## 🚀 Features

- **Public Website** — Home, About, Services, Contact pages (no login required)
- **Elevator Management** — Track all elevators by location, type, status
- **Technician Management** — Manage team skills (Wiring / Sensors / PCB)
- **Fault Reporting** — Report sensor, door, motor, PCB issues with photo upload
- **Maintenance Scheduler** — Monthly, quarterly, annual scheduling with overdue alerts
- **Service History** — Auto-logged history when faults are resolved or maintenance completed
- **Dashboard** — Charts (Chart.js), stat cards, recent activity tables
- **AI Suggestions** — Detects repeat faults and recommends part replacement
- **Hidden Admin Panel** — Accessible only via `/secret-admin-panel/`

---

## 🛠️ Local Setup

### Requirements
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone or extract the project
cd elevator_project

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py makemigrations main
python manage.py migrate

# 5. Create admin superuser
python manage.py createsuperuser

# 6. (Optional) Load sample data
python manage.py shell < seed_data.py

# 7. Start the development server
python manage.py runserver
```

Open http://127.0.0.1:8000/ — the homepage loads first (not login).

---

## 🌐 Deploy to Render

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial ElevaTech project"
git remote add origin https://github.com/YOUR_USERNAME/elevatech.git
git push -u origin main
```

### Step 2 — Create Web Service on Render
1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repository
3. Set the following:

| Setting | Value |
|---|---|
| Environment | Python |
| Build Command | `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput` |
| Start Command | `gunicorn elevator_system.wsgi` |

4. Add Environment Variables:

| Key | Value |
|---|---|
| `SECRET_KEY` | Generate a 64-character random string |
| `DEBUG` | `False` |

5. Click **Create Web Service** — Render will deploy automatically.

### Step 3 — Create Superuser (via Render Shell)
- Go to your service → **Shell** tab
- Run: `python manage.py createsuperuser`

### Step 4 — Access Admin
- Admin URL: `https://your-app.onrender.com/secret-admin-panel/`
- This URL is **not visible** in any navigation menu

---

## 📁 Project Structure

```
elevator_project/
├── manage.py
├── requirements.txt
├── render.yaml
├── elevator_system/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── main/
│       ├── models.py       # Elevator, Technician, FaultReport, Maintenance, ServiceHistory
│       ├── views.py        # All view logic
│       ├── urls.py         # 25 URL routes
│       └── admin.py        # Django admin registration
├── templates/              # 21 HTML templates
│   ├── base.html
│   ├── sidebar.html
│   ├── index.html          # Public homepage
│   ├── about.html
│   ├── services.html
│   ├── contact.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html      # Charts + stats
│   ├── elevators.html
│   ├── elevator_form.html
│   ├── elevator_detail.html
│   ├── technicians.html
│   ├── technician_form.html
│   ├── faults.html
│   ├── fault_form.html
│   ├── fault_update.html
│   ├── maintenance.html
│   ├── maintenance_form.html
│   ├── complete_maintenance.html
│   └── service_history.html
└── static/
    └── css/
        └── style.css       # 437-line responsive stylesheet
```

---

## 🔐 Security Notes

- Admin panel URL is `/secret-admin-panel/` — not exposed in any navigation
- All protected pages require login (`@login_required`)
- CSRF protection on all forms
- Password hashing via Django's built-in auth system
- File uploads validated and stored under `/media/`
- `SECRET_KEY` and `DEBUG=False` set via environment variables on Render

---

## 🎨 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 |
| Database | SQLite (dev) |
| Frontend | HTML5, CSS3, Vanilla JS |
| Charts | Chart.js 4.4 |
| Static Files | WhiteNoise |
| Deployment | Render + Gunicorn |
| Image Handling | Pillow |

---

## 📞 Support

ElevaTech — support@elevatech.com
