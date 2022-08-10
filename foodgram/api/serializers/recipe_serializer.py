from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Recipe,
    RecipeIngredients,
)
from users.serializers import BaseUserSerializer
from .base_serializers import (
    BaseTagSerializer,
    BaseRecipeSerializer,
    IngredientsInRecipeSerializer,
)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = BaseTagSerializer(many=True)
    image = Base64ImageField()
    author = BaseUserSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time', 'is_favorite', 'is_in_shopping_cart')

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
        # проверить наличие всех ингредиентов в базе
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


class UsersChoiceRecipeSerializer(BaseRecipeSerializer):
    """Универсальный сериалайзер, для Favorite и ShoppingCart.
    Подходит для любой модели с полями user, recipe.
    Принимает id рецепта как поля сериалайзера (в data).
    Класc модели, id пользователя и метод запроса получает через context.

    """
    def to_internal_value(self, data):
        # TODO принимать данные здесь!
        return data

    def validate(self, attr):
        recipe_id = self.initial_data['id']
        user_id = self.context['user_id']
        method = self.context['method']
        model = self.context['model']
        users_recipe = model.objects.filter(user=user_id, recipe=recipe_id).exists()
        if method == 'POST':
            if users_recipe:
                raise serializers.ValidationError('Рецепт уже добавлен!')
        if method == 'DELETE':
            if not users_recipe:
                raise serializers.ValidationError('Рецепт отсутствует!')
        return {'recipe_id': recipe_id, 'user_id': user_id}

    def save(self, **kwargs):
        model = self.context['model']
        users_recipe = model.objects.create(**self.validated_data)
        recipe = self.Meta.model.objects.get(id=users_recipe.recipe_id)
        self.instance = recipe
        return recipe

