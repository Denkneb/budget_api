import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import to_locale, get_language
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView

import user.serializers as serializers
from user.models import User, UsersSingUp

log = logging.getLogger('app')


def select_lang(lang: str) -> str:
    if lang:
        locale = lang
    else:
        locale = to_locale(get_language()).lower()

    if locale not in [l[0] for l in settings.LANGUAGES]:
        locale = settings.LANGUAGES[0][0]
    return locale


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)
    throttle_scope = 'reset-pass'

    def post(self, request, format=None, lang=None):
        """
        post: Сброс пароля пользователя, инициализирует отправку емайл
        ---

        ## Параметры запроса
        * **email** - **__str__** - емайл пользователя.

        ## Ответ:
            Статус 200

        ## Данные ответа
        -
        """

        locale = select_lang('ru')

        ser = serializers.RequestResetPassSerializer(data=request.data)
        if ser.is_valid():
            user = User.objects.filter(email=ser.data.get('email'))
            if not user.exists():
                # Всегда шлем успешный ответ, чтобы брутеры не узнали есть ли емэйл в системе
                # return Response(status=status.HTTP_404_NOT_FOUND, data={'status': _('Пользователь не найден')})
                return Response(status=status.HTTP_200_OK, data={'status': _('Иструкция отправлена')})

            user = user.get()
            user.init_pass_reset_process(lang=locale)
            return Response(status=status.HTTP_200_OK, data={'status': _('Иструкция отправлена')})
        else:
            return Response(ser.errors, status.HTTP_400_BAD_REQUEST)


class CheckResetCodeView(APIView):
    permission_classes = (AllowAny,)
    throttle_scope = 'reset-pass'

    def post(self, request, format=None):
        """
        post: Проверка числового кода сброса пароля пользователя
        #### Для двухступенчатой смены пароля по коду
        В случае неудачи, возвращает ошибку валидации с кодом 400
        ---


        ## Параметры запроса
        * **email** - **__str__** - емайл пользователя.
        * **code** - **__str__** - код для сброса пароля.

        ## Ответ (хэш для дальнейшей установки пароля):
            {'hash': 'c4292a70-c917-4cdb-9444-b8f78f0de60f'}

        ## Данные ответа
        * **hash** - **__uuid__** - хеш.
        """
        ser = serializers.CheckCodeSerializer(data=request.data)
        if ser.is_valid():
            hash_str = ser.save()
            return Response(status=status.HTTP_200_OK, data={'hash': hash_str})
        else:
            return Response(ser.errors, status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(APIView):
    permission_classes = (AllowAny,)
    throttle_scope = 'reset-pass'

    def post(self, request, lang=None, format=None):
        """
        post: Установка нового пароля пользователя
        ---

        ## Параметры запроса
        * **hash** - **__str__** - хеш (можно получить проверив код, или из емэйла (часть ссылки для сброса)).
        * **password** - **__str__** - новый пароль пользователя.
        * **confirm_password** - **__str__** - подтверждение пароля пользователя.

        ## Ответ:
            Статус 200

        ## Данные ответа
        -
        """
        locale = select_lang('ru')
        ser = serializers.RecoverySetNewPassword(data=request.data, context={'lang': locale})
        if ser.is_valid():
            if ser.validated_data.get('password') != ser.validated_data.get('confirm_password'):
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'password': _('Пароли не совпадают')})
            user = ser.save()
            return Response(status=status.HTTP_200_OK, data={'user': user.email})
        else:
            return Response(ser.errors, status.HTTP_400_BAD_REQUEST)


class UserSignUpView(APIView):
    permission_classes = (AllowAny,)
    throttle_scope = 'reset-pass'

    def post(self, request, lang=None, format=None):
        """
        post: Активация пользователей
        ---

        ## Параметры запроса
        * **token** - **__str__** - токен регистрации.
        * **password** - **__str__** - пароль установленный пользователем.
        * **confirm_password** - **__str__** - подтверждение пароля пользователя.

        ## Ответ:
            Статус 200

        ## Данные ответа
        -
        """
        serializer = serializers.UserProfileSignUpSerializer(data=request.data)
        if serializer.is_valid():

            if serializer.validated_data.get('password') != serializer.validated_data.get('confirm_password'):
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'password': _('Пароли не совпадают')})

            users_sing_up = UsersSingUp.objects.filter(token=serializer.validated_data.get('token'), is_active=True)
            if not users_sing_up.exists():
                return Response(status=status.HTTP_404_NOT_FOUND, data={'user': 'Инвайт не найден'})

            users_sing_up = users_sing_up.get()
            delta_time = timedelta(hours=settings.TIME_LIFE_TOKEN_REGISTRATION)

            if users_sing_up.token_time_stamp + delta_time < timezone.now():
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'user': 'Инвайт просрочен'})

            users_sing_up.user_activate(serializer.validated_data['password'])
            return Response(status=status.HTTP_200_OK, data={'email': users_sing_up.user.email})
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class JWTUserPayloadView(APIView):
    """
    get: Получить информацию о самом себе
    ##Данные ответа:
        {
          "id": 1,
          "email": "admin@admin.com",
          "groups": [],
          "avatar": null,
          "isSuperuser": true,
          "isStaff": true,
          "dateJoined": "2019-05-26T19:05:26+03:00",
          "lastLogin": "2019-06-17T22:23:57.632077+03:00",
          "phoneNumber": "",
          "firstName": "Тор",
          "lastName": "Израгнарока"
        }
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):

        user = request.user
        serializer = serializers.JWTUserPayloadSerializer(instance=user, context=request)
        return Response(serializer.data)

