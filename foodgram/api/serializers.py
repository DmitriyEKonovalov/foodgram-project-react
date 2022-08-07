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
from users.serializers import BaseUserSerializer
from recipes.serializers import (
    BaseRecipeSerializer,
    IngredientSerializer,
    TagSerializer,
)


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = BaseUserSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorite',
            'is_in_shopping_cart'
        )

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        is_favorite = obj.in_favor.filter(user=user).exists()
        return is_favorite

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        is_in_shopping_cart = obj.in_cart.filter(user=user).exists()
        return is_in_shopping_cart

    def to_internal_value(self, data):
        # tags = [{'id': tag_id} for tag_id in data['tags']]
        # data['tags'] = tags
        data['author'] = self.context['request'].user
        return data

    def validate(self, attrs):
        # проверить наличие всех тегов в базе

        # проверить наличие всех ингридиентов в базе

        #
        return attrs

    def create(self, validated_data):
        method = self.context['request'].method
        user = self.context['request'].user
        # recipe = Recipe.objects.get(id=validated_data.id)
        if method == "POST":
            tags = validated_data.pop('tags')
            ingredients = validated_data.pop('ingredients')
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags, clear=True)
            objs = [RecipeIngredients(ingredient_id=i['id'], amount=i['amount']) for i in ingredients]
            recipe.ingredients.set(objs, bulk=False, clear=True)

        return recipe



"""

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

"""

class UserWithRecipesSerializer(BaseUserSerializer):
    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

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

    def get_recipes_count(self, obj):
        recipes = obj.recipes.count()
        return recipes


class SubscribeSerializer(UserWithRecipesSerializer):
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

    def to_internal_value(self, data):
        # self.instance = self.context['author']
        return self.context['author']

    def validate(self, attrs):
        request = self.context['request']
        user = self.context['user']
        author = self.context['author']
        method = request.method
        subscribe = user.subscribed.filter(author=author).exists()

        if method == 'POST':
            if subscribe:
                raise serializers.ValidationError('Подписка существует!')
            if user == author:
                raise serializers.ValidationError('Нельзя подписаться на себя')
        if method == 'DELETE':
            if not subscribe:
                raise serializers.ValidationError('подписки не существует')

        return attrs

    def save(self, **kwargs):
        author_id = self.validated_data.id
        user_id = self.context['user'].id
        Subscribe.objects.create(author_id=author_id, user_id=user_id)
        return self.context['author']


"""
старые  сериалазеры для проверки гипотезы


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

