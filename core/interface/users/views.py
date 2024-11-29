import json
import logging
import uuid

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import View

from core.application.users.services import UserAppServices
from core.infrastructure.log_services.models import AttributeLogger
from utils.django.exceptions import (
    ForgotPasswordException,
    ForgotPasswordLinkExpired,
    InvalidCredentialsException,
    SendgridEmailException,
    UserAlreadyExist,
    UserDoesNotExist,
    UserDoesNotVerified,
    ValidationException,
)

log = AttributeLogger(logging.getLogger(__name__))

user_services = UserAppServices()


@login_required
def home(request):
    """
    Render the home page for the authenticated user.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A rendered HTML template for the home page.

    Raises:
    - Redirect to the 404 page if an exception occurs while rendering the home page.
    """
    try:
        log.info(msg="rendering home page.")
        return render(request, "users/home.html")
    except Exception as e:
        message = f"Something went wrong while rendering home page and Error : {e.args}"
        log.error(msg=message)
        return redirect("users:404")


class SignupView(View):
    """
    View class for handling user signup.

    Methods:
    - get(request): Renders the signup.html template.
    - post(request): Handles the POST request for user signup.
                    Creates a new user, sends a verification email, and
                    returns a JSON response.

    Raises:
    - ValidationException: If there is a validation error during user creation.
    - UserAlreadyExist: If a user with the same email already exists.
    - SendgridEmailException: If there is an error while sending the verification email.
    - Exception: If there is any other error during user signup.
    """

    def get(self, request):
        """
        Renders the signup.html template.

        Returns:
            HttpResponse: The rendered signup.html template.
        """
        return render(request, "users/signup.html")

    def post(self, request):
        """
        Handles the POST request for user signup.

        Returns:
            JsonResponse: A JSON response indicating whether the user was registered successfully or not.

        Raises:
            ValidationException: If there is a validation error during user creation.
            UserAlreadyExist: If a user with the same email already exists.
            SendgridEmailException: If there is an error while sending the verification email.
            Exception: If there is any other error during user signup.
        """
        try:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                data = json.load(request)

                # Creating a user by dict
                user = user_services.create_user_from_dict(data)

            if user:
                # Send a mail for verification
                current_site = get_current_site(request=request)
                user_services.create_and_send_verification_link(current_site, user)
                message = "User created successfully. Please check your email for verification."
                log.info(msg=message)
                messages.success(request, message)
                return JsonResponse({"registered": True})

            raise Exception
        except ValidationException as ve:
            log.error(msg=ve.message + f"{ve.args}")
            messages.error(request, ve.message)
            return JsonResponse(
                data={
                    "error_message": ve.message,
                    "error_tag": ve.item.get("error_tag"),
                    "error": ve.args,
                }
            )
        except UserAlreadyExist as uae:
            log.error(msg=uae.message + f"{uae.args}")
            messages.error(request, uae.message)
            return JsonResponse(
                data={
                    "error_message": uae.message,
                    "error_tag": uae.item.get("error_tag"),
                    "error": uae.args,
                }
            )
        except SendgridEmailException as sgee:
            log.error(msg=sgee.message)
            return JsonResponse(data={"registered": True})
        except Exception as e:
            message = "Something went wrong while registering a user."
            log.error(msg=f"Error : {str(e)} and Line No.- {e.__traceback__.tb_lineno}")
            messages.error(request, str(e))
            return JsonResponse(data={"error_message": message, "error": e.args})


class LoginView(View):
    """
    Handles the user login functionality.

    Methods:
    - get(request): Renders the login page.
    - post(request): Handles the POST request for user login.

    Raises:
    - UserDoesNotVerified: If the user is not verified.
    - UserDoesNotExist: If the user does not exist.
    - InvalidCredentialsException: If the provided credentials are invalid.
    - Exception: If any other error occurs during user login.
    """

    def get(self, request):
        """
        Renders the login.html template.

        Returns:
            HttpResponse: The rendered login.html template.
        """
        return render(request, "users/login.html")

    def post(self, request):
        """
        Handles the POST request for user login.

        Returns:
        - JsonResponse: A JSON response indicating whether the user was logged in successfully or not.

        Raises:
        - UserDoesNotVerified: If the user is not verified.
        - UserDoesNotExist: If the user does not exist.
        - InvalidCredentialsException: If the provided credentials are invalid.
        - Exception: If any other error occurs during user login.
        """
        try:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                data = json.load(request)
                email = data.get("email")
                password = data.get("password")

                user = user_services.authenticate_and_login_user(email, password)

                if user:
                    login(request, user)
                    messages.success(request, f"Welcome, {user.full_name}!")
                    log.info(msg=f"{user.full_name} has been logged in successfully.")
                    return JsonResponse({"logged_in": True})
                raise Exception
        except UserDoesNotVerified as udnv:
            log.error(msg=udnv.message)
            messages.error(request, udnv.message)
            return JsonResponse(
                {
                    "error_message": udnv.message,
                    "error_tag": udnv.item.get("error_tag"),
                    "error": udnv.args,
                }
            )
        except UserDoesNotExist as usne:
            log.error(msg=f"{usne.message} and Rendering to Signup Page.")
            messages.error(request, usne.message)
            return JsonResponse(
                {
                    "error_message": usne.message,
                    "error_tag": usne.item.get("error_tag"),
                    "error": usne.args,
                }
            )
        except InvalidCredentialsException as ice:
            log.error(msg=ice.message)
            messages.error(request, ice.message)
            return JsonResponse(
                {
                    "error_message": ice.message,
                    "error_tag": ice.item.get("error_tag"),
                    "error": ice.args,
                }
            )
        except Exception as e:
            message = "Something went wrong while logging a user."
            log.error(msg=f"Error : {str(e)} and Line No.- {e.__traceback__.tb_lineno}")
            messages.error(request, str(e))
            return JsonResponse(data={"error_message": message, "error": e.args})


