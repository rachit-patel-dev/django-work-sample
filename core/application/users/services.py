import datetime
import uuid
from typing import Optional
from uuid import UUID

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models.query import QuerySet

from core.domain.text_choices import UserStatusChoices
from core.domain.users.models import User, UserBasePermissions, UserPersonalData
from core.domain.users.services import UserServices
from core.infrastructure.mailing_services.services import SendMail
from utils.data_manipulation.type_conversion import decode_by_base64, encode_by_base64
from utils.django.exceptions import (
    ForgotPasswordLinkExpired,
    InvalidCredentialsException,
    InvalidParameterException,
    UserAlreadyExist,
    UserDoesNotExist,
    UserDoesNotVerified,
    ValidationException,
)
from utils.django.regex import validate_email_by_regex, validate_password_by_regex


class UserAppServices:
    user_services = UserServices()
    mailing_services = SendMail()

    # =====================================================================================
    # USER
    # =====================================================================================
    def get_user_by_id(self, id: UUID) -> User:
        """
        Get user instance by id
        """
        try:
            return self.user_services.get_user_repo().get(id=id)
        except Exception as e:
            raise UserDoesNotExist(
                message="User is not registered yet.", item={"error": e.args}
            )

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user instance by email
        """
        try:
            return self.user_services.get_user_repo().get(email=email)
        except Exception as e:
            raise UserDoesNotExist(
                message="User is not registered yet.", item={"error": e.args}
            )

    def list_users(self) -> QuerySet[User]:
        """
        List all users
        """
        return self.user_services.get_user_repo().all()

    def check_user_email_exists(self, email: str) -> bool:
        """
        Check if a user with the given email exists.

        Parameters:
        - email (str): The email address to check.

        Returns:
        - bool: True if a user with the given email exists, False otherwise.
        """
        return self.list_users().filter(email=email).exists()

    def check_user_is_verified_by_id_or_email(
        self, id: uuid.UUID = None, email: str = None
    ) -> bool:
        """
        Check if a user with the given id or email is verified.

        Parameters:
        - id (UUID): The ID of the user to check.
        - email (str): The email address of the user to check.

        Returns:
        - bool: True if the user with the given email is verified, False otherwise.
        """
        try:
            if id:
                return (
                    self.list_users()
                    .filter(id=id, status=UserStatusChoices.VERIFIED)
                    .exists()
                )
            elif email:
                return (
                    self.list_users()
                    .filter(email=email, status=UserStatusChoices.VERIFIED)
                    .exists()
                )
            else:
                raise InvalidParameterException(
                    message="id or email is required.", item={}
                )
        except Exception as e:
            raise e

    def authenticate_and_login_user(self, email: str, password: str) -> User:
        """
        Manually Login User After Checking Verification
        """
        try:
            user_exists = self.check_user_email_exists(email=email)
            if not user_exists:
                raise UserDoesNotExist(
                    message="User with this email is not exists.",
                    item={"error_tag": "email"},
                )

            user_verified = self.check_user_is_verified_by_id_or_email(email=email)
            if not user_verified:
                raise UserDoesNotVerified(
                    message="""Email verification is required.<br><span class="verification-link" id="resend_verification_link">Resend verification link</span>""",
                    item={"error_tag": "common"},
                )

            user = authenticate(email=email, password=password)
            if user is not None:
                return user
            raise InvalidCredentialsException(
                message="Unable to log in with provided credentials.",
                item={"error_tag": "common"},
            )
        except Exception as e:
            raise e

    def create_user_from_dict(self, data: dict) -> User:
        """
        Create user from user's data dict
        """
        try:
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            email = data.get("email")
            password = data.get("password")

            # Email and Password Validation
            if not validate_email_by_regex(email=email):
                custom_error_message = "Please, Enter valid Email."
                raise ValidationException(
                    message=custom_error_message, item={"error_tag": "email"}
                )
            if not validate_password_by_regex(password=password):
                custom_error_message = "Password should contain at least one digit, lowercase, uppercase, special character and length should be between 8-32."
                raise ValidationException(
                    message=custom_error_message, item={"error_tag": "password"}
                )

            user_services = self.user_services
            if self.check_user_email_exists(email=email):
                raise UserAlreadyExist(
                    message="this email address already registered",
                    item={"error_tag": "email"},
                )

            personal_data = UserPersonalData(
                first_name=first_name, last_name=last_name, email=email
            )
            base_permissions = UserBasePermissions()

            user = user_services.get_user_factory().build_entity_with_id(
                password=password,
                personal_data=personal_data,
                base_permissions=base_permissions,
            )
            user.save()
            return user

        except Exception as e:
            raise e

    def create_and_send_verification_link(self, current_site: str, user: User) -> None:
        """
        Create and Send an Email for verification link
        """
        try:
            # Create a verification link using user id
            encoded_user_id = encode_by_base64(str(user.id))
            verification_link = (
                f"http://{current_site}/users/email/verification/{encoded_user_id}"
            )

            # Send a mail for verification using sendgrid with verification link
            sendgrid_email_verification_template_id = getattr(
                settings, "SENDGRID_VERIFY_EMAIL_TEMPLATE_KEY", None
            )

            template_data = {
                "username": user.full_name,
                "date_time": datetime.datetime.utcnow().strftime("%d-%b-%Y %H:%M:%S"),
                "verification_link": verification_link,
            }
            self.mailing_services.send_mail(
                to=user.email,
                template_id=sendgrid_email_verification_template_id,
                dynamic_data_for_template=template_data,
            )
        except Exception as e:
            raise e

    def verify_user_by_verification_link(self, encoded_user_id: str) -> User:
        """
        Verification of User Email Sent with Verification Link
        """
        try:
            with transaction.atomic():
                decoded_user_id = decode_by_base64(string=encoded_user_id)
                user = self.user_services.get_user_repo().get(id=decoded_user_id)
                if not self.check_user_is_verified_by_id_or_email(email=user.email):
                    user.status = UserStatusChoices.VERIFIED
                    user.save()
                return user
        except Exception as e:
            raise e

    # =====================================================================================
    # FORGOT PASSWORD FUNCTIONALITY
    # =====================================================================================
    def send_mail_for_forgot_password(self, data: dict) -> bool:
        """
        Send Mail to user if Email exist for forgot password
        """
        try:
            current_site = data.get("current_site")
            email = data.get("email")

            user = self.get_user_by_email(email=email)

            email_exists = self.check_user_email_exists(email=email)
            if not email_exists:
                raise UserDoesNotExist(
                    message="User with this email is not exists.",
                    item={"error_tag": "email"},
                )

            with transaction.atomic():
                expiry = (
                    datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
                ).strftime("%d-%m-%y %H:%M:%S")
                token = str(user.id) + "_" + expiry
                encoded_token = encode_by_base64(str(token))

                forgot_password_url = f"http://{current_site}/reset-password-confirm/?token={encoded_token}"

                # Send a mail for forgot password
                template_data = {
                    "username": user.full_name,
                    "date_time": datetime.datetime.utcnow().strftime(
                        "%d-%b-%Y %H:%M:%S"
                    ),
                    "reset_password_link": forgot_password_url,
                }
                sendgrid_forgot_password_template_id = getattr(
                    settings, "SENDGRID_FORGOT_PASSWORD_TEMPLATE_KEY", None
                )

                self.mailing_services.send_mail(
                    to=user.email,
                    template_id=sendgrid_forgot_password_template_id,
                    dynamic_data_for_template=template_data,
                )
                return True
        except Exception as e:
            raise e

    def verify_forgot_password_token(self, encoded_token: str) -> uuid.UUID:
        """
        Check Forgot Password Token is Exist and is not Expired
        """
        try:
            password_token = decode_by_base64(encoded_token)
            splitted_token_list = password_token.split("_")
            user_id = uuid.UUID(splitted_token_list[0])
            expiry = splitted_token_list[1]
            if (
                datetime.datetime.strptime(expiry, "%d-%m-%y %H:%M:%S")
                < datetime.datetime.utcnow()
            ):
                raise ForgotPasswordLinkExpired(
                    message="Forgot Password Link is Expired.",
                    item={"error_tag": "common"},
                )

            return user_id
        except Exception as e:
            raise e

    def set_new_password_for_forgot_password(self, data: dict):
        """
        Set New Password and Remove Forgot Password Token and Expiry Time
        """
        try:
            password = data.get("password")
            current_site = data.get("current_site")
            user_id = data.get("user_id")

            if not validate_password_by_regex(password=password):
                message = "Please, Enter strong password."
                raise ValidationException(
                    message=message, item={"error_tag": "password"}
                )

            user = self.get_user_by_id(id=user_id)
            user.set_password(password)
            user.save()

            # Send a mail for informing a user that password has been changed successfully
            login_link = f"http://{current_site}/onboarding/"
            template_data = {
                "username": user.full_name,
                "date_time": datetime.datetime.utcnow().strftime("%d-%b-%Y %H:%M:%S"),
                "login_link": login_link,
            }
            sendgrid_forgot_password_completed_template_id = getattr(
                settings, "SENDGRID_FORGOT_PASSWORD_COMPLETED_TEMPLATE_KEY", None
            )
            self.mailing_services.send_mail(
                to=user.email,
                template_id=sendgrid_forgot_password_completed_template_id,
                dynamic_data_for_template=template_data,
            )
        except Exception as e:
            raise e
