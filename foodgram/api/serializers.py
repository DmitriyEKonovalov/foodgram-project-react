from rest_framework import serializers
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.models import User
from recipes.models import (
    Ingridient,
    Recipe,
    RecipeIngridients,
    Subscribe,
    ShoppingCart,
    Tag
)
from users.serializers import BaseUserSerializer
from recipes.serializers import (
    BaseRecipeSerializer,
    IngridientSerializer,
    TagSerializer,
)


class RecipeIngridientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingridient.id')
    name = serializers.ReadOnlyField(source='ingridient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeSerializer(serializers.ModelSerializer):
    author = BaseUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngridientsSerializer(
        source='ingridients',
        many=True, read_only=True,)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorite(self, obj):
        return None

    def get_is_in_shopping_cart(self, obj):
        return None


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
дублирующие сериалазеры для проверки гипотезы



"""


class NewBaseUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_subscribed']

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            not user.is_anonymous
            and user.subscribed.filter(author=obj).exists()
        )


class NewUserWithRecipesSerializer(NewBaseUserSerializer):
    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_subscribed', 'recipes', 'recipes_count']

    def get_recipes_count(self, obj):
        recipes = obj.recipes.count()
        return recipes


class SubscribeSerializer(NewUserWithRecipesSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_subscribed', 'recipes', 'recipes_count']

    def to_internal_value(self, data):
        self.instance = self.context['author']
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

