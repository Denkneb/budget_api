import logging
import random
import string
import uuid
from datetime import timedelta
from typing import Union

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models.functions import Concat
from django.template import Context
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from common.models import Configuration, EmailTemplate, PushTemplate, ConfigurationFireBase
from user.errors import SingUpExpiredError
from user.tasks import send_message as celery_send_mail
from user.tasks import send_push as celery_send_push

log = logging.getLogger('app')


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(full_name=Concat('first_name', models.Value(' '), 'last_name'))
        return qs


class AbstractUser(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)

    email = models.EmailField(
        _('email'),
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
        help_text=_(
            _('This field will be used as username.')
        ),
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


class PasswordResetData(models.Model):

    user = models.OneToOneField('user.User', on_delete=models.CASCADE, null=False)
    created = models.DateTimeField(auto_now_add=True)
    hash_str = models.CharField(max_length=255, blank=False)
    code = models.CharField(max_length=8, blank=False)
    is_active = models.BooleanField(_('Активный'), default=True)

    def complete(self, password: str, lang: str = 'en'):
        self.is_active = False
        self.save()
        user = self.user
        user.set_password(password)
        user.save()
        tmpl = user._get_template('password_reset_complete', lang)
        if tmpl:
            context = Context({'user': user})
            mess_struct = tmpl.format(context)
            user.send_email(*mess_struct)
        self.delete()
        return user


class User(AbstractUser):

    description = models.TextField(_('description'), blank=True)
    phone_number = PhoneNumberField(blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.email

    def send_email(self, subj, text, html):
        conf = Configuration.get_settings()
        if conf:
            celery_send_mail.delay(conf.get_smtp_conf(), [self.email], subj, html)

    @staticmethod
    def _get_template(event: str, lang: str = 'en') -> Union[EmailTemplate, None]:
        try:
            return EmailTemplate.objects.get(event=event, lang=lang)
        except EmailTemplate.DoesNotExist:
            return None

    def _clear_reset_data(self) -> None:
        try:
            data = self.passwordresetdata
            data.delete()
        except ObjectDoesNotExist:
            return

    def init_pass_reset_process(self, lang: str = 'en') -> None:

        self._clear_reset_data()

        code = ''.join(random.choices(string.digits, k=8))
        hash_str = uuid.uuid4()
        proc = PasswordResetData.objects.create(
            user=self,
            hash_str=hash_str,
            code=code
        )

        tmpl = self._get_template('password_reset', lang)
        if tmpl:
            context = Context({'data': proc, 'user': self})
            mess_struct = tmpl.format(context)
            self.send_email(*mess_struct)

    def get_password_reset_hash(self, code: str) -> Union[str, None]:
        try:
            data = self.passwordresetdata
            if data.code == code:
                return data.hash_str
        except ObjectDoesNotExist:
            return

    def init_invite(self, user, lang: str = 'ru') -> None:
        self.is_active = False
        self.save()
        users_sing_up = UsersSingUp.objects.filter(user=self)
        if users_sing_up.exists():
            users_sing_up.delete()
        proc = UsersSingUp.objects.create(
            user=self,
        )
        tmpl = self._get_template('invite', lang)
        if tmpl:
            context = Context({
                'url_sign_up': proc.token,
                'user': user.get_full_name(),
            })
            mess_struct = tmpl.format(context)
            self.send_email(*mess_struct)

    def send_push(self, title, text):
        conf = ConfigurationFireBase.get_settings()
        if conf:
            celery_send_push.delay(conf.get_firebase_conf(), self.firebasetoken.token, title, text)

    @staticmethod
    def get_template_push(event: str, lang: str = 'ru') -> Union[PushTemplate, None]:
        try:
            return PushTemplate.objects.get(event=event, lang=lang)
        except PushTemplate.DoesNotExist:
            return None

    def init_push(self, tmp, mission_id, date_time, lang: str = 'ru'):

        tmpl = self.get_template_push(tmp, lang)
        firebase_token = FirebaseToken.objects.filter(user=self)
        if tmpl and firebase_token.exists():
            context = Context({
                'url': mission_id,
                'datetime': date_time,
            })
            mess_struct = tmpl.format(context)
            self.send_push(*mess_struct)

    def get_full_name(self):
        return '{} {}'.format(self.last_name, self.first_name)


class UsersSingUp(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)
    token = models.UUIDField(_('Код активации'), default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(_('Активный'), default=True)
    token_time_stamp = models.DateTimeField(_('Дата создания'), default=timezone.now)

    class Meta:
        verbose_name = _('Инвайт')
        verbose_name_plural = _('Инвайты')

    def __str__(self):
        return self.user.email

    def user_activate(self, password: str) -> None:
        delta_time = timedelta(hours=settings.TIME_LIFE_TOKEN_REGISTRATION)

        if self.token_time_stamp + delta_time > timezone.now():
            user = self.user
            with transaction.atomic():
                user.set_password(password)
                user.is_active = True
                user.save()
                self.is_active = False
                self.save()
        else:
            raise SingUpExpiredError(_('Время действия токена автивации истекло'))


class FirebaseToken(models.Model):
    token = models.CharField(verbose_name=_('Токен'), max_length=2048)
    created = models.DateTimeField(verbose_name=_('Дата и время создания'), default=timezone.now)
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Данные токена firebase"
        verbose_name_plural = "Данные токена firebase"

    def __str__(self):
        return '%s) %s' % (self.id, self.user.email)


class Notification(models.Model):
    created = models.DateTimeField(verbose_name=_('Дата и время создания'), default=timezone.now)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    event = models.CharField(max_length=255, choices=settings.PUSH_NOTIFICATION_EVENT_CODES)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ('-created',)

    def __str__(self):
        return '%s) %s' % (self.id, self.user.email)
