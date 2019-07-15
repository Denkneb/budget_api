import json
import logging

import requests
from celery.task import task
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse


@task
def send_message(conf, to, subject, message):

    logging.debug('To: %s' % to)
    logging.debug('From: %s' % conf['email_noreply'])
    logging.debug('Message: %s' % message)

    if not conf['mailgun_api_url']:
        send_mail(
            subject=subject,
            message='',
            from_email=conf['email_noreply'],
            recipient_list=to,
            html_message=message
        )
    else:
        res = requests.post(
            conf['mailgun_api_url'],
            auth=("api", conf['mailgun_api_key']),
            data={
                "from": conf['email_noreply'],
                "to": to,
                "subject": subject,
                "html": message,
                "o:native-send": "yes"
            },
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )

        logging.debug('Result: %s' % res)


@task
def send_push(conf, token, title, message):
    """Send push notification"""

    logging.debug('Conf: %s' % conf)
    logging.debug('To: %s' % token)
    logging.debug('Title: %s' % title)
    logging.debug('Message: %s' % message)

    if conf['firebase_key_server']:
        data = {
            'notification': {
                'title': title,
                'body': message,
                'sound': 'default'
            },
            'data': {
                'title': title,
                'body': message,
            },
            'registration_ids': token
        }

        response = requests.post(
            url=conf['firebase_url_request'],
            data=json.dumps(data),
            headers={
                'content-type': 'application/json',
                'authorization': 'key=' + conf['firebase_key_server'],
            },
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        )
        if response.status_code != HttpResponse.status_code:
            logger = logging.getLogger(__name__)
            logger.error(
                'Для пользователя - "{}" не получилось отправить пуш уведомление - "{}".'.format(token, title),
                exc_info=True,
            )
