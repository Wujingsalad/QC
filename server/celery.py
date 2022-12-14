import os

# set the default Django settings module for the 'celery' program.
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('server')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.timezone = "Asia/Shanghai"
app.conf.enable_utc = False


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')