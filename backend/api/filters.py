from django_filters.rest_framework import FilterSet, CharFilter
from django_filters.rest_framework import (
    AllValuesMultipleFilter, ModelChoiceFilter)

from recipes.models import Recipe, Ingredient
from users.models import CustomUser


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = ModelChoiceFilter(
        queryset=CustomUser.objects.all())

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ['name']
