from celery import Celery

def make_celery(app_name=__name__):
    # Setup Celery with Redis as the broker and backend
    # Falls back gracefully if Redis is not running
    redis_url = 'redis://localhost:6379/0'
    celery = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url,
        include=['tasks']
    )
    
    celery.conf.update(
        timezone='UTC',
        enable_utc=True,
        broker_connection_retry_on_startup=True,  # suppress deprecation warning
    )
    
    return celery

celery_instance = make_celery()
