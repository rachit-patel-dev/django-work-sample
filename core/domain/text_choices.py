from django.db import models


class UserStatusChoices(models.TextChoices):
    """
    A class representing the choices for the user status in a Django model.

    Attributes:
        REGISTERED (str): The status for a registered user.
        ACTIVATED (str): The status for an activated user.
        VERIFIED (str): The status for a verified user.
        DEACTIVATED (str): The status for a deactivated user.
    """

    REGISTERED = "registered", "REGISTERED"
    ACTIVATED = "activated", "ACTIVATED"
    VERIFIED = "verified", "VERIFIED"
    DEACTIVATED = "deactivated", "DEACTIVATED"
