"""

from rest_framework import serializers
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField

from users.models import User
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    Subscribe,
    ShoppingCart,
    Tag
)
from recipes.serializers import (
    IngredientSerializer,
    IngredientsInRecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from users.serializers import BaseUserSerializer


class ShoppingCartSerializer(ShortRecipeSerializer):

    def validate(self, attrs):
        recipe_id = self.initial_data['id']
        user_id = self.context['user_id']
        method = self.context['method']
        in_cart = ShoppingCart.objects.filter(user=user_id, recipe=recipe_id).exists()

        if method == 'POST':
            if in_cart:
                raise serializers.ValidationError('Рецепт уже добавлен!')
        if method == 'DELETE':
            if not in_cart:
                raise serializers.ValidationError('Рецепт отсутствует!')

        return {'recipe_id': recipe_id, 'user_id': user_id}

    def save(self, **kwargs):
        recipe_in_cart = ShoppingCart.objects.create(**self.validated_data)
        recipe = Recipe.objects.get(id=recipe_in_cart.recipe_id)
        self.instance = recipe
        return recipe


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('user', 'receipt')

    def validate(self, attrs):
        recipe = self.instance
        user = self.context['user']
        method = self.context['request']
        in_cart = ShoppingCart.filter(user=user, recipe=recipe).exists()

        if method == 'POST':
            if in_cart:
                raise serializers.ValidationError('Рецепт уже добавлен!')
        if method == 'DELETE':
            if not in_cart:
                raise serializers.ValidationError('Рецепт отсутствует!')
        return attrs

    def save(self, **kwargs):
        recipe_id = self.validated_data.id
        user_id = self.context['user'].id
        selected_recipe = ShoppingCart.objects.create(recipe_id=recipe_id, user_id=user_id)
        return self.context['recipe']



старые  сериалазеры для проверки гипотезы

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = ingredientsInRecipeSerializer(
        source='ingredients',
        many=True
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = BaseUserSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        is_favorite = obj.in_favor.filter(user=user).exists()
        return is_favorite

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        is_in_shopping_cart = obj.in_cart.filter(user=user).exists()
        return is_in_shopping_cart


class UserRecipesSerializer(BaseUserSerializer):
    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]
        read_only_fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_recipes_count(self, obj):
        recipes = obj.recipes.count()
        return recipes

class OLDSubscribeSerializer(UserRecipesSerializer):

    def validate(self, attr):
        request = self.context.get('request')
        user = self.initial_data['user']
        author = self.initial_data['author']
        subscribe = user.subscribed.filter(author=author)
        if request.user.is_anonymous:
            raise serializers.ValidationError(
                'Учетные данные не были предоставлены.'
            )

        if request.method == 'POST':
            if subscribe.exists():
                raise serializers.ValidationError('Подписка уже существует')

        if request.method == 'DELETE':
            if not subscribe.exists():
                raise serializers.ValidationError('Подписка не существует')

        return attr

    def save(self, **kwargs):
        user = self.initial_data['user']
        author = self.initial_data['author']
        instance = Subscribe.objects.create(user=user, author=author)
        return author.id





"""

