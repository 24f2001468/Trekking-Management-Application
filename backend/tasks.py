from celery_app import celery_instance
from models.database import db
from models.models import Trek, Booking, User
from datetime import datetime, timedelta
from sqlalchemy import func
import csv
import io
import logging

logger = logging.getLogger(__name__)


def _send_mail(subject, recipients, html_body):
    """Send email using Flask-Mail within app context."""
    try:
        from mail import mail
        from flask_mail import Message
        msg = Message(subject=subject, recipients=recipients, html=html_body)
        mail.send(msg)
        logger.info("Email sent to %s: %s", recipients, subject)
        return True
    except Exception as e:
        logger.warning("Email send failed (check .env MAIL_USERNAME/PASSWORD): %s", e)
        return False


@celery_instance.task
def send_daily_reminders():
    """
    Scheduled Job: Runs daily at 08:00 UTC.
    Sends reminder emails to trekkers whose trek starts tomorrow.
    """
    tomorrow = (datetime.utcnow() + timedelta(days=1)).date()
    upcoming_treks = Trek.query.filter_by(start_date=tomorrow).all()
    sent = 0

    for trek in upcoming_treks:
        bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
        for booking in bookings:
            user = booking.user
            if not user or not user.email:
                continue

            html = f"""
            <html><body style="font-family:Arial,sans-serif;background:#0f172a;color:#f8fafc;padding:2rem;">
            <div style="max-width:560px;margin:auto;background:#1e293b;border-radius:12px;padding:2rem;border:1px solid rgba(255,255,255,0.1);">
              <h2 style="color:#34d399;">&#127956; Trek Reminder — TMA</h2>
              <p>Hi <strong>{user.username}</strong>,</p>
              <p>This is a reminder that your trek <strong>{trek.name}</strong> starts <strong>tomorrow ({trek.start_date})</strong>.</p>
              <table style="width:100%;border-collapse:collapse;margin:1rem 0;">
                <tr><td style="padding:.5rem;color:#94a3b8;">Location</td><td style="padding:.5rem;">{trek.location}</td></tr>
                <tr><td style="padding:.5rem;color:#94a3b8;">Difficulty</td><td style="padding:.5rem;">{trek.difficulty}</td></tr>
                <tr><td style="padding:.5rem;color:#94a3b8;">Duration</td><td style="padding:.5rem;">{trek.duration} day(s)</td></tr>
                <tr><td style="padding:.5rem;color:#94a3b8;">Start Date</td><td style="padding:.5rem;">{trek.start_date}</td></tr>
                <tr><td style="padding:.5rem;color:#94a3b8;">End Date</td><td style="padding:.5rem;">{trek.end_date}</td></tr>
              </table>
              <p style="color:#94a3b8;">Please arrive on time and carry all required gear. Have a great trek!</p>
              <hr style="border-color:rgba(255,255,255,0.1);">
              <p style="font-size:.8rem;color:#64748b;">Trekking Management Application &mdash; Automated Reminder</p>
            </div></body></html>
            """
            if _send_mail(f"Reminder: Your trek '{trek.name}' starts tomorrow!", [user.email], html):
                sent += 1
            logger.info("[REMINDER] %s -> %s", user.email, trek.name)

    logger.info("Daily reminders complete: sent %d for %d treks.", sent, len(upcoming_treks))
    return f"Sent {sent} reminders for {len(upcoming_treks)} treks."


