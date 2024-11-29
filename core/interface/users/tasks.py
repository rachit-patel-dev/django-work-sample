import logging

from celery import shared_task

from core.infrastructure.log_services.models import AttributeLogger
from core.infrastructure.mailing_services.services import SendMail

log = AttributeLogger(logging.getLogger(__name__))


@shared_task
def send_mail_async(to: str, template_id: str, dynamic_data_for_template: dict) -> dict:
    """
    Asynchronously sends an email using Celery.

    Parameters:
    - to (str): The email address of the recipient.
    - template_id (str): Template Id.
    - dynamic_data_for_template (dict): Dictionary of template data.

    Returns:
    - response dict
    """
    try:
        return SendMail().send_mail(
            to=to,
            template_id=template_id,
            dynamic_data_for_template=dynamic_data_for_template,
        )
    except Exception as e:
        log.error(msg=f"Error : {str(e)} and Line No. - {e.__traceback__.tb_lineno}")
