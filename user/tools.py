import logging
import hashlib
from django.conf import settings

from user.serializers import JWTUserPayloadSerializer

logger = logging.getLogger('app')


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': JWTUserPayloadSerializer(user, context={'request': request}).data
    }


def jwt_get_username_from_payload_handler(payload):
    return payload.get('email')


def jwt_get_user_secret_key(user):
    s_common = settings.SECRET_KEY
    s_jwt = settings.JWT_AUTH['JWT_SECRET_KEY']
    pass_hash = user.password
    skey = s_common + s_jwt + pass_hash
    sha = hashlib.sha512(skey.encode()).hexdigest()
    return sha
