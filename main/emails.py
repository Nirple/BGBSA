import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class SMTP2GOBackend(BaseEmailBackend):

    def send_messages(self, email_messages):



def _send_smtp2go_api_email(subject: str, message: str, to: list) -> dict:
    """Send email via smtp2go api."""
    payload = {
        'api_key': settings.EMAIL_API_KEY,
        'to': to,
        'sender': settings.EMAIL_DEFAULT_FROM,
        'subject': subject,
        'text_body': message,
        # 'html_body': '<h1>You're my favorite test person ever</h1>',
        'custom_headers': [
            {
                'header': 'Reply-To',
                'value': settings.EMAIL_DEFAULT_REPLY_TO,
            }
        ],
        # 'attachments': [
        #     {
        # 'filename': 'test.pdf',
        # 'fileblob': '--base64-data--',
        # 'mimetype': 'application/pdf'
        # },
        # ]
    }
    logger.info(f'Email payload: {payload}')
    res = requests.post(
        f'{settings.EMAIL_API_URL}/email/send',
        json=payload
    )
    try:
        res.raise_for_status()
    except requests.HTTPError as exc:
        logger.exception(f'Failed to send email: {res.content}')
        raise ValueError(f'{res.content}') from exc
    data = res.json()
    logger.info(f'Response: {data}')
    for failure in data['data']['failures']:
        logger.error(failure)
    return data

#
# @retry(SMTPException)
# def send_test_email(email_addresses: List[str]):
#     logger.info(f'Sending test email to {email_addresses}...')
#     _send_smtp2go_api_email(subject, message, email_addresses)
#     logger.info('Test email sent.')
