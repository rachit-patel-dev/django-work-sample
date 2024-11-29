import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple, Union

from dataclass_type_validator import dataclass_validate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import validate_email
from django.db import models

from core.domain.text_choices import UserStatusChoices
from core.infrastructure.log_services.models import AttributeLogger
from utils.data_manipulation.type_conversion import convert_to_dict
from utils.django import custom_models

log = AttributeLogger(logging.getLogger(__name__))


@dataclass(frozen=True)
class UserID:
    """
    Value Object (Dataclass) should be used to generate and pass Id to UserFactory
    """

    id: uuid.UUID = field(init=False, default_factory=uuid.uuid4)


@dataclass_validate(before_post_init=True)
@dataclass(frozen=True)
class UserPersonalData:
    """
    User personal data which is passed to the UserFactory
    """

    email: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    username: Union[str, None] = None
    status: str = UserStatusChoices.REGISTERED

    def __post_init__(self):
        validate_email(self.email)


@dataclass(frozen=True)
class UserBasePermissions:
    """
    User Base Permissions which is passed to the UserFactory
    """

    is_deleted: bool = False
    is_staff: bool = False
    is_superuser: bool = False


class UserManagerAutoID(UserManager):
    """
    UserManagerAutoID class extends the Django UserManager class and
    provides additional functionality for creating a superuser with an automatically generated ID.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Create a superuser with the given username, email, and password.

        Parameters:
        - username (str): The username for the superuser.
        - email (str, optional): The email address for the superuser. Defaults to None.
        - password (str, optional): The password for the superuser. Defaults to None.
        - **extra_fields (dict): Additional fields to be set for the superuser.

        Returns:
        - User: The created superuser instance.

        Raises:
        - ValueError: If the email, is_staff and is_superuser fields are not proper.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatusChoices.VERIFIED)

        if email is None:
            raise ValueError("Email field is required.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if id not in extra_fields:
            extra_fields = dict(extra_fields, id=UserID().id)

        return self._create_user(username, email, password, **extra_fields)


class User(custom_models.ActivityTracking, AbstractUser):
    """
    User Model with ActivityTracking model
    """

    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=155, null=True, blank=True, unique=False)
    email = models.EmailField(max_length=64, unique=True)
    is_deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=55,
        choices=UserStatusChoices.choices,
        default=UserStatusChoices.REGISTERED,
    )

    objects = UserManagerAutoID()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "user"

    @property
    def full_name(self):
        """
        Returns Full Name by using first_name, last_name or email
        """
        try:
            if self.first_name and self.last_name:
                full_name = f"{self.first_name} {self.last_name}"
            elif self.first_name:
                full_name = self.first_name
            else:
                splited_email = self.email.split("@")[0]
                full_name = splited_email.replace(".", " ").strip()
            return full_name
        except Exception as e:
            log.error(msg=f"Error occurred while generating full name: {str(e)}")

    def __str__(self):
        return self.email


class UserFactory:
    @staticmethod
    def build_entity_with_id(
        password: str,
        personal_data: UserPersonalData,
        base_permissions: UserBasePermissions,
    ) -> User:
        """
        Factory method used for building an instance of User
        """

        personal_data_dict = convert_to_dict(personal_data, skip_empty=True)
        base_permissions_dict = convert_to_dict(base_permissions, skip_empty=True)
        password = make_password(password=password)
        return User(
            id=UserID().id,
            **personal_data_dict,
            **base_permissions_dict,
            password=password,
        )
