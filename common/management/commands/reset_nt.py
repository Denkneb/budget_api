from django.core.management.base import BaseCommand
from common.models import EmailTemplate


class Command(BaseCommand):

    def handle(self, *args, **options):
        EmailTemplate.reset_defaults()
