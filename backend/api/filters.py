from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters.rest_framework import AllValuesMultipleFilter, ModelChoiceFilter, ChoiceFilter

from recipes.models import Recipe, Ingredient
from users.models import User


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(
        field_name='tags__id')
    author = ModelChoiceFilter(
        queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(FilterSet):

    class Meta:
        model = Ingredient
        fields = ['name']
