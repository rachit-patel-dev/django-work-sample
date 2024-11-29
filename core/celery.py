import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Create an instance of the Celery application
app = Celery(
    "core",
    include=[
        "core.interface.users.tasks",
    ],
)

# Load the Celery configuration from the Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover and register tasks from Django app modules
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
