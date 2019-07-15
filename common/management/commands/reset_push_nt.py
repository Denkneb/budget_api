from django.core.management.base import BaseCommand

from common.models import PushTemplate


class Command(BaseCommand):

    def handle(self, *args, **options):
        PushTemplate.reset_defaults()
