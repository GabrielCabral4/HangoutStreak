import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hangout_streak.settings')

app = Celery('hangout_streak')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-and-update-streaks': {
        'task': 'events.tasks.check_and_update_streaks',
        'schedule': crontab(minute=0, hour=0),  # Run daily at midnight
    },
    'cleanup-expired-stories': {
        'task': 'events.tasks.cleanup_expired_stories',
        'schedule': crontab(minute=0),  # Run hourly
    },
} 