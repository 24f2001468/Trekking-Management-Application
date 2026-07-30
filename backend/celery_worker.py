from app import create_app
from celery_app import celery_instance
from celery.schedules import crontab
import tasks

# Create app context for celery
app = create_app()
app.app_context().push()

# Celery Beat Schedule
celery_instance.conf.beat_schedule = {
    'daily-trek-reminders': {
        'task': 'tasks.send_daily_reminders',
        # Run every day at 8:00 AM UTC
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-admin-report': {
        'task': 'tasks.generate_monthly_report',
        # Run on the 1st of every month at midnight
        'schedule': crontab(hour=0, minute=0, day_of_month='1'),
    },
}

# Entry point for the celery worker and beat:
# celery -A celery_worker.celery_instance worker --pool=eventlet -l info
# celery -A celery_worker.celery_instance beat -l info
