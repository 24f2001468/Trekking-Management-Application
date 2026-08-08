# Technical Guide: Trekking Management Application (TMA)

## 1. Overview
The **Trekking Management Application (TMA)** is a modern, responsive web application for managing trekking activities, registrations, staff assignments, and analytics. It features a role-based architecture (Admin, Trek Staff, Trekker) powered by a Flask microframework backend and a Vue 3 single-page application (SPA) frontend.

---

## 2. Technical Stack

### Frontend
- **Framework**: Vue 3 (Options & Composition API)
- **Routing**: Vue Router 4 (HTML5 history mode)
- **Build Tool & Dev Server**: Vite v4
- **Charts & Visualization**: Chart.js with `vue-chartjs`
- **Iconography**: Bootstrap Icons (`bi-*`)
- **Styling Architecture**: Pure Vanilla CSS with a centralized Design System (`dashboard-layout.css`)
  - Modern Slate Dark Theme (`#0f172a` primary background, `#1e293b` surface dark cards)
  - High Contrast Typography (`#f8fafc` primary text, `#cbd5e1` secondary text)
  - Viewport-fitted container layouts (`calc(100vh - var(--nav-h))`) with zero unexpected page scrollbars and screen-constrained modal forms.

### Backend
- **Framework**: Python / Flask
- **Authentication**: JWT (JSON Web Tokens) with role enforcement
- **Database & ORM**: SQLite (`tma.sqlite3`) via Flask-SQLAlchemy
- **Background Tasks & Scheduling**: Celery + Redis (beat schedule for daily automated reminders)
- **Data Export**: Automated CSV export for user trekking history & admin logs

---

## 3. UI/UX & Design Guidelines

### Color Palette & Tokens
- **Background**: `#0f172a` (Slate 900)
- **Card Background**: `#1e293b` (Slate 800) / Glass overlay with 85% opacity
- **Primary Text**: `#f8fafc` (Slate 50)
- **Secondary Text**: `#cbd5e1` (Slate 300)
- **Muted Label Text**: `#94a3b8` (Slate 400)
- **Accent Emerald (Open / Ok)**: `#10b981` / Glow `rgba(16, 185, 129, 0.35)`
- **Accent Cyan (Info / Highlight)**: `#06b6d4`
- **Accent Amber (Warning / Pending)**: `#f59e0b`
- **Accent Rose (Danger / Closed)**: `#f43f5e`

### Component Behavior
- **Nav Header**: Fixed navigation bar (`height: 60px`) with blurred backdrop.
- **Admin/Staff/Trekker Dashboards**: Screen-height constrained layout shell (`height: calc(100vh - 60px)`). Sidebars and content areas scroll independently inside their viewport region.
- **Tables & Modals**: Sticky headers on data tables with maximum container height limits; modal forms enforce internal form body scrolling (`max-height: calc(100vh - 7rem)`) to guarantee action buttons stay visible on all resolutions.

---

## 4. User Roles & Capabilities

1. **Admin (`/admin`)**:
   - Manage all system treks (create, edit, delete, assign staff).
   - View user bookings, approve/reject requests, and update payment status.
   - Access real-time analytics and platform metrics.

2. **Trek Staff (`/staff`)**:
   - View assigned treks and participant rosters.
   - Update trek status (e.g. Open -> Completed).

3. **Trekker (`/trekker`)**:
   - Browse open treks, filter by difficulty/status/dates.
   - Book treks, view booking status, pay via simulator, and download CSV history.

---

## 5. Development & Build Setup

### Frontend
```bash
cd frontend
npm install
npm run dev    # Launch Vite development server
npm run build  # Compile production assets into dist/
```

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python init_db.py     # Initialize database
python app.py         # Start Flask API server on port 5000
```
