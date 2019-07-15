from django.core.management.base import BaseCommand

from common.models import ConfigurationFireBase, PushTemplate


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not ConfigurationFireBase.objects.all():
            ConfigurationFireBase.init_settings()
            self.stdout.write('Configuration was init')
        if not PushTemplate.objects.all():
            PushTemplate.reset_defaults()
        else:
            self.stderr.write('Templates already exists')
