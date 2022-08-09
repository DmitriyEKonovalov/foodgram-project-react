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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['name', 'color', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['name', 'measurement_unit']


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
        data['author'] = self.context['request'].user
        return data

    def validate(self, attrs):
        # проверить наличие всех тегов в базе

        # проверить наличие всех ингридиентов в базе

        #
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags, clear=False)
        objs = [RecipeIngredients(ingredient_id=i['id'], amount=i['amount']) for i in ingredients]
        recipe.ingredients.set(objs, bulk=False, clear=False)

        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        Recipe.objects.filter(id=recipe.id).update(**validated_data)
        recipe.tags.set(tags, clear=True)
        objs = [RecipeIngredients(ingredient_id=i['id'], amount=i['amount']) for i in ingredients]
        recipe.ingredients.set(objs, bulk=False, clear=True)
        return recipe


class ShortRecipeSerializer(serializers.ModelSerializer):
    # name = serializers.ModelField(model_field='name', read_only=True)
    # image = serializers.ModelField(model_field='image', read_only=True)
    # cooking_time = serializers.ModelField(model_field='cooking_time', read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class UserWithRecipesSerializer(BaseUserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
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


class ShoppingCartSerializer(ShortRecipeSerializer):
    # TODO !!! работает, сделать удаление и повторить код для Favorite
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


"""

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

