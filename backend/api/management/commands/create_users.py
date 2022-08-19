from os import getenv

from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Create initial users'

    def handle(self, *args, **options):
        User.objects.create_user({
            'username': getenv('DJANGO_SUPERUSER_USERNAME'),
            'email': getenv('DJANGO_SUPERUSER_EMAIL'),
            'password': getenv('DJANGO_SUPERUSER_PASSWORD'),
            'is_staff': True,
            'is_active': True,
            'is_superuser': True
        })
        User.objects.create_user({
            'id': 2,
            'username': 'user1',
            'password': '1adminuser',
            'firstname': 'Шеф по супам',
            'is_staff': False,
            'is_active': True,
            'is_superuser': False
        })
        User.objects.create_user({
            'id': 3,
            'username': 'user2',
            'password': '2adminuser',
            'firstname': 'Шеф по выпечке',
            'is_staff': False,
            'is_active': True,
            'is_superuser': False
        })
