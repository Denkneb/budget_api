import string
import uuid
from datetime import datetime, timedelta
from random import randint, sample, choice, choices

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.test import APITestCase

from budget.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from common.models import EmailTemplate, Configuration, ConfigurationFireBase, PushTemplate
from core.models import Uik, Mission
from core.models.mission import PRIORITY_TYPE_CHOICES, EXECUTION_TYPE_CHOICES, MISSION_TYPE_CHOICES
from user.models import User, UsersSingUp, PasswordResetData
from user.views import BudgetViewSet, UserSignUpView, PasswordResetRequestView, SetNewPasswordView, JWTUserPayloadView


class UserTestCase(APITestCase):

    PASSWORD = 'TestPassword123'

    @classmethod
    def setUpTestData(cls):

        cls.superuser = User.objects.create_superuser(
            email='superuser@agit.com',
            password=cls.PASSWORD,
            first_name='Chuck',
            last_name='Norris',
        )

        Configuration.init_settings()
        EmailTemplate.reset_defaults()

        ConfigurationFireBase.init_settings()
        PushTemplate.reset_defaults()

        cls.user = User.objects.create_user(
            email='user@budget.com',
            password=cls.PASSWORD,
            first_name='Candidate',
            last_name='Beer',
        )

    def setUp(self):
        self.factory = APIRequestFactory()
        self.headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64)',
            'HTTP_X_FORWARDED_FOR': '127.0.0.1',
        }


class TestAuthViews(UserTestCase):

    def _obtain_superuser_token(self):
        """Returns token obtained from test server"""

        url = reverse('obtain-token')
        data = {'email': self.superuser.email, 'password': self.PASSWORD}
        request = self.factory.post(url, data=data, **self.headers, format='json')
        response = obtain_jwt_token(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access'], response.data['refresh']

    def test_auth_views(self):
        """Test auth methods (obtain, refresh, verify token)"""

        access, refresh = self._obtain_superuser_token()

        url = reverse('refresh-token')
        data = {'refresh': refresh}
        request = self.factory.post(url, data=data, **self.headers, format='json')
        response = refresh_jwt_token(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('verify-token')
        data = {'token': response.data['access']}
        request = self.factory.post(url, data=data, **self.headers, format='json')
        response = verify_jwt_token(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jwt_token_auth(self):
        """Test token in http header is working"""

        access, refresh = self._obtain_superuser_token()
        self.headers.update({'HTTP_AUTHORIZATION': f'Bearer {access}'})

        # some auth required view
        url = reverse('coordinator-list')
        view = BudgetViewSet.as_view({'get': 'list'})
        request = self.factory.get(url, **self.headers, format='json')
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], User.objects.filter(groups__name__in=['budget']).count())

    def test_user_sign_up(self):
        """Метод для проверки активации юзера"""

        users_sign_up = UsersSingUp.objects.create(
            user=self.user,
        )
        url = reverse('sign-up')
        data = {
            'token': users_sign_up.token,
            'password': 'skdjfhkjhsf',
            'confirm_password': 'skdjfhkjhsf',
        }
        view = UserSignUpView.as_view()
        request = self.factory.post(url, data=data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_active, True)

    def test_user_sign_up_time_expired(self):
        """Метод для проверки активации юзера время истекло"""

        users_sign_up = UsersSingUp.objects.create(
            user=self.user,
            token_time_stamp=timezone.now() - timedelta(hours=24)
        )
        url = reverse('sign-up')
        data = {
            'token': users_sign_up.token,
            'password': 'skdjfhkjhsf',
            'confirm_password': 'skdjfhkjhsf',
        }
        view = UserSignUpView.as_view()
        request = self.factory.post(url, data=data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_reset_request_view(self):
        """Метод для проверки инициализации сброса пароля юзера"""

        url = reverse('reset-pass')

        data = {
            'email': self.user.email,
        }

        view = PasswordResetRequestView.as_view()
        request = self.factory.post(url, data=data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PasswordResetData.objects.filter(user=self.user).exists(), True)

    def test_user_set_new_password_view(self):
        """Метод для проверки установки нового пароля юзера"""

        code = ''.join(choices(string.digits, k=8))
        hash_str = uuid.uuid4()
        hash = PasswordResetData.objects.create(
            user=self.user,
            hash_str=hash_str,
            code=code
        )

        url = reverse('set-password')

        data = {
            'hash': hash.hash_str,
            'password': 'qwerty123',
            'confirm_password': 'qwerty123',
        }

        view = SetNewPasswordView.as_view()
        request = self.factory.post(url, data=data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.check_password('qwerty123'), True)

    def test_user_set_new_password_view_not_active(self):
        """Метод для проверки установки нового пароля юзера is_active = False"""

        code = ''.join(choices(string.digits, k=8))
        hash_str = uuid.uuid4()
        hash = PasswordResetData.objects.create(
            user=self.user,
            hash_str=hash_str,
            code=code,
            is_active=False,
        )

        url = reverse('set-password')

        data = {
            'hash': hash.hash_str,
            'password': 'qwerty123',
            'confirm_password': 'qwerty123',
        }

        view = SetNewPasswordView.as_view()
        request = self.factory.post(url, data=data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_set_new_password_view_restricted(self):
        """Метод для проверки установки нового пароля юзера, пароли не совпадают"""

        code = ''.join(choices(string.digits, k=8))
        hash_str = uuid.uuid4()
        hash = PasswordResetData.objects.create(
            user=self.user,
            hash_str=hash_str,
            code=code
        )

        url = reverse('set-password')

        data = {
            'hash': hash.hash_str,
            'password': 'qwerty123',
            'confirm_password': 'qwerty',
        }

        view = SetNewPasswordView.as_view()
        request = self.factory.post(url, data=data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_self_info(self):

        url = reverse('get-self-info')

        view = JWTUserPayloadView.as_view()
        request = self.factory.get(url, format='json')
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