@celery_instance.task
def generate_monthly_report():
    """
    Scheduled Job: Runs on 1st of every month at 00:05 UTC.
    Generates an HTML activity report and emails it to all Admins.
    """
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    recent_treks = Trek.query.filter(Trek.start_date >= thirty_days_ago).all()
    total_bookings = Booking.query.filter(
        Booking.booking_date >= thirty_days_ago,
        Booking.status != 'Cancelled'
    ).count()
    unique_participants = db.session.query(func.count(func.distinct(Booking.user_id))).filter(
        Booking.booking_date >= thirty_days_ago,
        Booking.status != 'Cancelled'
    ).scalar() or 0

    top_treks_rows = (
        db.session.query(Trek.name, Trek.location, func.count(Booking.id).label('cnt'))
        .join(Booking, Booking.trek_id == Trek.id)
        .filter(Booking.booking_date >= thirty_days_ago, Booking.status != 'Cancelled')
        .group_by(Trek.id).order_by(func.count(Booking.id).desc()).limit(5).all()
    )

    top_rows_html = ''.join(
        f"<tr><td style='padding:.5rem'>{r[0]}</td><td style='padding:.5rem'>{r[1]}</td><td style='padding:.5rem;text-align:center'>{r[2]}</td></tr>"
        for r in top_treks_rows
    ) or "<tr><td colspan='3' style='padding:.5rem;color:#94a3b8'>No data</td></tr>"

    html = f"""
    <html><body style="font-family:Arial,sans-serif;background:#0f172a;color:#f8fafc;padding:2rem;margin:0;">
    <div style="max-width:680px;margin:auto;background:#1e293b;border-radius:14px;padding:2.5rem;border:1px solid rgba(255,255,255,0.1);">
      <h1 style="color:#34d399;margin-top:0;">Monthly Activity Report &mdash; {now.strftime('%B %Y')}</h1>
      <p style="color:#94a3b8;">Period: <strong>{thirty_days_ago.strftime('%d %b %Y')}</strong> to <strong>{now.strftime('%d %b %Y')}</strong></p>
      <div style="display:flex;gap:1rem;margin:1.5rem 0;flex-wrap:wrap;">
        <div style="flex:1;min-width:140px;background:rgba(16,185,129,0.1);border-radius:10px;padding:1rem;text-align:center;">
          <div style="font-size:2rem;font-weight:800;color:#34d399;">{len(recent_treks)}</div>
          <div style="font-size:.8rem;color:#94a3b8;text-transform:uppercase;">Treks Conducted</div>
        </div>
        <div style="flex:1;min-width:140px;background:rgba(59,130,246,0.1);border-radius:10px;padding:1rem;text-align:center;">
          <div style="font-size:2rem;font-weight:800;color:#60a5fa;">{unique_participants}</div>
          <div style="font-size:.8rem;color:#94a3b8;text-transform:uppercase;">Unique Participants</div>
        </div>
        <div style="flex:1;min-width:140px;background:rgba(245,158,11,0.1);border-radius:10px;padding:1rem;text-align:center;">
          <div style="font-size:2rem;font-weight:800;color:#fbbf24;">{total_bookings}</div>
          <div style="font-size:.8rem;color:#94a3b8;text-transform:uppercase;">Total Bookings</div>
        </div>
      </div>
      <h3 style="color:#34d399;">Most Popular Treks</h3>
      <table style="width:100%;border-collapse:collapse;">
        <thead><tr style="background:rgba(0,0,0,0.3);">
          <th style="padding:.5rem;text-align:left;color:#64748b;font-size:.75rem;text-transform:uppercase;">Trek</th>
          <th style="padding:.5rem;text-align:left;color:#64748b;font-size:.75rem;text-transform:uppercase;">Location</th>
          <th style="padding:.5rem;text-align:center;color:#64748b;font-size:.75rem;text-transform:uppercase;">Bookings</th>
        </tr></thead>
        <tbody>{top_rows_html}</tbody>
      </table>
      <hr style="border-color:rgba(255,255,255,0.1);margin:2rem 0 1rem;">
      <p style="font-size:.78rem;color:#64748b;">Generated {now.strftime('%d %b %Y %H:%M UTC')} &mdash; TMA</p>
    </div></body></html>
    """

    admins = User.query.filter_by(role='Admin', active=True).all()
    for admin in admins:
        if admin.email:
            _send_mail(f"TMA Monthly Report — {now.strftime('%B %Y')}", [admin.email], html)

    report = {"treks_conducted": len(recent_treks), "total_participants": unique_participants}
    logger.info("[MONTHLY REPORT] %s", report)
    return report


@celery_instance.task
def export_user_history(user_id):
    """
    User-triggered async job: Generates a CSV of the user's trekking history.
    Triggered via .delay() from trekker route — runs in Celery worker.
    """
    user = User.query.get(user_id)
    if not user:
        return "User not found"

    bookings = Booking.query.filter_by(user_id=user_id).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['User ID', 'Username', 'Trek Name', 'Location',
                     'Start Date', 'End Date', 'Booking Date', 'Booking Status', 'Payment Status'])

    for b in bookings:
        trek = b.trek
        start_date = trek.start_date.strftime('%Y-%m-%d') if trek and trek.start_date else 'N/A'
        end_date   = trek.end_date.strftime('%Y-%m-%d')   if trek and trek.end_date   else 'N/A'
        writer.writerow([
            user.id, user.username,
            trek.name     if trek else 'Unknown',
            trek.location if trek else 'Unknown',
            start_date, end_date,
            b.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            b.status, b.payment_status
        ])

    csv_data = output.getvalue()
    output.close()
    return csv_data
