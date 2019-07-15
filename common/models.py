import os

from django.conf import settings
from django.db import models
from django.template import Template
from django.utils.translation import ugettext_lazy as _

from budget.mixins import SingleInstanceMixin


class Configuration(SingleInstanceMixin, models.Model):
    mailgun_api_key = models.CharField(max_length=255, blank=True)
    mailgun_domain = models.CharField(max_length=255, blank=True)
    mailgun_api_url = models.CharField(max_length=255, blank=True)
    email_noreply = models.CharField(max_length=255, blank=True)
    email_job = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _('Настройки почтового сервиса')
        verbose_name_plural = _('Настройки почтового сервиса')

    def __str__(self):
        return self.mailgun_domain

    @staticmethod
    def get_settings():
        conf = Configuration.objects.all()
        return conf[0] if conf else None

    @staticmethod
    def init_settings():
        conf = Configuration.objects.all()
        if conf:
            conf.delete()

        Configuration.objects.create(
            mailgun_api_key=settings.MAILGUN_API_KEY,
            mailgun_domain=settings.MAILGUN_DOMAIN,
            mailgun_api_url=settings.MAILGUN_API_URL,
            email_noreply=settings.EMAIL_NOREPLY,
            email_job=settings.EMAIL_JOB,
        )

    def get_smtp_conf(self):
        return dict(
            mailgun_api_key=self.mailgun_api_key,
            mailgun_domain=self.mailgun_domain,
            mailgun_api_url=self.mailgun_api_url.format(self.mailgun_domain),
            email_noreply=self.email_noreply,
            email_job=self.email_job,
        )


class EmailTemplate(models.Model):

    event = models.CharField(max_length=255, choices=settings.NOTIFICATION_EVENT_CODES, blank=False)
    subj = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=False)
    html = models.TextField(blank=False)

    lang = models.CharField(choices=settings.LANGUAGES, max_length=2, default=settings.LANGUAGE_CODE)

    class Meta:
        verbose_name = _('Шаблоны писем')
        verbose_name_plural = _('Шаблоны писем')
        unique_together = ('event', 'lang')

    def __str__(self):
        return '{}-{}'.format(self.subj, self.lang)

    @staticmethod
    def reset_defaults():
        EmailTemplate.objects.all().delete()
        for (event, descr) in settings.NOTIFICATION_EVENT_CODES:
            for lang in [lang[0] for lang in settings.LANGUAGES]:
                dpath = os.path.join(
                    settings.EMAIL_TEMPLATES_DIR,
                    lang,
                    event
                )
                with open(os.path.join(dpath, 'subject.txt')) as file:
                    subj = file.read(255)
                with open(os.path.join(dpath, 'text.txt')) as file:
                    text = file.read()
                with open(os.path.join(dpath, 'html.html')) as file:
                    html = file.read()
                EmailTemplate.objects.create(
                    event=event,
                    subj=subj,
                    text=text,
                    html=html,
                    lang=lang,
                )

    def _get_default_dir(self):
        return os.path.join(
            settings.EMAIL_TEMPLATES_DIR,
            str(self.lang),
            str(self.event)
        )

    def reset_default(self):

        dpath = self._get_default_dir()
        with open(os.path.join(dpath, 'subject.txt')) as file:
            subj = file.read(255)
        with open(os.path.join(dpath, 'text.txt')) as file:
            text = file.read()
        with open(os.path.join(dpath, 'html.html')) as file:
            html = file.read()

        self.subj = subj
        self.text = text
        self.html = html
        self.save()

    def format(self, context):

        emparts = []
        for attr in ('subj', 'text', 'html'):
            template = Template(getattr(self, attr))
            emparts.append(template.render(context))

        return emparts


class ConfigurationFireBase(SingleInstanceMixin, models.Model):
    firebase_key_server = models.CharField(max_length=255, blank=True)
    firebase_url_request = models.URLField(blank=True)

    class Meta:
        verbose_name = _('Настройки FireBase сервиса')
        verbose_name_plural = _('Настройки FireBase сервиса')

    @staticmethod
    def get_settings():
        return ConfigurationFireBase.objects.first()

    @staticmethod
    def init_settings():
        conf = ConfigurationFireBase.objects.all()
        if conf:
            conf.delete()

        ConfigurationFireBase.objects.create(
            firebase_key_server=settings.FIREBASE_KEY_SERVER,
            firebase_url_request=settings.FIREBASE_URL_REQUEST,
        )

    def get_firebase_conf(self):
        return dict(
            firebase_key_server=self.firebase_key_server,
            firebase_url_request=self.firebase_url_request,
        )


class PushTemplate(models.Model):

    event = models.CharField(max_length=255, choices=settings.PUSH_NOTIFICATION_EVENT_CODES, blank=False)
    title = models.CharField(max_length=255, blank=False)
    text = models.TextField(blank=False)
    lang = models.CharField(choices=settings.LANGUAGES, max_length=2, default=settings.LANGUAGE_CODE)

    class Meta:
        verbose_name = _('Шаблоны push уведомлений')
        verbose_name_plural = _('Шаблоны push уведомлений')
        unique_together = ('event', 'lang')

    def __str__(self):
        return '{}-{}'.format(self.title, self.lang)

    @staticmethod
    def reset_defaults():
        PushTemplate.objects.all().delete()
        for (event, descr) in settings.PUSH_NOTIFICATION_EVENT_CODES:
            for lang in [lang[0] for lang in settings.LANGUAGES]:
                dpath = os.path.join(
                    settings.PUSH_TEMPLATES_DIR,
                    lang,
                    event
                )
                with open(os.path.join(dpath, 'title.txt')) as file:
                    title = file.read(255)
                with open(os.path.join(dpath, 'text.txt')) as file:
                    text = file.read()
                PushTemplate.objects.create(
                    event=event,
                    title=title,
                    text=text,
                    lang=lang,
                )

    def _get_default_dir(self):
        return os.path.join(
            settings.PUSH_TEMPLATES_DIR,
            str(self.lang),
            str(self.event)
        )

    def reset_default(self):

        dpath = self._get_default_dir()
        with open(os.path.join(dpath, 'title.txt')) as file:
            title = file.read(255)
        with open(os.path.join(dpath, 'text.txt')) as file:
            text = file.read()

        self.title = title
        self.text = text
        self.save()

    def format(self, context):

        emparts = []
        for attr in ('title', 'text'):
            template = Template(getattr(self, attr))
            emparts.append(template.render(context))

        return emparts
