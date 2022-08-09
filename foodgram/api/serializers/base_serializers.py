from rest_framework import serializers
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    Subscribe,
    ShoppingCart,
    Tag
)


class BaseIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('name', 'color', 'slug')


class BaseTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'measurement_unit')


class BaseRecipeSerializer(serializers.ModelSerializer):
    # name = serializers.ModelField(model_field='name', read_only=True)
    # image = serializers.ModelField(model_field='image', read_only=True)
    # cooking_time = serializers.ModelField(model_field='cooking_time', read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount', )

