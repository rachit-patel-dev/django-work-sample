"""This file includes the function for the mail functionality"""

import logging

from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from core.infrastructure.log_services.models import AttributeLogger
from utils.django.exceptions import SendgridEmailException

log = AttributeLogger(logging.getLogger(__name__))


class SendMailBySendgrid:
    """
    Provides functionality to send emails using SendGrid.

    Attributes:
        SENDGRID_API_KEY (str): The API key for the SendGrid service.
        SENDGRID_FROM_MAIL (str): The email address from which the emails will be sent.

    Methods:
        send_mail_by_sendgrid : Sends an email using SendGrid.
    """

    def __init__(self) -> None:
        self.SENDGRID_API_KEY = getattr(settings, "SENDGRID_API_KEY", None)
        self.SENDGRID_FROM_MAIL = getattr(settings, "SENDGRID_FROM_MAIL", None)

    def send_mail_by_sendgrid(
        self, to_email: str, template_id: str, dynamic_data_for_template: dict
    ) -> dict:
        """
        Sends an email using sendgrid's python sdk.

        Parameters:
            to_email (str): The email address to which the email will be sent.
            template_id (str): The ID of the SendGrid template to be used for the email.
            dynamic_data_for_template (dict): A dictionary containing dynamic data to be used in the SendGrid template.

        Returns:
            dict: A dictionary containing the response from the SendGrid API.

        Raises:
            SendgridEmailException: If an error occurs while sending the email using SendGrid.
        """
        message = Mail(
            from_email=self.SENDGRID_FROM_MAIL,
            to_emails=to_email,
        )
        message.dynamic_template_data = dynamic_data_for_template
        message.template_id = template_id
        try:
            sg = SendGridAPIClient(self.SENDGRID_API_KEY)
            response = sg.send(message)
            return response
        except Exception as e:
            raise SendgridEmailException(
                message="Something went wrong while sending mail using sendgrid.",
                item={"error": str(e)},
            )


class SendMail:
    """
    Class for sending emails.

    Attributes:
        sendgrid_service (SendMailBySendgrid): An instance of the SendMailBySendgrid class.
    """

    def __init__(self) -> None:
        self.sendgrid_service = SendMailBySendgrid()

    def send_mail(
        self, to: str, template_id: str, dynamic_data_for_template: dict
    ) -> dict:
        """
        Sends an email.

        Parameters:
            to (str): The email address to which the email will be sent.
            template_id (str): The ID of the template to be used for the email.
            dynamic_data_for_template (dict): A dictionary containing dynamic data to be used in the template.

        Returns:
            dict: A dictionary containing the response.

        Raises:
            SendgridEmailException: If an error occurs while sending the email using SendGrid.
        """
        try:
            response = self.sendgrid_service.send_mail_by_sendgrid(
                to_email=to,
                template_id=template_id,
                dynamic_data_for_template=dynamic_data_for_template,
            )
            log.info(msg="Mail sent successfully.")
            return response
        except Exception as e:
            if isinstance(e, SendgridEmailException):
                message = "Something went wrong while sending mail using sendgrid."
                log.error(msg=message)
                raise SendgridEmailException(
                    message=message,
                    item={"error": str(e)},
                )
            log.error(msg="Something went wrong while sending an email.")
            raise e
