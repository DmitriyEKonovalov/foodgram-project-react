from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)
from users.serializers import BaseUserSerializer
from .base_serializers import (
    BaseRecipeSerializer,
    BaseTagSerializer,
    IngredientsInRecipeSerializer
)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = serializers.ListField(child=serializers.IntegerField())
    image = Base64ImageField()
    author = BaseUserSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time', 'is_favorite', 'is_in_shopping_cart')

    def _save_with_nested_fields(self, recipe, tags, ingredients):
        tag_list_id = tags
        recipe.tags.set(tag_list_id, clear=True)
        objs = [RecipeIngredient(
            ingredient_id=i['id'], amount=i['amount']
        ) for i in ingredients]
        recipe.ingredients.set(objs, bulk=False, clear=True)
        return recipe

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        is_favorite = obj.in_favor.filter(user=user).exists()
        return is_favorite

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        is_in_shopping_cart = obj.in_cart.filter(user=user).exists()
        return is_in_shopping_cart

    def validate(self, attrs):
        tags_id = attrs.get('tags')
        if len(tags_id) != len(set(tags_id)):
            raise serializers.ValidationError('Найдены дубли тэгов!')
        cnt = Tag.objects.filter(id__in=tags_id).count()
        if cnt != len(tags_id):
            raise serializers.ValidationError('Несуществующий тэг!')

        ingredients = attrs.get('ingredients')
        ingrs_id = [item['id'] for item in ingredients]
        if len(ingrs_id) != len(set(ingrs_id)):
            raise serializers.ValidationError('Найдены дубли ингредиентов!!')
        cnt = Ingredient.objects.filter(id__in=ingrs_id).count()
        if cnt != len(ingrs_id):
            raise serializers.ValidationError('Несуществующий ингредиент!')
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data['author_id'] = self.context.get('request').user.id
        recipe = Recipe.objects.create(**validated_data)
        self._save_with_nested_fields(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data['author_id'] = self.context.get('request').user.id
        recipe = super().update(self.instance, validated_data)
        self._save_with_nested_fields(recipe, tags, ingredients)
        return recipe

    def to_representation(self, obj):
        self.fields['tags'] = BaseTagSerializer(many=True)
        return super().to_representation(obj)


class UsersChoiceRecipeSerializer(BaseRecipeSerializer):
    recipe_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',
                  'recipe_id', 'user_id')
        read_only_fields = ('name', 'image', 'cooking_time')

    def validate(self, attr):
        recipe_id = attr.get('recipe_id')
        user_id = attr.get('user_id')
        method = self.context.get('method')
        model = self.context.get('model')
        users_recipe = model.objects.filter(
            user=user_id, recipe=recipe_id
        ).exists()
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
        recipe = get_object_or_404(Recipe, id=users_recipe.recipe_id)
        self.instance = recipe
        return recipe
