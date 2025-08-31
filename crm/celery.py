import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

app = Celery("crm")

app.config_from_objects("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
