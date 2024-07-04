from twilio.rest import Client
import logging
from settings import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PushController:
    def send_sms(self, number, message):

        client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

        message = client.messages.create(
            from_="+13613101634",
            body=message,
            to=f"+55{number}"
        )
        logger.info(f"Mensagem por SMS: {message.sid}")
