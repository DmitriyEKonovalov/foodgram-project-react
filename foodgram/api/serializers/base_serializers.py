from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    Tag
)
from rest_framework import serializers


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
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount', )
