from celery import Celery

def make_celery(app_name=__name__):
    # Setup Celery with Redis as the broker and backend
    redis_url = 'redis://localhost:6379/0'
    celery = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url,
        include=['tasks']
    )
    
    # Optional: Configure timezone or other celery settings
    celery.conf.update(
        timezone='UTC',
        enable_utc=True,
        # Schedule configuration for Celery Beat will go here
    )
    
    return celery

celery_instance = make_celery()
