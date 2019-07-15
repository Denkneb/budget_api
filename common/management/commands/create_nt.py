from django.core.management.base import BaseCommand
from common.models import EmailTemplate, Configuration


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not Configuration.objects.all():
            Configuration.init_settings()
            self.stdout.write('Configuration was init')
        if not EmailTemplate.objects.all():
            EmailTemplate.reset_defaults()
        else:
            self.stderr.write('Templates already exists')
