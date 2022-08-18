from os import getenv

from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Create initial admin user'

    def handle(self, *args, **options):
        User.objects.create_user(
            username=getenv('DJANGO_SUPERUSER_USERNAME'),
            email=getenv('DJANGO_SUPERUSER_EMAIL'),
            password=getenv('DJANGO_SUPERUSER_PASSWORD'),
            is_staff=True,
            is_active=True,
            is_superuser=True
        )
