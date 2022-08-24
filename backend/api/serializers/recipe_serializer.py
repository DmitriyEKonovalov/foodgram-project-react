from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
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
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time',
                  'is_favorited',
                  'is_in_shopping_cart'
                  )

    def _save_with_nested_fields(self, recipe, tags, ingredients):
        tag_list_id = tags
        recipe.tags.set(tag_list_id, clear=True)
        objs = [RecipeIngredient(
            ingredient_id=i['id'], amount=i['amount']
        ) for i in ingredients]
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.ingredients.set(objs, bulk=False, clear=False)
        return recipe

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.in_favor.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.in_cart.filter(user=user).exists()
        return False

    def validate(self, attrs):
        tags_id = attrs.get('tags')
        if len(tags_id) != len(set(tags_id)):
            raise serializers.ValidationError('Найдены дубли тэгов!')
        cnt = Tag.objects.filter(id__in=tags_id).count()
        if cnt != len(tags_id):
            raise serializers.ValidationError('Несуществующий тэг!')

        ingredients = attrs.get('ingredients')
        ingrs_id = []
        for item in ingredients:
            ingrs_id.append(item['id'])
            if item['amount'] <= 0:
                raise serializers.ValidationError('кол-во должно быть >0')

        cooking_time = attrs.get('cooking_time')
        if cooking_time and cooking_time <= 0:
            raise serializers.ValidationError('Время готовки должно быть >0!')

        if len(ingrs_id) != len(set(ingrs_id)):
            raise serializers.ValidationError('Найдены дубли ингредиентов!')
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
        self._save_with_nested_fields(instance, tags, ingredients)
        return recipe

    def to_representation(self, obj):
        self.fields['tags'] = BaseTagSerializer(many=True)
        self.context['author'] = obj.author
        return super().to_representation(obj)


class UsersChoiceRecipeReadSerializer(BaseRecipeSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context['user']
        if user.is_authenticated:
            return obj.in_favor.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['user']
        if user.is_authenticated:
            return obj.in_cart.filter(user=user).exists()
        return False


class UsersChoiceRecipeWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def validate(self, attr):
        model = self.context.get('model')
        if not model:
            raise serializers.ValidationError()
        self.Meta.model = self.context.get('model')

        user = attr.get('user')
        recipe = attr.get('recipe')
        if not (user and recipe):
            raise serializers.ValidationError('отсутствуют данные')

        users_recipe = self.Meta.model.objects.filter(user=user, recipe=recipe)
        method = self.context.get('method')
        if method == 'POST':
            if users_recipe:
                raise serializers.ValidationError('Рецепт уже добавлен!')
        if method == 'DELETE':
            if not users_recipe:
                raise serializers.ValidationError('Рецепт отсутствует!')

        return {'recipe': recipe, 'user': user}

    def save(self, **kwargs):
        user = self.validated_data.get('user')
        recipe = self.validated_data.get('recipe')
        users_recipe = self.Meta.model.objects.create(**self.validated_data)
        self.instance = recipe
        ret = UsersChoiceRecipeReadSerializer(instance=recipe, context={'user': user}).data
        return ret

