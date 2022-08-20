import csv
from pathlib import Path
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscribe, Tag)


TABLES = [
    (Ingredient, 'ingredients.csv'),
    (Tag, 'tags.csv'),
    (Recipe, 'recipes.csv'),
    (RecipeIngredient, 'recipe_ingredients.csv'),
    (Favorite, 'favorites.csv'),
    (ShoppingCart, 'shoppingcarts.csv'),
    (Subscribe, 'subscribes.csv'),
]


class Command(BaseCommand):
    help = 'Load data from csv files'

    def handle(self, *args, **kwargs):
        for model, filename in TABLES:
            file_path = Path(settings.BASE_DIR).parent.joinpath('data').joinpath(filename)
            self.stdout.write(self.style.MIGRATE_LABEL(f'start loading {filename}'))
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(model(**data) for data in reader)

        self.stdout.write(self.style.MIGRATE_LABEL(f'start loading recipe_tags.csv'))
        file_path = Path(settings.BASE_DIR).parent.joinpath('data').joinpath('recipe_tags.csv')
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                recipe = Recipe.objects.get(id=row['recipe_id'])
                recipe.tags.set(row['tag_id'], clear=False)

        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))