def logout_view(request):
    """
    Logs out the current user and redirects to the login page.

    Returns:
    - A redirect response to the login page.

    Raises:
    - Redirect to the 404 page if an exception occurs during the logout process.
    """
    try:
        logout(request)
        log.info(
            msg=f"User({request.user.email}) logged out successfully and Redirecting to Login Page."
        )
        return redirect("users:login")
    except Exception as e:
        log.error(msg=e.args)
        return redirect("users:404")


def send_verification_link_manually(request, email: str):
    """
    Sends a verification link manually to the specified email address.

    Parameters:
    - request: The Django request object.
    - email (str): The email address to send the verification link to.

    Returns:
    - HttpResponseRedirect: A redirect to the login page.

    Raises:
    - UserDoesNotExist: If the user with the specified email does not exist.
    - SendgridEmailException: If there is an error while sending the verification link using Sendgrid.
    - Exception: If there is any other error while sending the verification link.
    """
    try:
        log.info(msg="Entered into sending manually verification link.")
        user = user_services.get_user_by_email(email=email)
        user_services.create_and_send_verification_link(
            current_site=get_current_site(request=request), user=user
        )
        messages.success(
            request, message=f"Email verification link has been sent to {email}."
        )
        return redirect("users:login")
    except UserDoesNotExist as udne:
        log.error(msg=udne.message)
        message = "Something went wrong while manually sending verification link."
        messages.error(request, message=message)
        return redirect("users:login")
    except SendgridEmailException as see:
        message = "Something went wrong while manually sending verification link in sendgrid mail function."
        log.error(msg=f"{message} and Error : {see.message}")
        messages.error(
            request,
            message="Something went wrong while manually sending verification link.",
        )
        return redirect("users:login")
    except Exception as e:
        message = "Something went wrong while manually sending verification link."
        log.error(msg=f"{message} and Error : {e.args}")
        messages.error(request, message=message)
        return redirect("users:login")


def user_email_verification(request, encoded_user_id: str):
    """
    Verifying the user's email address based on the provided encoded user ID.
    It uses the 'verify_user_by_verification_link' method to verify the user.

    Parameters:
    - request: The HTTP request object.
    - encoded_user_id (str): The encoded user ID used for verification.

    Returns:
    - HttpResponseRedirect: Redirects the user to the login page if the email is verified successfully.
    - HttpResponseRedirect: Redirects the user to the 404 page if an error occurs during the verification process.

    Raises:
    - Exception: If an error occurs during the verification process.
    """
    log.info(msg="Entered into User email verification")
    try:
        user = user_services.verify_user_by_verification_link(
            encoded_user_id=encoded_user_id
        )
        log.info(
            msg=f"User({user.email}) is verified successfully and Redirecting to Login Page."
        )
        messages.success(
            request, message="Email Verified Successfully. You can login here."
        )
        return redirect("users:login")
    except Exception as e:
        log.error(
            msg="Something went wrong while verifying user email and Rendering to 404 Page."
        )
        messages.error(request, message="Please, try after some time.")
        return redirect("users:404")


