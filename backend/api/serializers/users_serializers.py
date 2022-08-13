from rest_framework import serializers

from recipes.models import Subscribe
from users.models import User
from users.serializers import BaseUserSerializer

from .base_serializers import BaseRecipeSerializer


class UserWithRecipesSerializer(BaseUserSerializer):
    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        recipes = obj.recipes.count()
        return recipes


class SubscribeSerializer(UserWithRecipesSerializer):
    author_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    method = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count',
                  'author_id', 'user_id', 'method')

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        author_id = attrs.get('author_id')
        method = attrs.get('method')
        is_subscribed = Subscribe.objects.filter(
            author_id=author_id,
            user_id=user_id
        ).exists()
        if method == 'POST':
            if is_subscribed:
                raise serializers.ValidationError('Подписка существует!')
            if user_id == author_id:
                raise serializers.ValidationError('Нельзя подписаться на себя')
        if method == 'DELETE':
            if not is_subscribed:
                raise serializers.ValidationError('подписки не существует')
        return attrs

    def save(self, **kwargs):
        author_id = self.validated_data.get('author_id')
        user_id = self.validated_data.get('user_id')
        subscribe = Subscribe.objects.create(author_id=author_id, user_id=user_id)
        self.instance = subscribe.author
        return self.instance