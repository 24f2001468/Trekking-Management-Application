"""
APScheduler-based background jobs replacing Celery for scheduled tasks.
Jobs:
  1. send_daily_reminders  — runs daily at 08:00 UTC
  2. generate_monthly_report — runs on 1st of every month at 00:05 UTC
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)
_scheduler = None


# ─────────────────────────────────────────────────────────
#  Email helpers
# ─────────────────────────────────────────────────────────

def _send_email(app, subject, recipients, html_body):
    """Send an HTML email using Flask-Mail inside app context."""
    from flask_mail import Message
    from mail import mail
    with app.app_context():
        try:
            msg = Message(subject=subject, recipients=recipients, html=html_body)
            mail.send(msg)
            logger.info("Email sent to %s — %s", recipients, subject)
            return True
        except Exception as e:
            logger.error("Email send failed: %s", e)
            return False


# ─────────────────────────────────────────────────────────
#  Job 1 – Daily Reminders
# ─────────────────────────────────────────────────────────

def send_daily_reminders(app):
    """Send reminder emails to trekkers whose trek starts tomorrow."""
    from datetime import datetime, timedelta
    from models.database import db
    from models.models import Trek, Booking

    with app.app_context():
        tomorrow = (datetime.utcnow() + timedelta(days=1)).date()
        upcoming = Trek.query.filter_by(start_date=tomorrow).all()
        sent = 0

        for trek in upcoming:
            bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
            for booking in bookings:
                user = booking.user
                if not user or not user.email:
                    continue

                html = f"""
                <html><body style="font-family:Arial,sans-serif;background:#0b1612;color:#e8f0ea;padding:2rem;">
                <div style="max-width:560px;margin:auto;background:#12201a;border-radius:12px;padding:2rem;border:1px solid rgba(61,139,101,0.2);">
                  <h2 style="color:#6dbf95;">🏔️ Trek Reminder — TMA</h2>
                  <p>Hi <strong>{user.username}</strong>,</p>
                  <p>This is a reminder that your trek <strong>{trek.name}</strong> starts <strong>tomorrow ({trek.start_date})</strong>.</p>
                  <table style="width:100%;border-collapse:collapse;margin:1rem 0;">
                    <tr><td style="padding:.5rem;color:#7fa88c;">Location</td><td style="padding:.5rem;">{trek.location}</td></tr>
                    <tr><td style="padding:.5rem;color:#7fa88c;">Difficulty</td><td style="padding:.5rem;">{trek.difficulty}</td></tr>
                    <tr><td style="padding:.5rem;color:#7fa88c;">Duration</td><td style="padding:.5rem;">{trek.duration} day(s)</td></tr>
                    <tr><td style="padding:.5rem;color:#7fa88c;">Start Date</td><td style="padding:.5rem;">{trek.start_date}</td></tr>
                    <tr><td style="padding:.5rem;color:#7fa88c;">End Date</td><td style="padding:.5rem;">{trek.end_date}</td></tr>
                  </table>
                  <p style="color:#7fa88c;">Please arrive on time and carry all required gear. Have a great trek!</p>
                  <hr style="border-color:rgba(61,139,101,0.2);">
                  <p style="font-size:.8rem;color:#4d6b58;">Trekking Management Application &mdash; Automated Reminder</p>
                </div></body></html>
                """
                if _send_email(app, f"Reminder: Your trek '{trek.name}' starts tomorrow!", [user.email], html):
                    sent += 1
                logger.info("[REMINDER] %s → %s", user.email, trek.name)

        logger.info("Daily reminders: sent %d emails for %d treks.", sent, len(upcoming))


# ─────────────────────────────────────────────────────────
#  Job 2 – Monthly Activity Report
# ─────────────────────────────────────────────────────────

def generate_monthly_report(app):
    """Generate HTML monthly report and email it to all Admins."""
    from datetime import datetime, timedelta
    from models.database import db
    from models.models import Trek, Booking, User
    from sqlalchemy import func

    with app.app_context():
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)

        # Stats
        recent_treks = Trek.query.filter(Trek.start_date >= thirty_days_ago).all()
        total_bookings = Booking.query.filter(
            Booking.booking_date >= thirty_days_ago,
            Booking.status != 'Cancelled'
        ).count()
        unique_participants = db.session.query(func.count(func.distinct(Booking.user_id))).filter(
            Booking.booking_date >= thirty_days_ago,
            Booking.status != 'Cancelled'
        ).scalar()

        # Top 5 treks by booking count
        top_treks_rows = (
            db.session.query(Trek.name, Trek.location, func.count(Booking.id).label('cnt'))
            .join(Booking, Booking.trek_id == Trek.id)
            .filter(Booking.booking_date >= thirty_days_ago, Booking.status != 'Cancelled')
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .limit(5).all()
        )

        top_rows_html = ''.join(
            f"<tr><td style='padding:.5rem .75rem'>{r[0]}</td><td style='padding:.5rem .75rem'>{r[1]}</td>"
            f"<td style='padding:.5rem .75rem;text-align:center'>{r[2]}</td></tr>"
            for r in top_treks_rows
        ) or "<tr><td colspan='3' style='padding:.5rem;color:#7fa88c'>No data</td></tr>"

        trek_rows_html = ''.join(
            f"<tr><td style='padding:.4rem .75rem'>{t.name}</td><td style='padding:.4rem .75rem'>{t.location}</td>"
            f"<td style='padding:.4rem .75rem'>{t.status}</td><td style='padding:.4rem .75rem'>{t.start_date}</td></tr>"
            for t in recent_treks
        ) or "<tr><td colspan='4' style='padding:.5rem;color:#7fa88c'>No treks this period</td></tr>"

        html = f"""
        <html><body style="font-family:Arial,sans-serif;background:#0b1612;color:#e8f0ea;padding:2rem;margin:0;">
        <div style="max-width:680px;margin:auto;background:#12201a;border-radius:14px;padding:2.5rem;border:1px solid rgba(61,139,101,0.2);">
          <h1 style="color:#6dbf95;margin-top:0;">📊 Monthly Activity Report</h1>
          <p style="color:#7fa88c;">Period: <strong>{thirty_days_ago.strftime('%d %b %Y')}</strong> — <strong>{now.strftime('%d %b %Y')}</strong></p>

          <div style="display:flex;gap:1rem;margin:1.5rem 0;flex-wrap:wrap;">
            <div style="flex:1;min-width:140px;background:rgba(61,139,101,0.12);border-radius:10px;padding:1rem;text-align:center;">
              <div style="font-size:2rem;font-weight:800;color:#6dbf95;">{len(recent_treks)}</div>
              <div style="font-size:.8rem;color:#7fa88c;text-transform:uppercase;letter-spacing:.06em;">Treks Conducted</div>
            </div>
            <div style="flex:1;min-width:140px;background:rgba(63,143,160,0.12);border-radius:10px;padding:1rem;text-align:center;">
              <div style="font-size:2rem;font-weight:800;color:#7ec9d8;">{unique_participants}</div>
              <div style="font-size:.8rem;color:#7fa88c;text-transform:uppercase;letter-spacing:.06em;">Unique Participants</div>
            </div>
            <div style="flex:1;min-width:140px;background:rgba(212,146,74,0.12);border-radius:10px;padding:1rem;text-align:center;">
              <div style="font-size:2rem;font-weight:800;color:#e8ae72;">{total_bookings}</div>
              <div style="font-size:.8rem;color:#7fa88c;text-transform:uppercase;letter-spacing:.06em;">Total Bookings</div>
            </div>
          </div>

          <h3 style="color:#6dbf95;border-bottom:1px solid rgba(61,139,101,0.2);padding-bottom:.5rem;">🏆 Most Popular Treks</h3>
          <table style="width:100%;border-collapse:collapse;">
            <thead><tr style="background:rgba(0,0,0,0.3);">
              <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Trek</th>
              <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Location</th>
              <th style="padding:.5rem .75rem;text-align:center;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Bookings</th>
            </tr></thead>
            <tbody>{top_rows_html}</tbody>
          </table>

          <h3 style="color:#6dbf95;border-bottom:1px solid rgba(61,139,101,0.2);padding-bottom:.5rem;margin-top:1.5rem;">📋 All Treks This Period</h3>
          <table style="width:100%;border-collapse:collapse;">
            <thead><tr style="background:rgba(0,0,0,0.3);">
              <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Name</th>
              <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Location</th>
              <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Status</th>
              <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Start</th>
            </tr></thead>
            <tbody>{trek_rows_html}</tbody>
          </table>

          <hr style="border-color:rgba(61,139,101,0.15);margin:2rem 0 1rem;">
          <p style="font-size:.78rem;color:#4d6b58;">Generated automatically on {now.strftime('%d %b %Y %H:%M UTC')} &mdash; Trekking Management Application</p>
        </div></body></html>
        """

        # Send to all Admin users
        admins = User.query.filter_by(role='Admin', active=True).all()
        for admin in admins:
            if admin.email:
                _send_email(app, f"TMA Monthly Report — {now.strftime('%B %Y')}", [admin.email], html)
                logger.info("[MONTHLY REPORT] Sent to %s", admin.email)

        logger.info("Monthly report generated: %d treks, %d participants.", len(recent_treks), unique_participants)


# ─────────────────────────────────────────────────────────
#  Scheduler lifecycle
# ─────────────────────────────────────────────────────────

def init_scheduler(app):
    """Initialize and start the APScheduler background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone='UTC')

    # Daily at 08:00 UTC
    _scheduler.add_job(
        func=send_daily_reminders,
        args=[app],
        trigger=CronTrigger(hour=8, minute=0),
        id='daily_reminders',
        replace_existing=True
    )

    # 1st of every month at 00:05 UTC
    _scheduler.add_job(
        func=generate_monthly_report,
        args=[app],
        trigger=CronTrigger(day=1, hour=0, minute=5),
        id='monthly_report',
        replace_existing=True
    )

    _scheduler.start()
    logger.info("APScheduler started — daily reminders + monthly report jobs registered.")
    return _scheduler
