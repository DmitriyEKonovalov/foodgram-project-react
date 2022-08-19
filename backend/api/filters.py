from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from django_filters.rest_framework import (
    AllValuesMultipleFilter, MultipleChoiceFilter,
    ModelMultipleChoiceFilter, ModelChoiceFilter, ChoiceFilter
)

from recipes.models import Recipe, Ingredient
from users.models import User


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(
        field_name='tags__name',
        # to_field_name='slug',
    )
    author = ModelChoiceFilter(
        queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ['name']
