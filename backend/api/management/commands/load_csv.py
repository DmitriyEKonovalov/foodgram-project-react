import csv
from pathlib import Path
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag, Recipe
from users.models import User

TABLES = [
    (Ingredient, 'ingredients.csv'),
    (Tag, 'tags.csv'),
    (User, 'users.csv'),
    (Recipe, 'recipes.csv'),

]


class Command(BaseCommand):
    help = 'Load data from csv files'

    def handle(self, *args, **kwargs):
        for model, filename in TABLES:
            file_path = Path(settings.BASE_DIR).parent.joinpath('data').joinpath(filename)
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(model(**data) for data in reader)

        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
