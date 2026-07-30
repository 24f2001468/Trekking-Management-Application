from celery_app import celery_instance
from models.database import db
from models.models import Trek, Booking, User
from datetime import datetime, timedelta
import csv
import io
import time

@celery_instance.task
def send_daily_reminders():
    """
    Scheduled Job: Run daily to notify trekkers of treks starting tomorrow.
    """
    tomorrow = (datetime.utcnow() + timedelta(days=1)).date()
    
    # Find treks starting tomorrow
    upcoming_treks = Trek.query.filter_by(start_date=tomorrow).all()
    
    for trek in upcoming_treks:
        bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
        for booking in bookings:
            user = booking.user
            # Mock sending email/SMS/webhook
            print(f"[REMINDER] Sending email to {user.email}: Your trek '{trek.name}' starts tomorrow!")
            
    return f"Sent reminders for {len(upcoming_treks)} treks."

@celery_instance.task
def generate_monthly_report():
    """
    Scheduled Job: Run monthly to generate stats for Admins.
    """
    # Mock date ranges (e.g., last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Get completed treks in the last 30 days (based on start date or status)
    recent_treks = Trek.query.filter(Trek.start_date >= thirty_days_ago).all()
    
    total_participants = 0
    for trek in recent_treks:
        total_participants += Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        
    report = {
        "treks_conducted": len(recent_treks),
        "total_participants": total_participants,
    }
    
    # Mock sending report to Admins
    print(f"[MONTHLY REPORT] Admin Report Generated: {report}")
    return report

@celery_instance.task
def export_user_history(user_id):
    """
    User-triggered Job: Generates a CSV of their trekking history.
    """
    # Simulate a long-running process
    time.sleep(3) 
    
    user = User.query.get(user_id)
    if not user:
        return "User not found"
        
    bookings = Booking.query.filter_by(user_id=user_id).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Booking Date', 'Trek Name', 'Location', 'Dates', 'Booking Status', 'Payment Status'])
    
    for b in bookings:
        trek = b.trek
        start_date = trek.start_date.strftime('%Y-%m-%d') if trek and trek.start_date else 'N/A'
        end_date = trek.end_date.strftime('%Y-%m-%d') if trek and trek.end_date else 'N/A'
        
        writer.writerow([
            b.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            trek.name if trek else 'Unknown',
            trek.location if trek else 'Unknown',
            f"{start_date} to {end_date}",
            b.status,
            b.payment_status
        ])
        
    csv_data = output.getvalue()
    output.close()
    
    # Returning the raw CSV string via the Redis backend
    # In a real app with large files, we would save to S3 or a local temp file and return the URL.
    return csv_data
