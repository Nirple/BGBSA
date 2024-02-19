import logging

from django.core.management import BaseCommand

from main.send_emails import _send_smtp2go_api_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send test api email'

    def add_arguments(self, parser):
        parser.add_argument(
            'email_address', type=str, help='Email address to send test to.')

    def handle(self, email_address: str, *args, **options):
        logger.info('Testing smtp2go api email')
        res = _send_smtp2go_api_email(
            'test subject',
            'test message',
            [email_address]
        )
        logger.info('finished testing smtp2go api email')