class PasswordResetView(View):
    """
    View class for handling password reset functionality.

    Methods:
    - get(request): Renders the password reset page.
    - post(request): Handles the AJAX post request for password reset.

    Exceptions:
    - UserDoesNotExist: Raised when the user does not exist.
    - SendgridEmailException: Raised when there is an error with sending the email.

    Returns:
    - For GET request: Renders the password reset page.
    - For AJAX POST request: Returns a JSON response indicating the success or failure of the password reset operation.
    """

    def get(self, request):
        """
        Renders the password reset page.

        Returns:
            HttpResponse: The rendered password reset page.
        """

        log.info(msg="Entered into password reset view.")
        return render(request, "users/password_reset.html")

    def post(self, request):
        """
        Handles the AJAX post request for password reset.

        Exceptions:
        - UserDoesNotExist: Raised when the user does not exist.
        - SendgridEmailException: Raised when there is an error with sending the email.
        - Exception: Raised when there is any other error during password reset.

        Returns:
        - JsonResponse: A JSON response indicating the success or failure of the password reset operation.
        If the password reset instruction is successfully sent, the response will contain {"email_exists": True}.
        If the user does not exist, the response will contain {"email_exists": False}.
        If there is an error with sending the email.
        """
        try:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                log.info(msg="Entered into Password Reset View's AJAX Post Method.")
                data = json.load(request)
                data["current_site"] = get_current_site(request)
                user_services.send_mail_for_forgot_password(data=data)
                message = f"Password reset instruction sent to {data.get('email', '')}."
                messages.success(request, message)
                log.info(msg=f"{message} and returns email_exists: True")
                return JsonResponse({"email_exists": True})
        except UserDoesNotExist as usne:
            log.error(msg=usne.message)
            return JsonResponse({"email_exists": False})
        except SendgridEmailException as sgee:
            log.error(msg=sgee.message)
            return JsonResponse({"error_message": sgee.message, "error": sgee.args})
        except Exception as e:
            message = "Something went wrong while PasswordReset"
            log.error(msg=message)
            return JsonResponse({"error_message": message, "error": e.args})


class PasswordResetConfirmView(View):
    """
    View class for confirming password reset.

    Methods:
    - get: Verify Token and Check Expiry date of token.
    - post: AJAX - Post Method of PasswordConfirmView.
    """

    def get(self, request):
        """
        Renders the password reset confirm page.

        Returns:
            HttpResponse: The rendered password_reset_confirm.html template.

        Raises:
            ForgotPasswordLinkExpired: If the forgot password link has expired.
            Exception: If there is any other error while verifying the forgot password link.
        """
        log.info(msg="Entered into password reset confirm view.")
        try:
            if "user_id_for_forgot_password" in request.session.keys():
                del request.session["user_id_for_forgot_password"]

            encoded_token = request.GET.get("token")
            user_id = user_services.verify_forgot_password_token(
                encoded_token=encoded_token
            )
            if user_id:
                request.session["user_id_for_forgot_password"] = str(user_id)
                log.info(
                    msg="Verified Forgot Password Token successfully and rendering to password reset confirm page."
                )
                return render(request, "users/password_reset_confirm.html")
            raise Exception
        except ForgotPasswordLinkExpired:
            message = "Forgot Password Link is Expired. Please, Try Again."
            messages.error(request, message)
            log.error(msg=f"{message} and redirecting to Onboarding page.")
            return redirect("users:password_reset")
        except Exception as e:
            log.error(
                msg=f"Something went wrong while verifying forgot password link and Error: {e.args}."
            )
            return redirect("users:404")

    def post(self, request):
        """
        Handles the AJAX post request for password reset.

        Exceptions:
        - ValidationException: If there is a validation error during password reset.
        - SendgridEmailException: If there is an error while sending the email.
        - ForgotPasswordException: If there is an error during the password reset process.
        - Exception: If there is any other error during password reset.

        Returns:
        - JsonResponse: A JSON response indicating the success or failure of the password reset operation.
        """
        try:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                log.info(
                    msg="Entered into Password Reset Confirm View's AJAX Post Method."
                )
                user_id = request.session["user_id_for_forgot_password"]
                if user_id and uuid.UUID(user_id) == request.user.id:
                    data_dict = json.load(request)
                    data_dict["current_site"] = get_current_site(request)
                    data_dict["user_id"] = request.session[
                        "user_id_for_forgot_password"
                    ]
                    user_services.set_new_password_for_forgot_password(data=data_dict)

                    message = "Password reset successfully."
                    messages.success(request, message)
                    log.info(msg=f"{message} and returns reset_successful: True.")
                    return JsonResponse({"reset_successful": True})
                raise Exception
        except ValidationException as ve:
            log.error(msg=ve.message)
            return JsonResponse(
                {"error_message": ve.message, "error_tag": ve.item.get("error_tag")}
            )
        except SendgridEmailException as sgee:
            log.error(msg=sgee.message)
            return JsonResponse({"reset_successful": True})
        except ForgotPasswordException as fpe:
            log.error(msg=fpe.message)
            return JsonResponse(
                {
                    "error_message": fpe.message,
                    "error_tag": fpe.item.get("error_tag"),
                    "error": fpe.args,
                }
            )
        except Exception as e:
            message = "Something went wrong while manually sending verification link."
            log.error(msg=f"{message} and Error : {e.args}")
            messages.error(request, message=message)
            return JsonResponse({"error_message": message})


def error_404_page_view(request, *args, **kwargs):
    """
    Renders the 404.html template for the 404 error page.

    Returns:
    - A rendered HTML template for the 404 error page.
    """
    return render(request, "users/404.html")
