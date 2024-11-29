from django.db import models


class ActivityTracking(models.Model):
    """
    A CustomModel includes fields that reflect when the model has been created or updated
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
