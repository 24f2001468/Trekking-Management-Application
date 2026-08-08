# 🏔️ Trekking Management Application (TMA)

A full-stack web application for managing, booking, and tracking trekking adventures. Built with **Flask** (backend) and **Vue 3** (frontend).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ with pip
- Node.js 18+
- Docker (for Redis — optional, only needed for Celery async tasks)

### 1. Clone & Setup

```bash
cd "Trekking-Management-Application"
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Configure Environment (Email)

Edit `backend/.env` and fill in your Gmail credentials to enable email features:

```env
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password (16 chars)
MAIL_DEFAULT_SENDER=your_gmail@gmail.com
```

**How to get a Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Select Mail → Windows Computer → Generate
5. Paste the 16-character password into `MAIL_PASSWORD`

> If you skip this step, the app works fully — emails simply won't be sent.

### 5. Initialize Database

```bash
cd backend
python init_db.py
```

Creates `tma.sqlite3` and seeds the default admin account:
- **Username:** `admin`
- **Password:** `admin123`

### 6. Start the Application

From the project root, run the startup script:

```powershell
.\start.ps1
```

This opens separate terminal windows for:
| Service | URL |
|---------|-----|
| Vue Frontend | http://localhost:5173 |
| Flask API | http://localhost:5000 |
| Celery Worker | (background) |
| Celery Beat | (background) |

Open **http://localhost:5173** in your browser.

---

## 👤 User Roles & Access

| Role | How to Get Access | Default Credentials |
|------|-------------------|---------------------|
| **Admin** | Created by `init_db.py` | `admin` / `admin123` |
| **Trek Staff** | Admin creates in Staff panel | Set by Admin |
| **Trekker** | Self-register at `/register` | Your own |

---

## ✉️ Email Features

Once `MAIL_USERNAME` and `MAIL_PASSWORD` are set in `backend/.env`:

| Feature | Trigger | Recipients |
|---------|---------|------------|
| **Daily Trek Reminder** | Automatic — runs at 08:00 UTC daily | Trekkers whose trek starts tomorrow |
| **Monthly Activity Report** | Automatic — runs on 1st of each month | All Admin accounts |

Reminder emails are sent to the **email address entered during registration**.

---

## 📊 Features

### Admin Dashboard
- Full trek lifecycle management (create, edit, assign staff, delete)
- User management with **Deactivate** (reversible) and **Blacklist** (permanent ban)
- Staff account management
- Booking and payment status management
- Analytics: 6 Chart.js charts (monthly trends, top treks, difficulty/status distributions)
- Download monthly HTML activity report
- Advanced trek search and filtering

### Trek Staff Dashboard
- View assigned treks and participant lists
- Update trek status and available slots
- Mark participant bookings as Completed/Cancelled

### Trekker Dashboard
- Browse and book open treks (with slot availability)
- Payment simulation (card entry → processing → success/fail)
- Cancel active bookings
- View full trek history with filters
- Export booking history as CSV
- Update profile (username, email, password)

---

## 💳 Payment Simulation

After booking a trek, a **Pay Now** button appears for pending payments.

- Enter any valid card number → payment succeeds → status updates to **Paid**
- Card ending in **0002** → simulated decline → status stays Pending
- Payment status updates instantly in the UI and is saved to the database

---

## 🗄️ Project Structure

```
Trekking-Management-Application/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── models/
│   │   ├── database.py     # SQLAlchemy instance
│   │   └── models.py       # User, StaffProfile, Trek, Booking
│   ├── routes/
│   │   ├── auth.py         # Register, Login, Profile
│   │   ├── admin.py        # Admin endpoints + monthly report
│   │   ├── staff.py        # Staff endpoints
│   │   ├── trekker.py      # Trekker endpoints + CSV export
│   │   ├── payments.py     # Payment & booking status updates
│   │   ├── search.py       # Trek search & filtering
│   │   └── analytics.py    # Public + admin analytics
│   ├── scheduler.py        # APScheduler jobs (reminders + reports)
│   ├── tasks.py            # CSV export + Celery tasks
│   ├── mail.py             # Flask-Mail instance
│   ├── cache.py            # Flask-Caching instance
│   ├── celery_app.py       # Celery configuration
│   ├── celery_worker.py    # Celery Beat schedule
│   ├── init_db.py          # DB initializer
│   ├── requirements.txt
│   └── .env                # Environment variables (mail config)
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/index.js
│   │   ├── assets/dashboard-layout.css   # Shared design system
│   │   ├── composables/
│   │   │   ├── useToast.js
│   │   │   ├── useConfirm.js
│   │   │   └── useChartDefaults.js
│   │   ├── components/
│   │   │   ├── admin/      # AdminHome, Treks, Users, Staff, Bookings, Analytics
│   │   │   ├── staff/      # StaffHome, Treks, TrekDetails
│   │   │   └── trekker/    # TrekkerHome, Browse, Bookings, History, Profile
│   │   └── views/          # Dashboard layouts + Auth views + Landing
│   └── package.json
├── api.yaml                # OpenAPI 3.0 specification
├── start.ps1               # One-command startup script
└── .gitignore
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Flask 3.0 | Backend REST API |
| SQLAlchemy | ORM for SQLite |
| Flask-JWT-Extended | JWT authentication |
| Flask-Mail | Email delivery |
| APScheduler | Scheduled jobs (no Redis needed) |
| Flask-Caching | Response caching |
| Celery + Redis | Async task queue (optional) |
| Vue 3 | Frontend SPA |
| Vue Router | Client-side routing with RBAC guards |
| Chart.js + vue-chartjs | Analytics charts |
| Vite | Build tool with dev proxy |
| Bootstrap Icons | Icon library |
| Inter (Google Fonts) | UI typeface |

---

## 🔒 Security Notes

- Passwords are hashed with Werkzeug PBKDF2
- JWT tokens expire after 24 hours
- Blacklisted users cannot log in even if `active=True`
- All protected routes validate JWT role claims server-side
- Never commit `.env` to version control — it's in `.gitignore`
